from flask import Flask,render_template,redirect,url_for,request,flash,session
from httpcore import __name
from flask_mysqldb import MySQL


app = Flask(__name__)

# Secret key is required to enable sessions and flash messages in Flask
app.secret_key = "mysecretkey"

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'          # your username
app.config['MYSQL_PASSWORD'] = '123456789'  # your password
app.config['MYSQL_DB'] = 'user'      # your DB name

mysql = MySQL(app)


@app.route("/",methods=['GET','POST'])
def main():
    if request.method == 'POST':
        flash("Login Successful", "success")# Flash is used to show temporary messages on a web page using session storage.
        return redirect(url_for("home"))
    return render_template("main.html")


@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        cur = mysql.connection.cursor()
        cur.execute(F"SELECT * FROM user WHERE Email = '{email}' && Password = '{password}'")
        data = cur.fetchone()
        print(email," ",password)

        if data:
            session['email'] = email
            session['password'] = password
            session['username'] = data[3]
            flash("Login Successful", "success")
            return redirect("/home")
           
        else:
            flash("Login Unsuccesfull !", "error")
            return redirect("/login")

    return render_template("login.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if(request.method == "POST"):
        session['email'] = request.form.get("email")
        session['password'] = request.form.get("password")
        session['username'] = request.form.get("username")

        cur = mysql.connection.cursor()
        cur.execute(f"INSERT INTO user (Email,Password,Username) values ('{session['email']}','{session['password']}','{session['username']}')")

        mysql.connection.commit()
        cur.close()
        flash("Register Successful", "success")
        return redirect("/home")
    return render_template("register.html")

@app.route("/home")
def home():
    return render_template("home.html",username = session['username'])



@app.route('/customer_dashboard')
def customer_dashboard():
    if 'username' not in session:
        return redirect('/login')

    return render_template('customer_dashboard.html', username=session['username'])



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)#we use the debug true because when an error comes so it will show inside the web browser 