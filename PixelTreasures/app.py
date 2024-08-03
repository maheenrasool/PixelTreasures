from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import db 
import os
import stripe

app = Flask(__name__)

# Database configuration
app.config["DB_HOST"] = 'localhost'
app.config["DB_USER"] = 'root'
app.config["DB_PASSWORD"] = '123456'
app.config["DB_DATABASE"] = 'pixeltreasures'
app.config["UPLOAD_FOLDER"] = 'static/uploads' #stores artpieces
app.secret_key = 'my_secret_key' #for session management

#Initialize database setup

db.init_app(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods = ['GET','POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db_connection = db.get_db()
        cursor = db_connection.cursor(dictionary = True) # return rows as dict rather than a tuple
        query = 'SELECT *  FROM sellers WHERE username = %s AND userpassword = %s'
        values = (username, password)
        cursor.execute( query, values )
        user = cursor.fetchone()
        cursor.close()

        if user:

            session['username'] = username
            return redirect(url_for('seller_profile'))
        
        else:

            return "Invalid Credentials"

    return render_template('login.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        account_number = request.form['account_number']
        insert_seller(username, password, email)
        #print(account_number, username)
        insert_account(account_number, username)

        return redirect(url_for('home'))
        
    return render_template('signup.html')

def insert_seller(username, password, email):
    db_connection = db.get_db()
    cursor = db_connection.cursor()
    query = 'INSERT INTO sellers(username, userpassword, email) VALUES (%s, %s, %s)'
    values = (username, password, email)
    cursor.execute(query, values)
    db_connection.commit()
    cursor.close()

    print('was here')
    return

def insert_account(account_number, username):

    db_connection = db.get_db()
    cursor  = db_connection.cursor()
    query = 'INSERT INTO seller_bank_account(username, account_number) VALUES (%s, %s)'
    values = (username, account_number)
    cursor.execute(query, values)
    db_connection.commit()
    cursor.close()

    return



@app.route('/seller_profile', methods=['GET','POST'])
def seller_profile():
        
        if request.method == 'POST': #upload image
            
            upload_art()
        # fetch all art pieces for the seller

        db_connection = db.get_db()
        cursor = db_connection.cursor(dictionary = True)
        query = 'SELECT * FROM artpieces WHERE owner_username = %s'
        value = (session['username'],)
        cursor.execute(query, value)
        art_pieces = cursor.fetchall()
        return render_template('seller_profile.html', art_pieces = art_pieces)

def upload_art():
    art_piece = request.files['art_image']
    item_price = request.form['art_price']
    item_status = 0
    owner_username = session['username']

    db_connection = db.get_db()
    cursor = db_connection.cursor()

    query = 'INSERT INTO artpieces(owner_username, item_status, item_price)  VALUES(%s, %s, %s)'
    values = (owner_username, item_status, item_price)

    cursor.execute(query, values)
    db_connection.commit()
    item_id = cursor.lastrowid

    image_name = f"{item_id}.png"
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
    art_piece.save(image_path)
    cursor.close()

    print("Artpiece added")

    return


@app.route('/shop')
def shop():

     # fetch all art pieces available to sell

    db_connection = db.get_db()
    cursor = db_connection.cursor(dictionary = True)
    query = 'SELECT * FROM artpieces WHERE item_status = %s'
    value = (0,)
    cursor.execute(query, value)
    art_pieces = cursor.fetchall()

    return render_template('shop.html', art_pieces = art_pieces)

@app.route('/calculate_order_amount', methods=['POST'])
def calculate_order_amount():
    
    total = request.form['total']
    return total 


@app.route('/payment')
def payment():
    return render_template('payment.html')



stripe_keys = {
    "secret_key": 'sk_test_51PhWzQRteMEBybePA7fMT5qT6EJ7z4tMhj70tTHWUvwU1nHzkihBQV5xRruGPkpaCbz2Y4Sgx9o3F1ZbhFQo1gsf00PWjpj5O5',
    "publishable_key": 'pk_test_51PhWzQRteMEBybePJMWgIpSKc8WUaepSjZXUvh8emPYrsJbnrCYs1COuS9pL3lzFZyZ2Do6f4HwtKEsSboErXCdd00lEW2NDlO',
}

stripe.api_key = stripe_keys["secret_key"]


@app.route('/process-payment', methods=['POST'])
def process_payment():
    try:
        # Get the token from the form
        token = request.form['stripeToken']
        # Create a charge
        charge = stripe.Charge.create(
            amount=calculate_order_amount(),  # Amount in $
            currency='usd',
            description='Example charge',
            source=token,
        )
       
        return "Payment successful"
    except stripe.error.StripeError as e:
      
        return "Payment failed"

if __name__ == "__main__":
    
    app.run(debug = True)