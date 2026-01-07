/**
 * Task 2.2: MongoDB Implementation
 * File: mongodb_operations.js
 * 
 * Database: productDB
 * Collection: products
 */

const { MongoClient } = require("mongodb");
const fs = require("fs");

// MongoDB connection URL
const url = "mongodb://127.0.0.1:27017";
const dbName = "productDB";
const collectionName = "products";

async function runMongoDBOperations() {
  const client = new MongoClient(url);

  try {
    // Connect to MongoDB
    await client.connect();
    console.log("Connected to MongoDB");

    const db = client.db(dbName);
    const collection = db.collection(collectionName);

    /* ---------------------------------------------------
       OPERATION 1: LOAD DATA
       Import products_catalog.json into 'products' collection
    --------------------------------------------------- */
    const data = JSON.parse(fs.readFileSync("products_catalog.json", "utf8"));

    // Prevent duplicate insertions
    const count = await collection.countDocuments();
    if (count === 0) {
      await collection.insertMany(data);
      console.log("Product data loaded successfully");
    } else {
      console.log("Data already exists, skipping insertion");
    }

    /* ---------------------------------------------------
       OPERATION 2: BASIC QUERY
       Find all Electronics products with price < 50000
       Return only name, price, and stock
    --------------------------------------------------- */
    const electronicsUnder50k = await collection.find(
      { category: "Electronics", price: { $lt: 50000 } },
      { projection: { _id: 0, name: 1, price: 1, stock: 1 } }
    ).toArray();

    console.log("\nElectronics products under 50000:");
    console.log(electronicsUnder50k);

    /* ---------------------------------------------------
       OPERATION 3: REVIEW ANALYSIS
       Find products with average rating >= 4.0
       Use aggregation on reviews array
    --------------------------------------------------- */
    const highRatedProducts = await collection.aggregate([
      { $unwind: "$reviews" },
      {
        $group: {
          _id: "$product_id",
          name: { $first: "$name" },
          avg_rating: { $avg: "$reviews.rating" }
        }
      },
      { $match: { avg_rating: { $gte: 4.0 } } }
    ]).toArray();

    console.log("\nProducts with average rating >= 4.0:");
    console.log(highRatedProducts);

    /* ---------------------------------------------------
       OPERATION 4: UPDATE OPERATION
       Add a new review to product "ELEC001"
    --------------------------------------------------- */
    const newReview = {
      user: "U999",
      rating: 4,
      comment: "Good value",
      date: new Date()
    };

    await collection.updateOne(
      { product_id: "ELEC001" },
      { $push: { reviews: newReview } }
    );

    console.log("\nNew review added to product ELEC001");

    /* ---------------------------------------------------
       OPERATION 5: COMPLEX AGGREGATION
       Calculate average price by category
       Return category, avg_price, product_count
       Sort by avg_price descending
    --------------------------------------------------- */
    const avgPriceByCategory = await collection.aggregate([
      {
        $group: {
          _id: "$category",
          avg_price: { $avg: "$price" },
          product_count: { $sum: 1 }
        }
      },
      {
        $project: {
          _id: 0,
          category: "$_id",
          avg_price: 1,
          product_count: 1
        }
      },
      { $sort: { avg_price: -1 } }
    ]).toArray();

    console.log("\nAverage price by category:");
    console.log(avgPriceByCategory);

  } catch (error) {
    console.error("Error executing MongoDB operations:", error);
  } finally {
    // Close connection
    await client.close();
    console.log("\nMongoDB connection closed");
  }
}

// Run all operations
runMongoDBOperations();
