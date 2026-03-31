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
    cur.execute("DESCRIBE customer_dashboard_Favorite_Shops;")
    columns = cur.fetchall()
    for col in columns:
        print(col)
