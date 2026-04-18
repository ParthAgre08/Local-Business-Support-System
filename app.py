from flask import Flask,render_template,redirect,url_for,request,flash,session,jsonify
from httpcore import __name
from flask_mysqldb import MySQL
import os 
from werkzeug.utils import secure_filename 
from dotenv import load_dotenv

load_dotenv()

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
    
    # Active businesses count
    cur.execute("SELECT COUNT(*) FROM business_record WHERE email = %s", (email,))
    active_businesses_count = cur.fetchone()[0]
    
    # Total earnings from owner_earnings table
    cur.execute("SELECT total_earnings FROM owner_earnings WHERE owner_email = %s", (email,))
    earnings_row = cur.fetchone()
    total_earnings = float(earnings_row[0]) if earnings_row else 0.00
    
    # Average rating across all owner's businesses
    cur.execute("""
        SELECT AVG(r.rating) FROM ratings r
        INNER JOIN business_record b ON r.shop_name = b.name
        WHERE b.email = %s
    """, (email,))
    avg_row = cur.fetchone()
    avg_rating = round(float(avg_row[0]), 1) if avg_row and avg_row[0] else 0.0
    
    # Total bookings count
    cur.execute("SELECT COUNT(*) FROM bookings WHERE owner_email = %s", (email,))
    total_bookings = cur.fetchone()[0]
    
    # Recent activity (last 5 bookings)
    cur.execute("""
        SELECT customer_email, shop_name, product_name, product_price, order_type, created_at
        FROM bookings WHERE owner_email = %s ORDER BY created_at DESC LIMIT 5
    """, (email,))
    recent_bookings = cur.fetchall()
    
    # Recent ratings (last 5)
    cur.execute("""
        SELECT customer_email, shop_name, rating, review, created_at
        FROM ratings WHERE owner_email = %s ORDER BY created_at DESC LIMIT 5
    """, (email,))
    recent_ratings = cur.fetchall()
    
    cur.close()
    
    return render_template("owner_dashboard.html",
        username=session['username'],
        active_businesses=active_businesses_count,
        total_earnings=total_earnings,
        avg_rating=avg_rating,
        total_bookings=total_bookings,
        recent_bookings=recent_bookings,
        recent_ratings=recent_ratings
    )



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
        subcategory = request.form.get("subcategory")
        starting_time = request.form.get("starting_time")
        closing_time = request.form.get("closing_time")
        email = session['email']
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")

        #getting the files uploaded by the user 
        image = request.files['image']

        if image and image.filename != "":
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'] ,filename))

        else:
            filename = 'default.jpg'

        cur = mysql.connection.cursor()
        latitude_val = f"'{latitude}'" if latitude else "NULL"
        longitude_val = f"'{longitude}'" if longitude else "NULL"

        cur.execute(
            f"INSERT INTO business_record (name,description,location,category,images,starting_time,closing_time,email,subcategory,latitude,longitude) "
            f"VALUES ('{name}','{description}','{location}','{category}','{filename}','{starting_time}','{closing_time}','{email}','{subcategory}',{latitude_val},{longitude_val})"
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
    subcategory = request.args.get("subcategory")

    cur = mysql.connection.cursor()
    # Explicitly select columns to maintain consistent indexing even if table structure changes
    sql = "SELECT id, name, description, location, category, subcategory, images, starting_time, closing_time, email, latitude, longitude FROM business_record WHERE 1=1"
    params = []
    
    if query:
        sql += " AND (name LIKE %s OR description LIKE %s)"
        params.append(f"%{query}%")
        params.append(f"%{query}%")

    if location and location != "" and location != "Nearby":
        sql += " AND location = %s"
        params.append(location)

    if category and category != "":
        sql += " AND category = %s"
        params.append(category)

    if subcategory and subcategory != "All" and subcategory != "":
        sql += " AND subcategory = %s"
        params.append(subcategory)

    if not params:
        cur.execute("SELECT id, name, description, location, category, subcategory, images, starting_time, closing_time, email, latitude, longitude FROM business_record LIMIT 50") 
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
        
        # With explicit SELECT:
        # 0:id, 1:name, 2:description, 3:location, 4:category, 5:subcategory, 6:images, 7:starting_time, 8:closing_time, 9:email, 10:latitude, 11:longitude
        if len(row_list) > 8:
            start_td = row_list[7]
            close_td = row_list[8]
            
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
                
        # Append extra info: is_open, start_str, close_str
        row_list.append(is_open)
        row_list.append(start_str)
        row_list.append(close_str)
        
        # Sanitize row_list for JSON: convert timedeltas to strings
        final_row = []
        for item in row_list:
            if isinstance(item, datetime.timedelta):
                final_row.append(str(item))
            elif isinstance(item, (datetime.date, datetime.datetime)):
                final_row.append(item.isoformat())
            else:
                final_row.append(item)
        results.append(final_row)
        
    user_favorites = []
    if 'email' in session:
        cur.execute("SELECT shop_name FROM customer_dashboard_favorite_shops WHERE Email = %s", (session['email'],))
        favs = cur.fetchall()
        user_favorites = [f[0] for f in favs]
        
    cur.close()
    
    # Handle AJAX/Fetch request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.args.get('ajax') == '1':
        return jsonify({
            'results': results,
            'user_favorites': user_favorites
        })

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

@app.route('/manage_products')
def manage_products():
    if 'email' not in session:
        return redirect('/login')
    
    email = session['email']
    cur = mysql.connection.cursor()
    
    # Get owner's business names
    cur.execute("SELECT name FROM business_record WHERE email = %s", (email,))
    businesses_raw = cur.fetchall()
    businesses = [b[0] for b in businesses_raw]
    
    # Get all products for this owner
    cur.execute("SELECT id, shop_name, owner_email, product_name, description, price, product_image, stock, created_at FROM products WHERE owner_email = %s ORDER BY created_at DESC", (email,))
    products = cur.fetchall()
    cur.close()
    
    return render_template("manage_products.html", username=session['username'], businesses=businesses, products=products)


@app.route('/add_product', methods=['POST'])
def add_product():
    if 'email' not in session:
        return redirect('/login')
    
    shop_name = request.form.get('shop_name')
    product_name = request.form.get('product_name')
    description = request.form.get('description', '')
    price = request.form.get('price')
    stock = request.form.get('stock', 0)
    email = session['email']
    
    # Handle image upload
    image = request.files.get('product_image')
    if image and image.filename != '':
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        filename = 'default.jpg'
    
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO products (shop_name, owner_email, product_name, description, price, product_image, stock) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (shop_name, email, product_name, description, price, filename, stock)
    )
    mysql.connection.commit()
    cur.close()
    
    flash("Product added successfully!", "success")
    return redirect('/manage_products')


@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'email' not in session:
        return redirect('/login')
    
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM products WHERE id = %s AND owner_email = %s", (product_id, session['email']))
    mysql.connection.commit()
    cur.close()
    
    flash("Product deleted!", "success")
    return redirect('/manage_products')


@app.route('/shop/<shop_name>/products')
def shop_products(shop_name):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, shop_name, owner_email, product_name, description, price, product_image, stock, created_at FROM products WHERE shop_name = %s ORDER BY created_at DESC", (shop_name,))
    products = cur.fetchall()
    cur.close()
    
    return render_template("shop_products.html", shop_name=shop_name, products=products, username=session.get('username'))


@app.route('/my_businesses')
def my_businesses():
    if 'email' not in session:
        return redirect('/login')
    
    email = session['email']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, name, description, location, category, subcategory, images, starting_time, closing_time, latitude, longitude
        FROM business_record WHERE email = %s ORDER BY id DESC
    """, (email,))
    businesses_raw = cur.fetchall()
    
    import datetime
    businesses = []
    for b in businesses_raw:
        start_str = ''
        close_str = ''
        if b[7] and b[8]:
            def format_td(td):
                if isinstance(td, datetime.timedelta):
                    total_seconds = int(td.total_seconds())
                else:
                    return str(td)
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
            start_str = format_td(b[7])
            close_str = format_td(b[8])
        
        # Get booking count for this business
        cur.execute("SELECT COUNT(*) FROM bookings WHERE shop_name = %s AND owner_email = %s", (b[1], email))
        booking_count = cur.fetchone()[0]
        
        # Get avg rating for this business
        cur.execute("SELECT AVG(rating) FROM ratings WHERE shop_name = %s AND owner_email = %s", (b[1], email))
        rating_row = cur.fetchone()
        biz_rating = round(float(rating_row[0]), 1) if rating_row and rating_row[0] else 0.0
        
        businesses.append({
            'id': b[0],
            'name': b[1],
            'description': b[2],
            'location': b[3],
            'category': b[4],
            'subcategory': b[5],
            'image': b[6],
            'start_time': start_str,
            'close_time': close_str,
            'bookings': booking_count,
            'rating': biz_rating
        })
    
    cur.close()
    return render_template('my_businesses.html', username=session['username'], businesses=businesses)


@app.route('/book_product', methods=['POST'])
def book_product():
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.json
    customer_email = session['email']
    shop_name = data.get('shop_name')
    product_name = data.get('product_name')
    order_type = data.get('order_type', 'online')
    
    cur = mysql.connection.cursor()
    
    # Get product price and owner email
    cur.execute("SELECT price, owner_email, stock FROM products WHERE shop_name = %s AND product_name = %s", (shop_name, product_name))
    product = cur.fetchone()
    
    if not product:
        cur.close()
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    
    price = float(product[0])
    owner_email = product[1]
    stock = product[2]
    
    if stock <= 0:
        cur.close()
        return jsonify({'success': False, 'message': 'Out of stock'}), 400
    
    # Insert booking
    cur.execute(
        "INSERT INTO bookings (customer_email, owner_email, shop_name, product_name, product_price, order_type) VALUES (%s, %s, %s, %s, %s, %s)",
        (customer_email, owner_email, shop_name, product_name, price, order_type)
    )
    
    # Update owner earnings (INSERT or UPDATE)
    cur.execute(
        "INSERT INTO owner_earnings (owner_email, total_earnings) VALUES (%s, %s) ON DUPLICATE KEY UPDATE total_earnings = total_earnings + %s",
        (owner_email, price, price)
    )
    
    # Decrement stock
    cur.execute("UPDATE products SET stock = stock - 1 WHERE shop_name = %s AND product_name = %s", (shop_name, product_name))
    
    mysql.connection.commit()
    
    # Get the booking ID
    booking_id = cur.lastrowid
    cur.close()
    
    return jsonify({'success': True, 'booking_id': booking_id, 'price': price, 'shop_name': shop_name})


@app.route('/submit_rating', methods=['POST'])
def submit_rating():
    if 'email' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    data = request.json
    customer_email = session['email']
    shop_name = data.get('shop_name')
    rating = data.get('rating')
    review = data.get('review', '')
    
    if not rating or not shop_name:
        return jsonify({'success': False, 'message': 'Missing data'}), 400
    
    # Get owner email from business_record
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM business_record WHERE name = %s LIMIT 1", (shop_name,))
    biz = cur.fetchone()
    
    if not biz:
        cur.close()
        return jsonify({'success': False, 'message': 'Business not found'}), 404
    
    owner_email = biz[0]
    
    cur.execute(
        "INSERT INTO ratings (customer_email, shop_name, owner_email, rating, review) VALUES (%s, %s, %s, %s, %s)",
        (customer_email, shop_name, owner_email, rating, review)
    )
    mysql.connection.commit()
    cur.close()
    
    return jsonify({'success': True})


@app.route('/category')
def category():
    return render_template('category.html', username=session.get('username'))


@app.route('/about')
def about():
    return render_template('about.html', username=session.get('username'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)#we use the debug true because when an error comes so it will show inside the web browser 