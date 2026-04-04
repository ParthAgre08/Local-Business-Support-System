from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456789'
app.config['MYSQL_DB'] = 'user'

mysql = MySQL(app)

with app.app_context():
    cur = mysql.connection.cursor()
    # Create the customer_dashboard_reviews table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customer_dashboard_reviews (
            Id INT AUTO_INCREMENT PRIMARY KEY,
            Email VARCHAR(100),
            shop_name VARCHAR(100),
            review_text VARCHAR(500),
            rating INT
        );
    """)
    mysql.connection.commit()
    
    cur.execute("DESCRIBE customer_dashboard_reviews;")
    columns = cur.fetchall()
    print("Columns in customer_dashboard_reviews:")
    for col in columns:
        print(col)
    cur.close()
