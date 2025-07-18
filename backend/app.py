from flask import Flask, jsonify, request, session, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this in production
CORS(app, supports_credentials=True)

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['bakery_db']

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_admin():
    return session.get('role') == 'admin'

def is_customer():
    return session.get('role') == 'customer'

# Auth endpoints
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    if db.customers.find_one({'email': data['email']}):
        return jsonify({'error': 'Email already registered'}), 400
    db.customers.insert_one({
        'name': data['name'],
        'email': data['email'],
        'password': data['password'],  # Hash in production!
        'cart': []
    })
    return jsonify({'message': 'Registration successful'})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    # Admin login
    if data['email'] == 'admin@bakery.com' and data['password'] == 'admin123':
        session['role'] = 'admin'
        session['email'] = data['email']
        return jsonify({'message': 'Admin login successful', 'role': 'admin'})
    # Customer login
    user = db.customers.find_one({'email': data['email'], 'password': data['password']})
    if user:
        session['role'] = 'customer'
        session['email'] = data['email']
        return jsonify({'message': 'Customer login successful', 'role': 'customer'})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'})

# Product image upload
@app.route('/upload', methods=['POST'])
def upload():
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file'}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    return jsonify({'url': f'/static/images/{filename}'})

@app.route('/static/images/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Products CRUD
@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'GET':
        products = list(db.products.find({}, {'_id': 0}))
        return jsonify(products)
    elif request.method == 'POST':
        if not is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        data = request.json
        db.products.insert_one(data)
        return jsonify({'message': 'Product added'}), 201

@app.route('/products/<name>', methods=['PUT', 'DELETE'])
def product_detail(name):
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    if request.method == 'PUT':
        data = request.json
        db.products.update_one({'name': name}, {'$set': data})
        return jsonify({'message': 'Product updated'})
    elif request.method == 'DELETE':
        db.products.delete_one({'name': name})
        return jsonify({'message': 'Product deleted'})

# Cart endpoints
@app.route('/cart', methods=['GET', 'POST', 'PUT', 'DELETE'])
def cart():
    if not is_customer():
        return jsonify({'error': 'Unauthorized'}), 403
    email = session['email']
    user = db.customers.find_one({'email': email})
    if request.method == 'GET':
        return jsonify(user.get('cart', []))
    elif request.method == 'POST':
        item = request.json
        db.customers.update_one({'email': email}, {'$push': {'cart': item}})
        return jsonify({'message': 'Item added to cart'})
    elif request.method == 'PUT':
        cart = request.json.get('cart', [])
        db.customers.update_one({'email': email}, {'$set': {'cart': cart}})
        return jsonify({'message': 'Cart updated'})
    elif request.method == 'DELETE':
        db.customers.update_one({'email': email}, {'$set': {'cart': []}})
        return jsonify({'message': 'Cart cleared'})

# Orders CRUD (admin only for now)
@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if request.method == 'GET':
        if not is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        orders = list(db.orders.find({}, {'_id': 0}))
        return jsonify(orders)
    elif request.method == 'POST':
        if not is_admin():
            return jsonify({'error': 'Unauthorized'}), 403
        data = request.json
        db.orders.insert_one(data)
        return jsonify({'message': 'Order added'}), 201

# Customers CRUD (admin only for now)
@app.route('/customers', methods=['GET'])
def customers():
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    customers = list(db.customers.find({}, {'_id': 0, 'password': 0, 'cart': 0}))
    return jsonify(customers)

@app.route('/')
def home():
    return jsonify({'message': 'Bakery Management System API'})

if __name__ == '__main__':
    app.run(debug=True)