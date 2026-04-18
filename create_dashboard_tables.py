"""
Run this script once to create the dashboard-related tables in the MySQL database.
Tables: bookings, ratings, owner_earnings, products (kept from before)
Usage: python create_dashboard_tables.py
"""
import MySQLdb

conn = MySQLdb.connect(
    host='localhost',
    user='root',
    passwd='123456789',
    db='user'
)

cur = conn.cursor()

# Products table (kept from original)
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
print("✅ 'products' table created/verified!")

# Bookings table — records every product booking
cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_email VARCHAR(255) NOT NULL,
        owner_email VARCHAR(255) NOT NULL,
        shop_name VARCHAR(255) NOT NULL,
        product_name VARCHAR(255) NOT NULL,
        product_price DECIMAL(10,2) NOT NULL,
        order_type ENUM('online','offline') DEFAULT 'online',
        status VARCHAR(50) DEFAULT 'Confirmed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
print("✅ 'bookings' table created successfully!")

# Ratings table — stores customer ratings per business
cur.execute("""
    CREATE TABLE IF NOT EXISTS ratings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_email VARCHAR(255) NOT NULL,
        shop_name VARCHAR(255) NOT NULL,
        owner_email VARCHAR(255) NOT NULL,
        rating INT NOT NULL,
        review TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
print("✅ 'ratings' table created successfully!")

# Owner earnings table — running total of each owner's earnings
cur.execute("""
    CREATE TABLE IF NOT EXISTS owner_earnings (
        id INT AUTO_INCREMENT PRIMARY KEY,
        owner_email VARCHAR(255) UNIQUE NOT NULL,
        total_earnings DECIMAL(12,2) DEFAULT 0.00,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
""")
print("✅ 'owner_earnings' table created successfully!")

conn.commit()
cur.close()
conn.close()

print("\n🎉 All dashboard tables created successfully!")
