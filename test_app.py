import unittest
import json
import os
import sqlite3
from app import app
import database
class GiftPointTestCase(unittest.TestCase):
    def setUp(self):
        self.test_db_path = os.path.join(os.path.dirname(__file__), 'test_inventory.db')
        database.DB_PATH = self.test_db_path
        
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        cursor.execute('DROP TABLE IF EXISTS OrderItem')
        cursor.execute('DROP TABLE IF EXISTS Orders')
        cursor.execute('DROP TABLE IF EXISTS Customerservice')
        cursor.execute('DROP TABLE IF EXISTS Product')
        cursor.execute('DROP TABLE IF EXISTS User')
        conn.commit()
        conn.close()
        
        database.init_db()
        
        app.config['TESTING'] = True
        self.client = app.test_client()
    def tearDown(self):
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except PermissionError:
                pass
    def test_login_success(self):
        response = self.client.post('/api/auth/login', json={
            'userId': 241462,
            'name': 'Aruj',
            'password': 'aruj123',
            'role': 'employee'
        })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['user']['name'], 'Aruj')
        self.assertEqual(data['user']['role'], 'employee')
    def test_login_failure(self):
        response = self.client.post('/api/auth/login', json={
            'userId': 241462,
            'name': 'Aruj',
            'password': 'wrongpassword',
            'role': 'employee'
        })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 401)
        self.assertFalse(data['success'])
    def test_create_product(self):
        response = self.client.post('/api/products', json={
            'name': 'Glitter Glue Set',
            'description': 'Pack of 6 metallic colors',
            'price': 220.0,
            'stockQty': 30
        })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('productId', data)
        self.assertEqual(data['message'], 'Product added successfully.')
        conn = database.get_db_connection()
        prod = conn.execute('SELECT * FROM Product WHERE ProductID = ?', (data['productId'],)).fetchone()
        conn.close()
        self.assertIsNotNone(prod)
        self.assertEqual(prod['Name'], 'Glitter Glue Set')
        self.assertEqual(prod['Price'], 220.0)
        self.assertEqual(prod['StockQty'], 30)
    def test_read_products(self):
        response = self.client.get('/api/products')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        response_search = self.client.get('/api/products?q=Notebook')
        data_search = json.loads(response_search.data)
        self.assertEqual(response_search.status_code, 200)
        for item in data_search:
            self.assertIn('Notebook', item['Name'])
    def test_update_product(self):
        response = self.client.put('/api/products/1', json={
            'name': 'Premium Notebook - Upgraded',
            'description': 'A5, 150 pages, leather finish cover',
            'price': 320.0,
            'stockQty': 60
        })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Product updated successfully.')
        conn = database.get_db_connection()
        prod = conn.execute('SELECT * FROM Product WHERE ProductID = 1').fetchone()
        conn.close()
        self.assertEqual(prod['Name'], 'Premium Notebook - Upgraded')
        self.assertEqual(prod['Price'], 320.0)
        self.assertEqual(prod['StockQty'], 60)
    def test_delete_product(self):
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Product (Name, Price, StockQty) VALUES ('Temp Pen', 10.0, 10)")
        conn.commit()
        temp_id = cursor.lastrowid
        conn.close()
        response = self.client.delete(f'/api/products/{temp_id}')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['message'], 'Product deleted successfully.')
        conn = database.get_db_connection()
        prod = conn.execute('SELECT * FROM Product WHERE ProductID = ?', (temp_id,)).fetchone()
        conn.close()
        self.assertIsNone(prod)
    def test_create_customer(self):
        response = self.client.post('/api/customers', json={
            'name': 'Harry Thompson',
            'phoneNumber': '0894567890',
            'loyaltyPoints': 10
        })
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('customerId', data)
        conn = database.get_db_connection()
        cust = conn.execute('SELECT * FROM Customerservice WHERE PhoneNumber = "0894567890"').fetchone()
        conn.close()
        self.assertIsNotNone(cust)
        self.assertEqual(cust['Name'], 'Harry Thompson')
    def test_delete_customer(self):
        self.client.post('/api/customers', json={
            'name': 'Grace Wilson',
            'phoneNumber': '0835556677',
            'loyaltyPoints': 0
        })
        
        response = self.client.delete('/api/customers/0835556677')
        self.assertEqual(response.status_code, 200)
        conn = database.get_db_connection()
        cust = conn.execute('SELECT * FROM Customerservice WHERE PhoneNumber = "0835556677"').fetchone()
        conn.close()
        self.assertIsNone(cust)
    def test_checkout_integration_flow(self):
        
        response = self.client.post('/api/orders', json={
            'userId': 241462,
            'customerId': 1,
            'cartItems': [
                {
                    'productId': 1,
                    'quantity': 2
                }
            ]
        })
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['success'])
        self.assertIn('orderId', data)
        self.assertAlmostEqual(data['totalAmount'], 1.66, places=2)
        conn = database.get_db_connection()
        
        prod = conn.execute('SELECT StockQty FROM Product WHERE ProductID = 1').fetchone()
        self.assertEqual(prod['StockQty'], 43)
        
        cust = conn.execute('SELECT LoyaltyPoints FROM Customerservice WHERE CustomerID = 1').fetchone()
        self.assertEqual(cust['LoyaltyPoints'], 16)
        
        order = conn.execute('SELECT * FROM Orders WHERE OrderID = ?', (data['orderId'],)).fetchone()
        self.assertIsNotNone(order)
        self.assertEqual(order['UserID'], 241462)
        self.assertEqual(order['CustomerID'], 1)
        self.assertAlmostEqual(order['TotalAmount'], 1.66, places=2)
        
        order_item = conn.execute('SELECT * FROM OrderItem WHERE OrderID = ? AND ProductID = 1', (data['orderId'],)).fetchone()
        self.assertIsNotNone(order_item)
        self.assertEqual(order_item['Quantity'], 2)
        self.assertEqual(order_item['UnitPrice'], 0.83)
        
        conn.close()
if __name__ == '__main__':
    unittest.main()
