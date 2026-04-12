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
    try:
        cur.execute("ALTER TABLE customer_dashboard_Favorite_Shops DROP INDEX Email;")
        mysql.connection.commit()
        print("Successfully dropped UNIQUE constraint on Email.")
    except Exception as e:
        print("Error:", e)
    finally:
        cur.close()
