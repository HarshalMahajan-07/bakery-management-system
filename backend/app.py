from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['bakery_db']

# Placeholder endpoints
@app.route('/')
def home():
    return jsonify({'message': 'Bakery Management System API'})

# Products CRUD
@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'GET':
        products = list(db.products.find({}, {'_id': 0}))
        return jsonify(products)
    elif request.method == 'POST':
        data = request.json
        db.products.insert_one(data)
        return jsonify({'message': 'Product added'}), 201

# Orders CRUD
@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if request.method == 'GET':
        orders = list(db.orders.find({}, {'_id': 0}))
        return jsonify(orders)
    elif request.method == 'POST':
        data = request.json
        db.orders.insert_one(data)
        return jsonify({'message': 'Order added'}), 201

# Customers CRUD
@app.route('/customers', methods=['GET', 'POST'])
def customers():
    if request.method == 'GET':
        customers = list(db.customers.find({}, {'_id': 0}))
        return jsonify(customers)
    elif request.method == 'POST':
        data = request.json
        db.customers.insert_one(data)
        return jsonify({'message': 'Customer added'}), 201

if __name__ == '__main__':
    app.run(debug=True)