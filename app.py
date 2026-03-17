from flask import Flask,render_template,redirect,url_for,request,flash
from httpcore import __name

app = Flask(__name__)

# Secret key is required to enable sessions and flash messages in Flask
app.secret_key = "mysecretkey"

@app.route("/",methods=['GET','POST'])
def main():
    if request.method == 'POST':
        flash("Login Successful", "success")# Flash is used to show temporary messages on a web page using session storage.
        return redirect(url_for("home"))
    return render_template("main.html")


@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        session["Email"] = request.form.get("Email")
        session["password"] = request.form.get("password")

    return render_template("login.html")

@app.route("/register",methods=["GET","POST"])
def register():
    return render_template("register.html")

@app.route("/home")
def home():
    return render_template("home.html")

if __name__ == '__main__':
    app.run(debug=True)#we use the debug true because when an error comes so it will show inside the web browser 