from flask import Flask,render_template,redirect,url_for,request,flash,session,jsonify
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

@app.context_processor
def inject_owner_status():
    is_owner = False
    if 'email' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1 FROM business_record WHERE email = %s LIMIT 1", (session['email'],))
        if cur.fetchone():
            is_owner = True
        cur.close()
    return dict(is_owner=is_owner)



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
    if 'email' not in session:
        return redirect('/login')
        
    email = session['email']
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM business_record WHERE email = %s", (email,))
    active_businesses_count = cur.fetchone()[0]
    cur.close()
    
    return render_template("owner_dashboard.html", username=session['username'], active_businesses=active_businesses_count)



@app.route("/home")
def home():
    return render_template("home.html",username = session['username'])


@app.route('/customer_dashboard')
def customer_dashboard():
    if 'username' not in session:
        return redirect('/login')

    email = session.get('email')
    cur = mysql.connection.cursor()
    
    # Orders count
    cur.execute("SELECT COUNT(*) FROM customer_dashboard_recent_orders WHERE Email = %s", (email,))
    orders_count = cur.fetchone()[0]
    
    # Fav count
    cur.execute("SELECT COUNT(*) FROM customer_dashboard_favorite_shops WHERE Email = %s", (email,))
    fav_count = cur.fetchone()[0]
    
    # Reviews count
    cur.execute("SELECT COUNT(*) FROM customer_dashboard_reviews WHERE Email = %s", (email,))
    reviews_count = cur.fetchone()[0]
    
    # Recent orders
    cur.execute("SELECT id, shop_name, order_detail, Order_Status FROM customer_dashboard_recent_orders WHERE Email = %s ORDER BY Id DESC LIMIT 3", (email,))
    recent_orders_raw = cur.fetchall()
    cur.close()
    
    recent_orders = []
    for row in recent_orders_raw:
        recent_orders.append({
            'id': row[0],
            'business_name': row[1],
            'items_summary': row[2],
            'status': row[3],
            'status_type': 'delivered' if row[3] == 'Delivered' else ('service' if row[3] == 'Service Complete' else 'pending'),
            'created_at': 'recently',
            'has_review': False
        })

    return render_template('customer_dashboard.html', 
                            username=session['username'],
                            orders_count=orders_count,
                            fav_count=fav_count,
                            reviews_count=reviews_count,
                            recent_orders=recent_orders)



@app.route("/addbusiness" , methods = ["GET","POST"])
def addbusiness():
    if 'email' not in session:
        flash("Please log in to add a business", "error")
        return redirect('/login')

    if request.method == 'POST':
        #getting the form section details 
        name = request.form.get("name")
        location = request.form.get("location")
        description = request.form.get("description")
        category = request.form.get("category")
        starting_time = request.form.get("starting_time")
        closing_time = request.form.get("closing_time")
        email = session['email']

        #getting the files uploaded by the user 
        image = request.files['image']

        if image and image.filename != "":
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'] ,filename))

        else:
            filename = 'default.jpg'

        cur = mysql.connection.cursor()
        cur.execute(
            f"INSERT INTO business_record (name,description,location,category,images,starting_time,closing_time,email) "
            f"VALUES ('{name}','{description}','{location}','{category}','{filename}','{starting_time}','{closing_time}','{email}')"
        )
        mysql.connection.commit()
        cur.close()

        # return redirect(url_for('owner_dashboard',name = name , location=location, description = description , category = category))
        return redirect(url_for("owner_dashboard"))
    return render_template("addbusiness.html")


@app.route("/search",methods =["GET", "POST"])
def search():
    query = request.args.get("query")
    location = request.args.get("location")
    category = request.args.get("category")

    cur = mysql.connection.cursor()
    sql = "SELECT * FROM business_record WHERE 1=1"
    params = []
    
    if query:
        sql += " AND name LIKE %s"
        params.append(f"%{query}%")

    if location:
        sql += " AND location = %s"
        params.append(location)

    if category:
        sql += " AND category = %s"
        params.append(category)

    if not params:
        cur.execute("SELECT * FROM business_record LIMIT 6") 
        results_raw = cur.fetchall()
    else:
        cur.execute(sql, tuple(params))
        results_raw = cur.fetchall()
        
    import datetime
    now_dt = datetime.datetime.now()
    now_td = datetime.timedelta(hours=now_dt.hour, minutes=now_dt.minute, seconds=now_dt.second)
    
    results = []
    for row in results_raw:
        row_list = list(row)
        is_open = False
        start_str = ""
        close_str = ""
        
        # Check if the row has starting_time and closing_time (index 6 and 7)
        if len(row_list) > 7:
            start_td = row_list[6]
            close_td = row_list[7]
            
            if isinstance(start_td, datetime.timedelta) and isinstance(close_td, datetime.timedelta):
                if start_td <= close_td:
                    is_open = start_td <= now_td <= close_td
                else:
                    is_open = now_td >= start_td or now_td <= close_td
                    
                def format_td(td):
                    total_seconds = int(td.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    period = "AM"
                    if hours >= 12:
                        period = "PM"
                        if hours > 12:
                            hours -= 12
                    if hours == 0:
                        hours = 12
                    return f"{hours}:{minutes:02d} {period}"
                    
                start_str = format_td(start_td)
                close_str = format_td(close_td)
                
        # Append extra info: index 8 is is_open, 9 is start_str, 10 is close_str
        while len(row_list) <= 7:
            row_list.append(None)
        row_list.append(is_open)
        row_list.append(start_str)
        row_list.append(close_str)
        results.append(row_list)
        
    user_favorites = []
    if 'email' in session:
        cur.execute("SELECT shop_name FROM customer_dashboard_favorite_shops WHERE Email = %s", (session['email'],))
        favs = cur.fetchall()
        user_favorites = [f[0] for f in favs]
        
    cur.close()
    
    return render_template("search.html", username=session.get('username'), results=results, user_favorites=user_favorites)

@app.route('/toggle_favorite', methods=['POST'])
def toggle_favorite():
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.json
    shop_name = data.get('shop_name')
    shop_location = data.get('shop_location')
    shop_details = data.get('shop_details')
    email = session['email']
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT Id FROM customer_dashboard_favorite_shops WHERE Email = %s AND shop_name = %s", (email, shop_name))
    existing = cur.fetchone()
    
    if existing:
        # Remove from favorites
        cur.execute("DELETE FROM customer_dashboard_favorite_shops WHERE Id = %s", (existing[0],))
        mysql.connection.commit()
        action = 'removed'
    else:
        # Add to favorites
        cur.execute(
            "INSERT INTO customer_dashboard_favorite_shops (Email, shop_name, shop_location, shop_details) VALUES (%s, %s, %s, %s)",
            (email, shop_name, shop_location, shop_details[:499])
        )
        mysql.connection.commit()
        action = 'added'
        
    cur.close()
    return jsonify({'success': True, 'action': action})

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)#we use the debug true because when an error comes so it will show inside the web browser 