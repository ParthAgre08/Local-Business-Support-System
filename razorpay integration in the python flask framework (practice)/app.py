from flask import Flask,render_template ,request ,redirect 
import razorpay

app = Flask(__name__)

#Razorpay API keys 
RAZORPAY_KEY_ID = "rzp_test_SepTWnThzqOGes"
RAZORPAY_KEY_SECRET = "wToCdxGSPxSeaHGSmaQkfEY3"  

#Razorpay client intialization 
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID,RAZORPAY_KEY_SECRET))

@app.route("/")
def home():
    return render_template("index.html" , key_id = RAZORPAY_KEY_ID)

@app.route('/order',methods = ['POST'])
def create_order():
    #create an order with razorpay
    amount = 500
    currency = "INR"

    order_data = {
        "amount":amount,
        "currency" : currency
    }
    razorpay_order = razorpay_client.order.create(data=order_data)
    print(razorpay_order)
    return {"order_id":razorpay_order['id'],"amount":amount}


@app.route('/success')
def payment_success():
    return render_template("success.html")

@app.route("/verify",methods=['GET','POST'])
def verify_signature():
    #data from razorpay checkout 
    payment_id  = request.form.get("razorpay_payment_id")
    order_id = request.form.get("razorpay_order_id")
    signature = request.form.get("razorpay_signature")

    #verify signature 
    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id":order_id,
            "razorpay_payment_id":payment_id,
            "razorpay_signature":signature
        })
        return redirect("/success")#redirect to sucess page

    except razorpay.errors.SignatureVerificationError:
        return "Signature verification failed",400

if __name__ == "__main__":
    app.run(debug = True)