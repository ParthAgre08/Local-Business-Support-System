from flask import Flask,render_template,redirect,url_for,request,flash,session
from httpcore import __name
from flask_mysqldb import MySQL
import os 
from werkzeug.utils import secure_filename 

#craeting the obj of flask class and save into app or we also say creating the flask app 
app = Flask(__name__)

# Secret key is required to enable sessions and flash messages in Flask
app.secret_key = "mysecretkey"

# MySQL Config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'          # your username
app.config['MYSQL_PASSWORD'] = '123456789'  # your password
app.config['MYSQL_DB'] = 'user'      # your DB name

mysql = MySQL(app)

# creating the upload folder (folder path config)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



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


@app.route("/owner_dashboard")
def owner_dashboard():
    return render_template("dashboard.html", username=session['username'],name = name , location=location, description = description , category = category)



@app.route("/home")
def home():
    return render_template("home.html",username = session['username'])


@app.route('/customer_dashboard')
def customer_dashboard():
    if 'username' not in session:
        return redirect('/login')

    return render_template('customer_dashboard.html', username=session['username'])



@app.route("/addbusiness" , methods = ["GET","POST"])
def addbusiness():
    if request.method == 'POST':
        #getting the form section details 
        name = request.form.get("name")
        location = request.form.get("location")
        description = request.form.get("description")
        category = request.form.get("category")

        #getting the files uploaded by the user 
        image = request.files['image']

        if image and image.filename != "":
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'] ,filename))

        else:
            filename = 'default.jpg'

        cur = mysql.connection.cursor()
        cur.execute(f"INSERT INTO business_record (name,description,location,category,images) VALUES ('{name}','{description}','{location}','{category}','{filename}')")
        mysql.connection.commit()
        cur.close()

        # return redirect(url_for('owner_dashboard',name = name , location=location, description = description , category = category))
        return render_template("dashboard.html",username = session['username'],name = name , location=location, description = description , category = category)
    return render_template("addbusiness.html")


@app.route("/search",methods =["GET", "POST"])
def search():
    query  = request.args.get("query ")
    location = request.args.get("location")
    category = request.args.get("category")

    cur = mysql.connection.cursor()
    sql = "SELECT * FROM business_record WHERE 1=1"
    
    if query:
        sql += f"AND name LIKE '%{query}%'"

    if location:
        sql += f"AND loaction = {loaction}" 

    if category:
        sql += f"AND category  = {category}"

    if not query and not location and not category:
        cur.execute("SELECT * FROM business_record LIMIT 6") 

    cur.execute(sql)
    results = cur.fetchall()#.fetchall() so Get all rows returned by the SQL query
    cur.close()
    
    return render_template("search.html",username = session['username'],results = results)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)#we use the debug true because when an error comes so it will show inside the web browser 