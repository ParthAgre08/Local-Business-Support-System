"""
Run this script once to create the 'products' table in the MySQL database.
Usage: python create_products_table.py
"""
import MySQLdb

conn = MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='123456789',
    db='user'
)

cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INT AUTO_INCREMENT PRIMARY KEY,
        shop_name VARCHAR(255) NOT NULL,
        owner_email VARCHAR(255) NOT NULL,
        product_name VARCHAR(255) NOT NULL,
        description TEXT,
        price DECIMAL(10,2) NOT NULL,
        product_image VARCHAR(255) DEFAULT 'default.jpg',
        stock INT NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()
cur.close()
conn.close()

print("✅ 'products' table created successfully!")
