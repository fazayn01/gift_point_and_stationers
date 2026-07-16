import sqlite3
import os
from datetime import datetime, timedelta
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'inventory.db')
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS User (
        UserID INTEGER PRIMARY KEY,
        Name TEXT NOT NULL,
        Password TEXT NOT NULL,
        Role TEXT NOT NULL CHECK(Role IN ('admin', 'employee', 'owner'))
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Product (
        ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Description TEXT,
        Price REAL NOT NULL,
        StockQty INTEGER NOT NULL
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Customerservice (
        CustomerID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        PhoneNumber TEXT UNIQUE NOT NULL,
        LoyaltyPoints INTEGER DEFAULT 0
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Orders (
        OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER NOT NULL,
        CustomerID INTEGER,
        TotalAmount REAL NOT NULL,
        OrderDate TEXT NOT NULL,
        FOREIGN KEY(UserID) REFERENCES User(UserID),
        FOREIGN KEY(CustomerID) REFERENCES Customerservice(CustomerID)
    );
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS OrderItem (
        OrderID INTEGER NOT NULL,
        ProductID INTEGER NOT NULL,
        Quantity INTEGER NOT NULL,
        UnitPrice REAL NOT NULL,
        PRIMARY KEY (OrderID, ProductID),
        FOREIGN KEY(OrderID) REFERENCES Orders(OrderID) ON DELETE CASCADE,
        FOREIGN KEY(ProductID) REFERENCES Product(ProductID)
    );
    ''')
    
    conn.commit()
    seed_data(conn)
    conn.close()
def seed_data(conn):
    cursor = conn.cursor()
    
    users = [
        (1, 'Admin', 'admin123', 'admin'),
        (241462, 'Aruj', 'aruj123', 'employee'),
        (3, 'Owner', 'owner123', 'owner')
    ]
    cursor.executemany('''
    INSERT OR IGNORE INTO User (UserID, Name, Password, Role) 
    VALUES (?, ?, ?, ?);
    ''', users)
    
    products = [
        (1, 'Premium Notebook', 'A5 spiral bound, 120 pages, rule-lined', 0.83, 45),
        (2, 'Luxury Gel Pens', 'Pack of 5, fine-point black gel ink', 1.16, 95),
        (3, 'Wrapping Paper', 'Floral pattern wrapping sheet (large)', 0.20, 150),
        (4, 'Gift Box Set', 'Decorative cardboard gift boxes, set of 3', 2.81, 20),
        (5, 'Art Sketchbook', 'A4 drawing pad, 150gsm cartridge paper', 2.15, 15),
        (6, 'Pencil Case', 'Zippered canvas pencil case, blue color', 0.59, 60),
        (7, 'Fountain Pen', 'Classic metal fountain pen with ink converter', 3.96, 10),
        (8, 'Sticky Notes Pack', '4 pastel colors, 100 sheets each', 0.46, 120)
    ]
    
    cursor.execute("SELECT COUNT(*) FROM Product")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO Product (ProductID, Name, Description, Price, StockQty) 
        VALUES (?, ?, ?, ?, ?);
        ''', products)
        
    customers = [
        (1, 'John Smith', '0851234567', 15),
        (2, 'Emily Carter', '0872345678', 45),
        (3, 'Oliver Bennett', '0863456789', 5)
    ]
    cursor.execute("SELECT COUNT(*) FROM Customerservice")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
        INSERT INTO Customerservice (CustomerID, Name, PhoneNumber, LoyaltyPoints) 
        VALUES (?, ?, ?, ?);
        ''', customers)
        
    cursor.execute("SELECT COUNT(*) FROM Orders")
    if cursor.fetchone()[0] == 0:
        order_date_1 = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
        INSERT INTO Orders (OrderID, UserID, CustomerID, TotalAmount, OrderDate)
        VALUES (1001, 241462, 2, 4.79, ?);
        ''', (order_date_1,))
        cursor.execute('''
        INSERT INTO OrderItem (OrderID, ProductID, Quantity, UnitPrice)
        VALUES (1001, 7, 1, 3.96);
        ''', )
        cursor.execute('''
        INSERT INTO OrderItem (OrderID, ProductID, Quantity, UnitPrice)
        VALUES (1001, 1, 1, 0.83);
        ''')
        
        order_date_2 = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
        INSERT INTO Orders (OrderID, UserID, CustomerID, TotalAmount, OrderDate)
        VALUES (1002, 241462, 3, 1.75, ?);
        ''', (order_date_2,))
        cursor.execute('''
        INSERT INTO OrderItem (OrderID, ProductID, Quantity, UnitPrice)
        VALUES (1002, 1, 1, 0.83);
        ''')
        cursor.execute('''
        INSERT INTO OrderItem (OrderID, ProductID, Quantity, UnitPrice)
        VALUES (1002, 8, 2, 0.46);
        ''')
        
    conn.commit()
if __name__ == '__main__':
    init_db()
    print("Database initialized successfully at:", DB_PATH)
