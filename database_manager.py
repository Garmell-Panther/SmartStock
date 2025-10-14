# database_manager.py
import sqlite3
from sqlite3 import Error
from datetime import datetime

LOW_STOCK_THRESHOLD = 5

class DatabaseManager:
    def __init__(self, db_file="inventory.db"):
        self.db_file = db_file
        self.conn = None
        self._connect()
        self._setup_database()
        
    # -----------------------------
    # CONNECTION & SETUP
    # -----------------------------
    def _connect(self):
        """Creates a database connection to the SQLite database specified by db_file"""
        try:
            self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
            print("✅ Database connection established.")
        except Error as e:
            raise Exception(f"Failed to connect to SQLite database: {e}")

    def _setup_database(self):
        """Creates necessary tables and default users/items."""
        cursor = self.conn.cursor()
        
        # 1️⃣ Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL, 
                role TEXT NOT NULL
            );
        """)

        # 2️⃣ Inventory Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS InventoryItems (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL
            );
        """)

        # 3️⃣ Transactions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Transactions (
                id INTEGER PRIMARY KEY,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                transaction_type TEXT NOT NULL,
                date TEXT NOT NULL
            );
        """)

        # Default Users
        cursor.execute("SELECT COUNT(*) FROM Users")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO Users (username, password, role) VALUES (?, ?, ?)", ('admin', 'admin', 'admin'))
            cursor.execute("INSERT INTO Users (username, password, role) VALUES (?, ?, ?)", ('staff', 'staff', 'staff'))
            print("👤 Default 'admin' and 'staff' users created.")

        # Default Inventory
        cursor.execute("SELECT COUNT(*) FROM InventoryItems")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO InventoryItems (name, quantity, price) VALUES (?, ?, ?)", ('Laptop', 10, 999.99))
            print("💻 Default inventory item created.")
        
        self.conn.commit()
            
    # -----------------------------
    # LOGIN
    # -----------------------------
    def check_user_login(self, username, password):
        """Checks login credentials against the Users table."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT role FROM Users WHERE username = ? AND password = ?", (username, password))
        return cursor.fetchone()

    # -----------------------------
    # INVENTORY OPERATIONS
    # -----------------------------
    def get_all_items(self, search_term=None):
        """Retrieves all inventory items, optionally filtered by name."""
        try:
            cursor = self.conn.cursor()
            sql = "SELECT id, name, quantity, price FROM InventoryItems"
            params = []

            if search_term:
                sql += " WHERE name LIKE ?"
                params.append(f"%{search_term}%")

            sql += " ORDER BY id DESC"
            cursor.execute(sql, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error in get_all_items: {e}")
            return []

    def add_item(self, name, quantity, price):
        """Adds a new item to inventory."""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO InventoryItems (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))
        self.conn.commit()

    def update_item(self, item_id, name, quantity, price):
        """Updates an existing item by ID."""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE InventoryItems SET name=?, quantity=?, price=? WHERE id=?", (name, quantity, price, item_id))
        self.conn.commit()

    def delete_item(self, item_id):
        """Deletes an inventory item by ID."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM InventoryItems WHERE id=?", (item_id,))
        self.conn.commit()

    # -----------------------------
    # TRANSACTIONS
    # -----------------------------
    def record_transaction(self, item_name, quantity, price, transaction_type):
        """Records a sale or purchase transaction."""
        cursor = self.conn.cursor()
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO Transactions (item_name, quantity, price, transaction_type, date) VALUES (?, ?, ?, ?, ?)",
            (item_name, quantity, price, transaction_type, date_str)
        )
        self.conn.commit()

    def get_all_transactions(self, search_term=None):
        """Retrieves all transactions, optionally filtered by item name."""
        try:
            cursor = self.conn.cursor()
            sql = "SELECT id, item_name, quantity, price, transaction_type, date FROM Transactions"
            params = []

            if search_term:
                sql += " WHERE item_name LIKE ?"
                params.append(f"%{search_term}%")

            sql += " ORDER BY date DESC"
            cursor.execute(sql, params)
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error in get_all_transactions: {e}")
            return []

    # -----------------------------
    # CLOSE CONNECTION
    # -----------------------------
    def close(self):
        if self.conn:
            self.conn.close()
            print("🔒 Database connection closed.")
