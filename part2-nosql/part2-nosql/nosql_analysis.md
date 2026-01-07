# NoSQL Justification Report

## Section A: Limitations of RDBMS (Relational Databases)

Relational database management systems (RDBMS) use fixed schemas with predefined tables and columns. In a product catalog where products have different attributes, such as laptops having RAM and processors while shoes have size and color, an RDBMS would struggle to model this efficiently. It would require either many nullable columns or multiple related tables, increasing complexity and reducing clarity.

Frequent schema changes are another major limitation. When new product types or attributes are introduced, the database schema must be altered using operations such as `ALTER TABLE`, which can be time-consuming and risky for large datasets. These changes may also cause downtime.

Storing customer reviews is also challenging in relational databases. Reviews would typically be stored in a separate table and linked using foreign keys. Retrieving a product along with all its reviews requires complex joins, which can negatively impact performance and make queries harder to maintain.

---

## Section B: Benefits of NoSQL (MongoDB)

MongoDB addresses these limitations through its flexible, document-based data model. Each product is stored as a document, allowing different products to have different attributes without enforcing a fixed schema. This makes it easy to store laptops, smartphones, and clothing items in the same collection while keeping their unique specifications.

Embedded documents allow related data, such as customer reviews, to be stored directly inside the product document. This improves read performance and simplifies queries, as all relevant information can be retrieved in a single operation without joins.

MongoDB also supports horizontal scalability through sharding, allowing data to be distributed across multiple servers. This makes it suitable for growing product catalogs and high-traffic applications, where traditional relational databases may struggle to scale efficiently.

---

## Section C: Trade-offs of Using MongoDB

One disadvantage of using MongoDB instead of MySQL is the lack of strong relational constraints such as foreign keys, which can make enforcing data consistency more difficult at the database level. Developers must handle validation and relationships within the application logic.

Another drawback is that MongoDB may not be ideal for complex transactional operations involving multiple documents, as relational databases generally provide stronger ACID guarantees. For systems that rely heavily on complex transactions and strict consistency, a relational database may still be a better choice.

