import sqlite3
import os
import sys
from datetime import datetime


def get_app_dir():
    """
    Returns the directory where persistent data (DB, receipts, assets) should live.
    - When running as a PyInstaller onefile EXE: directory containing the EXE
    - When running as a normal Python script: directory containing this script
    """
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        return os.path.dirname(sys.executable)
    else:
        # Running as normal Python script
        return os.path.dirname(os.path.abspath(__file__))


DB_FILE = os.path.join(get_app_dir(), 'restaurant.db')

def get_connection():
    """Returns a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row # To access columns by name
        # Enable foreign keys for SQLite
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        raise Exception(f"Database connection error: {e}")

def initialize_database():
    """Creates the database and all required tables if they do not exist.
    
    All schema is defined inline — no external SQL file is required.
    This makes the application fully self-contained when packaged as an EXE.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # --- Create tables ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS RestaurantSettings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                restaurant_name TEXT,
                address TEXT,
                phone TEXT,
                logo_path TEXT,
                default_delivery_charge REAL DEFAULT 0,
                default_service_charge REAL DEFAULT 0,
                custom_receipt_message TEXT DEFAULT ''
            )
        """)

        # --- Migrate existing RestaurantSettings table ---
        existing_cols = [r[1] for r in cursor.execute("PRAGMA table_info(RestaurantSettings)").fetchall()]
        if 'default_delivery_charge' not in existing_cols:
            cursor.execute("ALTER TABLE RestaurantSettings ADD COLUMN default_delivery_charge REAL DEFAULT 0")
        if 'default_service_charge' not in existing_cols:
            cursor.execute("ALTER TABLE RestaurantSettings ADD COLUMN default_service_charge REAL DEFAULT 0")
        if 'custom_receipt_message' not in existing_cols:
            cursor.execute("ALTER TABLE RestaurantSettings ADD COLUMN custom_receipt_message TEXT DEFAULT ''")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT UNIQUE,
                price REAL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT,
                phone TEXT,
                address TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Bills (
                bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                bill_date TEXT,
                bill_time TEXT,
                subtotal_amount REAL,
                delivery_charge REAL DEFAULT 0,
                service_charge REAL DEFAULT 0,
                total_amount REAL,
                FOREIGN KEY(customer_id) REFERENCES Customers(id) ON DELETE CASCADE
            )
        """)

        # --- Migrate existing Bills table ---
        bill_cols = [r[1] for r in cursor.execute("PRAGMA table_info(Bills)").fetchall()]
        if 'delivery_charge' not in bill_cols:
            cursor.execute("ALTER TABLE Bills ADD COLUMN delivery_charge REAL DEFAULT 0")
        if 'service_charge' not in bill_cols:
            cursor.execute("ALTER TABLE Bills ADD COLUMN service_charge REAL DEFAULT 0")
        if 'subtotal_amount' not in bill_cols:
            cursor.execute("ALTER TABLE Bills ADD COLUMN subtotal_amount REAL DEFAULT 0")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS BillItems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id INTEGER,
                item_name TEXT,
                price REAL,
                quantity INTEGER,
                subtotal REAL,
                FOREIGN KEY(bill_id) REFERENCES Bills(bill_id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS LastCleanup (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cleanup_date TEXT
            )
        """)

        # --- Seed default data on first run ---
        cursor.execute("SELECT COUNT(*) as count FROM LastCleanup")
        if cursor.fetchone()['count'] == 0:
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("INSERT INTO LastCleanup (cleanup_date) VALUES (?)", (today,))

        cursor.execute("SELECT COUNT(*) as count FROM RestaurantSettings")
        if cursor.fetchone()['count'] == 0:
            cursor.execute(
                "INSERT INTO RestaurantSettings (restaurant_name, address, phone, logo_path, default_delivery_charge, default_service_charge, custom_receipt_message) VALUES (?, ?, ?, ?, ?, ?, ?)",
                ("Restaurant Name", "Address", "Phone", "", 0.0, 0.0, "")
            )

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# --- Settings ---
def get_settings():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM RestaurantSettings ORDER BY id DESC LIMIT 1")
        return dict(cursor.fetchone() or {})
    finally:
        conn.close()

def save_settings(name, address, phone, logo_path, delivery_charge=0.0, service_charge=0.0, custom_receipt_message=""):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM RestaurantSettings")
        if cursor.fetchone()['count'] == 0:
            cursor.execute(
                "INSERT INTO RestaurantSettings (restaurant_name, address, phone, logo_path, default_delivery_charge, default_service_charge, custom_receipt_message) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (name, address, phone, logo_path, float(delivery_charge), float(service_charge), custom_receipt_message)
            )
        else:
            cursor.execute(
                "UPDATE RestaurantSettings SET restaurant_name=?, address=?, phone=?, logo_path=?, default_delivery_charge=?, default_service_charge=?, custom_receipt_message=?",
                (name, address, phone, logo_path, float(delivery_charge), float(service_charge), custom_receipt_message)
            )
        conn.commit()
    finally:
        conn.close()

# --- Menu ---
def get_menu_items():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Menu ORDER BY item_name")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def search_menu_items(query):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        search_pattern = f"%{query}%"
        cursor.execute("SELECT * FROM Menu WHERE item_name LIKE ? ORDER BY item_name", (search_pattern,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def add_menu_item(name, price):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Menu (item_name, price) VALUES (?, ?)", (name, float(price)))
        conn.commit()
        return True, "Item added successfully."
    except sqlite3.IntegrityError:
        return False, "Item already exists."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def update_menu_item(item_id, name, price):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE Menu SET item_name=?, price=? WHERE id=?", (name, float(price), item_id))
        conn.commit()
        return True, "Item updated successfully."
    except sqlite3.IntegrityError:
        return False, "Item name already exists."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def delete_menu_item(item_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Menu WHERE id=?", (item_id,))
        conn.commit()
        return True, "Item deleted successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

# --- Billing ---
def save_bill(customer_name, phone, address, items, subtotal_amount, delivery_charge=0.0, service_charge=0.0):
    """
    items is a list of dicts: [{'item_name': 'x', 'price': 100, 'quantity': 2, 'subtotal': 200}]
    Returns bill_id, bill_date, bill_time
    """
    total_amount = subtotal_amount + float(delivery_charge) + float(service_charge)
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # 1. Save customer
        cursor.execute(
            "INSERT INTO Customers (customer_name, phone, address) VALUES (?, ?, ?)",
            (customer_name, phone, address)
        )
        customer_id = cursor.lastrowid
        
        # 2. Save bill
        now = datetime.now()
        bill_date = now.strftime("%Y-%m-%d")
        bill_time = now.strftime("%I:%M %p")
        
        cursor.execute(
            "INSERT INTO Bills (customer_id, bill_date, bill_time, subtotal_amount, delivery_charge, service_charge, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (customer_id, bill_date, bill_time, subtotal_amount, float(delivery_charge), float(service_charge), total_amount)
        )
        bill_id = cursor.lastrowid
        
        # 3. Save bill items
        for item in items:
            cursor.execute(
                "INSERT INTO BillItems (bill_id, item_name, price, quantity, subtotal) VALUES (?, ?, ?, ?, ?)",
                (bill_id, item['item_name'], item['price'], item['quantity'], item['subtotal'])
            )
            
        conn.commit()
        return bill_id, bill_date, bill_time
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# --- History ---
def get_todays_bills():
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = '''
            SELECT b.bill_id, c.customer_name, b.bill_time, b.total_amount 
            FROM Bills b
            JOIN Customers c ON b.customer_id = c.id
            WHERE b.bill_date = ?
            ORDER BY b.bill_id DESC
        '''
        cursor.execute(query, (today,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def search_todays_bills(search_term):
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_connection()
    try:
        cursor = conn.cursor()
        search_pattern = f"%{search_term}%"
        query = '''
            SELECT b.bill_id, c.customer_name, b.bill_time, b.total_amount 
            FROM Bills b
            JOIN Customers c ON b.customer_id = c.id
            WHERE b.bill_date = ? AND (c.customer_name LIKE ? OR CAST(b.bill_id AS TEXT) LIKE ?)
            ORDER BY b.bill_id DESC
        '''
        cursor.execute(query, (today, search_pattern, search_pattern))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

def get_bill_details(bill_id):
    """Returns details for re-printing a receipt."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # Get bill and customer info
        cursor.execute('''
            SELECT b.bill_id, b.bill_date, b.bill_time, b.subtotal_amount,
                   b.delivery_charge, b.service_charge, b.total_amount, 
                   c.customer_name, c.phone, c.address
            FROM Bills b
            JOIN Customers c ON b.customer_id = c.id
            WHERE b.bill_id = ?
        ''', (bill_id,))
        bill_info = cursor.fetchone()
        
        if not bill_info:
            return None
            
        # Get bill items
        cursor.execute('''
            SELECT item_name, price, quantity, subtotal
            FROM BillItems
            WHERE bill_id = ?
        ''', (bill_id,))
        items = cursor.fetchall()
        
        return {
            'info': dict(bill_info),
            'items': [dict(row) for row in items]
        }
    finally:
        conn.close()
