import os
# import sqlite3
import urllib.request
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import get_db_connection, init_db

app = Flask(__name__, static_folder=os.path.dirname(__file__), static_url_path='')
CORS(app)

init_db()

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')
def row_to_dict(row):
    return dict(row) if row else None
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json or {}
    user_id = data.get('userId')
    name = data.get('name', '').strip()
    password = data.get('password', '')
    role = data.get('role', '').strip()
    
    if not user_id or not name or not password or not role:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400
        
    try:
        user_id_int = int(user_id)
    except ValueError:
        return jsonify({'success': False, 'message': 'User ID must be a number.'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM User 
        WHERE UserID = ? AND Name = ? AND Password = ? AND Role = ?
    ''', (user_id_int, name, password, role))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            'success': True,
            'user': {
                'userId': user['UserID'],
                'name': user['Name'],
                'role': user['Role']
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials or role.'}), 401
@app.route('/api/products', methods=['GET'])
def get_products():
    q = request.args.get('q', '').strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    if q:
        cursor.execute('''
            SELECT * FROM Product 
            WHERE Name LIKE ? OR Description LIKE ?
        ''', (f'%{q}%', f'%{q}%'))
    else:
        cursor.execute('SELECT * FROM Product')
    products = [row_to_dict(p) for p in cursor.fetchall()]
    conn.close()
    return jsonify(products)
@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    price = data.get('price')
    stock_qty = data.get('stockQty')
    
    if not name or price is None or stock_qty is None:
        return jsonify({'message': 'Product name, price, and quantity are required.'}), 400
        
    try:
        price_val = float(price)
        qty_val = int(stock_qty)
        if price_val < 0 or qty_val < 0:
            raise ValueError()
    except ValueError:
        return jsonify({'message': 'Price and Stock Quantity must be non-negative numbers.'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Product (Name, Description, Price, StockQty)
        VALUES (?, ?, ?, ?)
    ''', (name, description, price_val, qty_val))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        'message': 'Product added successfully.',
        'productId': new_id
    }), 201
@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json or {}
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    price = data.get('price')
    stock_qty = data.get('stockQty')
    
    if not name or price is None or stock_qty is None:
        return jsonify({'message': 'Product name, price, and quantity are required.'}), 400
        
    try:
        price_val = float(price)
        qty_val = int(stock_qty)
        if price_val < 0 or qty_val < 0:
            raise ValueError()
    except ValueError:
        return jsonify({'message': 'Price and Stock Quantity must be non-negative numbers.'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT 1 FROM Product WHERE ProductID = ?', (product_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'message': 'Product not found.'}), 404
        
    cursor.execute('''
        UPDATE Product 
        SET Name = ?, Description = ?, Price = ?, StockQty = ?
        WHERE ProductID = ?
    ''', (name, description, price_val, qty_val, product_id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Product updated successfully.'})
@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT 1 FROM Product WHERE ProductID = ?', (product_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'message': 'Product not found.'}), 404
        
    cursor.execute('DELETE FROM Product WHERE ProductID = ?', (product_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Product deleted successfully.'})
@app.route('/api/customers', methods=['GET'])
def get_customers():
    phone = request.args.get('phone', '').strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    if phone:
        cursor.execute('''
            SELECT CustomerID AS id, Name AS name, PhoneNumber AS phoneNumber, LoyaltyPoints AS loyaltyPoints
            FROM Customerservice
            WHERE PhoneNumber LIKE ?
        ''', (f'{phone}%',))
    else:
        cursor.execute('''
            SELECT CustomerID AS id, Name AS name, PhoneNumber AS phoneNumber, LoyaltyPoints AS loyaltyPoints
            FROM Customerservice
        ''')
    customers = [row_to_dict(c) for c in cursor.fetchall()]
    conn.close()
    return jsonify(customers)
@app.route('/api/customers', methods=['POST'])
def add_customer():
    data = request.json or {}
    name = data.get('name', '').strip()
    phone = data.get('phoneNumber', '').strip()
    points = data.get('loyaltyPoints', 0)
    
    if not name or not phone:
        return jsonify({'message': 'Customer name and phone number are required.'}), 400
        
    try:
        points_val = int(points)
    except ValueError:
        return jsonify({'message': 'Loyalty points must be an integer.'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO Customerservice (Name, PhoneNumber, LoyaltyPoints)
            VALUES (?, ?, ?)
        ''', (name, phone, points_val))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return jsonify({
            'message': 'Customer added successfully.',
            'customerId': new_id
        }), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'message': 'A customer with this phone number already exists.'}), 409
@app.route('/api/customers/<string:phone>', methods=['DELETE'])
def delete_customer(phone):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT 1 FROM Customerservice WHERE PhoneNumber = ?', (phone,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'message': 'Customer not found.'}), 404
        
    cursor.execute('DELETE FROM Customerservice WHERE PhoneNumber = ?', (phone,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Customer deleted successfully.'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
