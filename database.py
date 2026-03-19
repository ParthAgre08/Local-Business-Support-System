from flask import Flask,request,render_template
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'          # your username
app.config['MYSQL_PASSWORD'] = '123456789'  # your password
app.config['MYSQL_DB'] = 'user'      # your DB name

mysql = MySQL(app)

@app.route("/")
def main():
    return render_template("main.html")


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "POST":

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO user(username, email, password) VALUES(%s, %s, %s)",
                    (username, email, password))
        
        mysql.connection.commit()
        cur.close()
        return "<h1>You register sucessfully</h1>"

    return render_template("register.html")

app.run()