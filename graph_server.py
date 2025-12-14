# graph_server.py


from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from models import db, Cryptocurrency, Portfolio, Order
from execute_update_trades import place_order


USER_FILE = 'users.txt'

# Flask server to display graphs in a webpage

class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://Sriman:SpitterDune#891*@localhost/crypto_market_sim' # Specifies the database URI (Unique Resouce Identifier); basically tells which database to connect to & under what user & password should be used
    SQLALCHEMY_TRACK_MODIFICATIONS = False # Disables a feature that tracks changes to objects making it more resource-efficient


app = Flask(__name__) # Initialises a Flask app instance which allows to locate resources & files
app.config.from_object(Config) # Configures the Flask app using the settings defined in the Config class

db.init_app(app) # Connects the database to the Flask app so it can manage the database connections & perform ORM operations

@app.route('/') # Listens to when the root URL (/) is triggered. If so, it calls the index func.
def index():
# func. is executed when root URL (/) is accessed

    return render_template('index.html')


def read_users():
    users = {}

    try:
        with open(USER_FILE, 'r') as file:
            for line in file:
                email, password = line.strip().split(',')

                users[email] = password

    except FileNotFoundError:
        pass

    return users

def write_user(email, password):
    with open(USER_FILE, 'a') as file:
        file.write(f'{email},{password}\n')


@app.route('/login', methods = ['POST'])
def login():
    data = request.json

    email = data.get('email')
    password = data.get('password')

    users = read_users()

    if email in users and users[email] == password:
        session['user_email'] = email

        return jsonify({'message' : "Login successful"})
    
    else:

        return jsonify({'error' : "Invalid credentials"}), 401


@app.route('/register', methods = ['POST'])
def register():
    data = request.json

    email = data.get('email')
    password = data.get('password')

    users = read_users()

    if email in users:

        return jsonify({'error' : "Email already registered"}), 400
    
    write_user(email, password)

    return jsonify({'message' : "User registered successfully"})


@app.route('/logout')
def logout():
    session.pop('user_email', None)

    return redirect('/login')


@app.route('/graph_display')
def graphs():
    cryptocurrencies = Cryptocurrency.query.all() # Returns a list of all cryptocurrencies listed in the cryptocurrency table

    return render_template('graph_display.html', cryptocurrencies = cryptocurrencies) # Displays the graph_display.html page template, passing cryptocurrencies list as a variable


@app.route('/place_order', methods = ['GET', 'POST'])
def orders():
    if request.method == 'POST':

        user_id = 1
        order_type = request.form['order_type']
        asset = request.form['asset']
        quantity = float(request.form['quantity'])

        try:
            place_order(user_id, order_type, asset, quantity)

            return redirect(url_for('portfolio_data'))

        except Exception as e:
            return f"Error placing order : {str(e)}"

    return render_template('place_order.html')


@app.route('/portfolio')
def portfolio_data():
    user_id = 1
    
    portfolio = Portfolio.query.filter_by(user_id = user_id).all()

    return render_template(portfolio.html, portfolio_data = portfolio_data)


app.run(debug = True) # Starts the Flask app which listens for incoming requests & displays them on the HTML page. debug = True allows automatic reloading on code changes & detailed error messages
