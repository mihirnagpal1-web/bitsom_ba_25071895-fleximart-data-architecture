"""
ETL Pipeline for FlexiMart
-------------------------
Extracts raw CSV data, fixes data quality issues,
generates surrogate keys, and loads clean data
into PostgreSQL.

Author: Assignment Submission
"""

import pandas as pd
import numpy as np
import re
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# =============================
# CONFIGURATION
# =============================

DB_CONFIG = {
    "postgresql": "postgresql://postgres:1234@localhost/fleximart"
}

CUSTOMERS_FILE = "customers_raw.csv"
PRODUCTS_FILE = "products_raw.csv"
SALES_FILE = "sales_raw.csv"

REPORT_FILE = "data_quality_report.txt"

# =============================
# HELPER FUNCTIONS
# =============================

def standardize_phone(phone):
    if pd.isna(phone):
        return None
    digits = re.sub(r"\D", "", str(phone))
    return f"+91-{digits}" if len(digits) == 10 else None


def standardize_category(category):
    if pd.isna(category):
        return "Unknown"
    return category.strip().capitalize()


def standardize_date(date_val):
    try:
        return pd.to_datetime(date_val, errors="coerce").date()
    except Exception:
        return None


# =============================
# ETL PROCESS
# =============================

def main():
    report = []

    try:
        # =============================
        # EXTRACT
        # =============================
        print("[DEBUG] Reading CSV files...")
        customers = pd.read_csv(CUSTOMERS_FILE)
        products = pd.read_csv(PRODUCTS_FILE)
        sales = pd.read_csv(SALES_FILE)

        report.extend([
            f"Customers records read: {len(customers)}",
            f"Products records read: {len(products)}",
            f"Sales records read: {len(sales)}"
        ])

        # =============================
        # TRANSFORM — CUSTOMERS
        # =============================
        print("[DEBUG] Cleaning customers...")
        cust_dupes = customers.duplicated().sum()
        customers.drop_duplicates(inplace=True)

        customers["email"].replace("", np.nan, inplace=True)
        customers.dropna(subset=["email"], inplace=True)

        customers["phone"] = customers["phone"].apply(standardize_phone)
        customers["registration_date"] = customers["registration_date"].apply(standardize_date)

        customers["old_customer_id"] = customers["customer_id"]
        customers.drop(columns=["customer_id"], inplace=True)

        report.append(f"Customer duplicates removed: {cust_dupes}")

        # =============================
        # TRANSFORM — PRODUCTS
        # =============================
        print("[DEBUG] Cleaning products...")
        prod_dupes = products.duplicated().sum()
        products.drop_duplicates(inplace=True)

        products["price"].fillna(products["price"].median(), inplace=True)
        products["stock_quantity"].fillna(0, inplace=True)
        products["category"] = products["category"].apply(standardize_category)

        products["old_product_id"] = products["product_id"]
        products.drop(columns=["product_id"], inplace=True)

        report.append(f"Product duplicates removed: {prod_dupes}")

        # =============================
        # TRANSFORM — SALES
        # =============================
        print("[DEBUG] Cleaning sales...")
        sales_dupes = sales.duplicated().sum()
        sales.drop_duplicates(inplace=True)

        sales["transaction_date"] = sales["transaction_date"].apply(standardize_date)
        sales.dropna(subset=["customer_id", "product_id", "transaction_date"], inplace=True)

        sales["subtotal"] = sales["quantity"] * sales["unit_price"]

        report.append(f"Sales duplicates removed: {sales_dupes}")

        # =============================
        # LOAD — DATABASE
        # =============================
        engine = create_engine(DB_CONFIG["postgresql"])

        print("[DEBUG] Testing database connection...")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        # =============================
        # LOAD CUSTOMERS
        # =============================
        print("[DEBUG] Loading customers...")
        customers_clean = customers.drop(columns=["old_customer_id"])
        customers_clean.to_sql("customers", engine, if_exists="append", index=False)

        customer_map = pd.read_sql(
            "SELECT customer_id, email FROM customers",
            engine
        )

        customers = customers.merge(customer_map, on="email", how="left")

        # =============================
        # LOAD PRODUCTS
        # =============================
        print("[DEBUG] Loading products...")
        products_clean = products.drop(columns=["old_product_id"])
        products_clean.to_sql("products", engine, if_exists="append", index=False)

        product_map = pd.read_sql(
            "SELECT product_id, product_name FROM products",
            engine
        )

        products = products.merge(product_map, on="product_name", how="left")

        # =============================
        # MAP SURROGATE KEYS
        # =============================
        sales = sales.merge(
            customers[["old_customer_id", "customer_id"]],
            left_on="customer_id",
            right_on="old_customer_id",
            how="left"
        )

        sales = sales.merge(
            products[["old_product_id", "product_id"]],
            left_on="product_id",
            right_on="old_product_id",
            how="left"
        )

        # =============================
        # LOAD ORDERS
        # =============================
        print("[DEBUG] Loading orders...")
        orders = sales.groupby(
            ["customer_id_y", "transaction_date"],
            as_index=False
        )["subtotal"].sum()

        orders.rename(columns={
            "customer_id_y": "customer_id",
            "transaction_date": "order_date",
            "subtotal": "total_amount"
        }, inplace=True)

        orders["status"] = "Pending"
        orders.to_sql("orders", engine, if_exists="append", index=False)

        order_map = pd.read_sql(
            "SELECT order_id, customer_id, order_date FROM orders",
            engine
        )

        # =============================
        # LOAD ORDER ITEMS (CRITICAL FIX)
        # =============================
        print("[DEBUG] Loading order items...")
        sales = sales.merge(
            order_map,
            left_on=["customer_id_y", "transaction_date"],
            right_on=["customer_id", "order_date"],
            how="left"
        )

        order_items = sales[[
            "order_id",
            "product_id_y",
            "quantity",
            "unit_price",
            "subtotal"
        ]].copy()

        order_items.rename(columns={"product_id_y": "product_id"}, inplace=True)

        # 🔥 REQUIRED FK SAFETY
        order_items.dropna(subset=["order_id"], inplace=True)
        order_items["order_id"] = order_items["order_id"].astype(int)

        order_items.to_sql("order_items", engine, if_exists="append", index=False)

        # =============================
        # REPORT
        # =============================
        report.extend([
            f"Customers loaded: {len(customers_clean)}",
            f"Products loaded: {len(products_clean)}",
            f"Orders loaded: {len(orders)}",
            f"Order items loaded: {len(order_items)}",
            "ETL Pipeline completed successfully"
        ])

        print("[DEBUG] ✓ ETL Pipeline completed successfully")

    except SQLAlchemyError as e:
        report.append(f"Database error: {e}")
        print("[ERROR]", e)

    except Exception as e:
        report.append(f"ETL error: {e}")
        print("[ERROR]", e)

    finally:
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            for line in report:
                f.write(line + "\n")


if __name__ == "__main__":
    main()
