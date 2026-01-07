# FlexiMart Database Schema Documentation

## 1. Entity-Relationship Description

### ENTITY: customers
Purpose: Stores customer information.

Attributes:
- customer_id: Unique identifier for each customer (Primary Key)
- first_name: Customer's first name
- last_name: Customer's last name
- email: Customer’s email address (used to link with orders)
- phone: Customer’s contact number (standardized format +91-XXXXXXXXXX)
- city: City of residence
- registration_date: Date when the customer registered

Relationships:
- One customer can place MANY orders (1:M with orders table)

---

### ENTITY: products
Purpose: Stores product information.

Attributes:
- product_id: Unique identifier for each product (Primary Key)
- product_name: Name of the product
- category: Product category (standardized capitalization)
- price: Price of the product
- stock_quantity: Quantity available in stock

Relationships:
- One product can appear in MANY order items (1:M with order_items table)

---

### ENTITY: orders
Purpose: Stores order information for customers.

Attributes:
- order_id: Unique identifier for each order (Primary Key)
- customer_id: ID of the customer who placed the order (Foreign Key → customers.customer_id)
- order_date: Date of the order
- total_amount: Total amount for the order
- status: Order status (Pending, Completed, Cancelled)

Relationships:
- One order can contain MANY order items (1:M with order_items table)

---

### ENTITY: order_items
Purpose: Stores details of products within each order.

Attributes:
- order_item_id: Unique identifier for each order item (Primary Key)
- order_id: ID of the order (Foreign Key → orders.order_id)
- product_id: ID of the product (Foreign Key → products.product_id)
- quantity: Quantity of product in the order
- unit_price: Price per unit of the product
- subtotal: Calculated subtotal = quantity * unit_price

Relationships:
- Many order items belong to one order (M:1 with orders)
- Many order items reference one product (M:1 with products)

---

## 2. Normalization Explanation (3NF)

The FlexiMart database is designed to follow Third Normal Form (3NF):

Functional Dependencies:
1. customer_id → first_name, last_name, email, phone, city, registration_date
2. product_id → product_name, category, price, stock_quantity
3. order_id → customer_id, order_date, total_amount, status
4. order_item_id → order_id, product_id, quantity, unit_price, subtotal

3NF Justification:
- 1NF: All tables have atomic values and unique primary keys.
- 2NF: All non-key attributes are fully dependent on the table’s primary key.
  For example, in orders, total_amount depends on order_id, not just customer_id.
- 3NF: There are no transitive dependencies. Customer details are only in customers, and product details are only in products.

Anomaly Avoidance:
- Update anomalies: Changing a product price or customer email requires modification in only one table.
- Insert anomalies: New customers, products, or orders can be inserted independently.
- Delete anomalies: Deleting an order does not remove the customer or product data.

---

## 3. Sample Data Representation

### customers

| customer_id | first_name | last_name | email | phone | city | registration_date |
|------------|------------|-----------|-------|-------|------|------------------|
| C001 | Rahul | Sharma | rahul.sharma@gmail.com | +91-9876543210 | Bangalore | 2023-01-15 |
| C002 | Priya | Patel | priya.patel@yahoo.com | +91-9988776655 | Mumbai | 2023-02-20 |
| C003 | Amit | Kumar | NULL | +91-9765432109 | Delhi | 2023-03-10 |

### products

| product_id | product_name | category | price | stock_quantity |
|-----------|--------------|----------|-------|----------------|
| P001 | Samsung Galaxy S21 | Electronics | 45999.00 | 150 |
| P002 | Nike Running Shoes | Fashion | 3499.00 | 80 |
| P003 | Apple MacBook Pro | Electronics | 52999.00 | 45 |

### orders

| order_id | customer_id | order_date | total_amount | status |
|----------|------------|------------|-------------|--------|
| 1 | C001 | 2024-01-15 | 45999.00 | Completed |
| 2 | C002 | 2024-01-16 | 5998.00 | Completed |
| 3 | C003 | 2024-01-15 | 52999.00 | Completed |

### order_items

| order_item_id | order_id | product_id | quantity | unit_price | subtotal |
|---------------|----------|------------|---------|------------|---------|
| 1 | 1 | P001 | 1 | 45999.00 | 45999.00 |
| 2 | 2 | P004 | 2 | 2999.00 | 5998.00 |
| 3 | 3 | P007 | 1 | 52999.00 | 52999.00 |
