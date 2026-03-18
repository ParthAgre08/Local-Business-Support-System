from flask import Flask,request,render_template
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'          # your username
app.config['MYSQL_PASSWORD'] = 'password'  # your password
app.config['MYSQL_DB'] = 'mydatabase'      # your DB name

mysql = MySQL(app)

@app.route("/")
def main():
    return render_template("main.html")


@app.route('/login', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users(username, email, password) VALUES(%s, %s, %s)",
                (username, email, password))
    
    mysql.connection.commit()
    cur.close()

    return render_template("register.html")

app.run()