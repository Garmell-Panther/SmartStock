import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import random # Used for mock data generation

# --- GLOBAL CURRENCY SETTING ---
DISPLAY_CURRENCY = "₱" # Options: "₱" (Pesos) or "$" (Dollars)
# -------------------------------

# --- GLOBAL STYLE COLORS ---
COLOR_MAIN_BG = "#f9f9f9"
COLOR_ACCENT = "#3498DB"
COLOR_BUTTON_ADD = "#4CAF50"
COLOR_BUTTON_SALES = "#2ecc71"
COLOR_BUTTON_PURCHASE = "#F39C12"
COLOR_BUTTON_TRANSACT = "#1ABC9C" # New color for transaction buttons
# -----------------------------

# -------------------------------
# Database Connection and Setup (UPDATED WITH SALES/PURCHASES TABLES)
# -------------------------------
try:
    conn = sqlite3.connect("smartstock.db")
    cursor = conn.cursor()
except Exception as e:
    messagebox.showerror("Database Error", f"Could not connect to database: {e}")
    exit()

# Create necessary tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    quantity INTEGER,
    price REAL
)
""")

# NEW: Sales Transactions Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    quantity_sold INTEGER,
    total_price REAL,
    sale_date TEXT,
    FOREIGN KEY(product_id) REFERENCES products(id)
)
""")

# NEW: Purchases Transactions Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    quantity_bought INTEGER,
    total_cost REAL,
    purchase_date TEXT,
    FOREIGN KEY(product_id) REFERENCES products(id)
)
""")

# Insert default user data
cursor.execute("SELECT COUNT(*) FROM users")
if cursor.fetchone()[0] == 0:
    cursor.executemany(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        [('admin', 'admin123', 'admin'), ('staff', 'staff123', 'staff')]
    )

# Insert mock data for products, sales, and purchases
cursor.execute("SELECT COUNT(*) FROM products")
if cursor.fetchone()[0] < 20:
    cursor.executemany(
        "INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)",
        [ # --- General Groceries ---
            ('Milk Carton', 150, 85.00), 
            ('Bread Loaf', 200, 50.00), 
            ('Eggs Dozen', 100, 120.00),
            ('Coffee Jar', 75, 250.00), 
            ('Sugar Sack (kg)', 40, 75.00),
            ('Bottled Water (L)', 300, 35.00),
            ('Cooking Oil (L)', 80, 150.50), 
            ('Rice (kg)', 50, 60.00), 
            ('Potato Chips (Large)', 90, 88.75), 
            ('Shampoo Bottle', 65, 180.00),
            
            # --- Baking Items ---
            ('All-Purpose Flour (kg)', 120, 95.00), 
            ('Baking Powder (small)', 70, 30.00),
            ('Vanilla Extract (oz)', 55, 110.00), 
            ('Chocolate Chips (bag)', 85, 145.00),
            ('Brown Sugar (box)', 90, 85.00), 
            ('Dry Yeast (packets)', 150, 20.00), 

            # --- Herbs & Spices ---
            ('Dried Basil (jar)', 45, 75.00), 
            ('Ground Cinnamon (can)', 60, 92.50), 
            ('Dried Oregano (bag)', 40, 65.00), 
            ('Black Pepper Corns', 50, 130.00),
            ('Paprika (can)', 35, 105.00), 
            ('Bay Leaves (bag)', 30, 55.00), 
            ]
    )

# Mock sales data (if empty)
cursor.execute("SELECT COUNT(*) FROM sales")
if cursor.fetchone()[0] == 0:
    today = datetime.date.today().strftime("%Y-%m-%d")
    cursor.executemany(
        "INSERT INTO sales (product_id, quantity_sold, total_price, sale_date) VALUES (?, ?, ?, ?)",
        [(1, 10, 850.00, today), (2, 25, 1250.00, today), (1, 5, 425.00, today)]
    )

# Mock purchases data (if empty)
cursor.execute("SELECT COUNT(*) FROM purchases")
if cursor.fetchone()[0] == 0:
    last_week = (datetime.date.today() - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    cursor.executemany(
        "INSERT INTO purchases (product_id, quantity_bought, total_cost, purchase_date) VALUES (?, ?, ?, ?)",
        [(1, 100, 5000.00, last_week), (3, 50, 4500.00, last_week)]
    )

conn.commit()
# -------------------------------


# -------------------------------
# REPORT DATA FUNCTIONS (Unchanged)
# -------------------------------
def get_sales_summary(period='day'):
    """Calculates total sales and number of transactions for the specified period."""
    today = datetime.date.today().strftime("%Y-%m-%d")
    
    if period == 'day':
        query = "SELECT SUM(total_price), COUNT(id) FROM sales WHERE sale_date = ?"
        cursor.execute(query, (today,))
    else: # defaults to 'all-time'
        query = "SELECT SUM(total_price), COUNT(id) FROM sales"
        cursor.execute(query)

    total_sales, transaction_count = cursor.fetchone()
    return {
        'total_sales': total_sales if total_sales else 0.00,
        'transactions': transaction_count if transaction_count else 0,
        'period_name': "Today's" if period == 'day' else "All-Time"
    }

def get_purchases_summary(period='month'):
    """Calculates total purchase cost and number of orders for the specified period."""
    # Simplified to get total for demonstration
    
    if period == 'month':
        # In a real app, this would filter by date range. We'll use all-time for simplicity here.
        query = "SELECT SUM(total_cost), COUNT(id) FROM purchases"
        cursor.execute(query)
    else: # defaults to 'all-time'
        query = "SELECT SUM(total_cost), COUNT(id) FROM purchases"
        cursor.execute(query)
    
    total_cost, order_count = cursor.fetchone()
    return {
        'total_cost': total_cost if total_cost else 0.00,
        'orders': order_count if order_count else 0,
        'period_name': "Total"
    }

# -------------------------------
# HELPER FUNCTION: CENTER WINDOW (Unchanged)
# -------------------------------
def center_window(window, width, height):
    """Calculates and sets the window's position to center it on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')


# -------------------------------
# REPORTS WINDOW (Unchanged)
# -------------------------------
def reports_window(parent):
    report_win = tk.Toplevel(parent)
    report_win.title("Reports Dashboard")
    center_window(report_win, 600, 450)
    report_win.configure(bg=COLOR_MAIN_BG)
    report_win.grab_set() # Modal window

    tk.Label(report_win, text="Reports Dashboard", font=("Segoe UI", 18, "bold"),
             bg=COLOR_MAIN_BG, fg="#333").pack(pady=15)

    frame_reports = tk.Frame(report_win, bg=COLOR_MAIN_BG)
    frame_reports.pack(padx=20, pady=10, fill='x')

    def create_report_card(parent_frame, title, data, bg_color, detail_action=None):
        card = tk.Frame(parent_frame, bg="white", padx=15, pady=15, bd=1, relief=tk.RAISED)
        card.pack(side=tk.LEFT, padx=10, expand=True, fill='both')

        # Title
        tk.Label(card, text=title, font=("Segoe UI", 12, "bold"), bg="white", fg="#333").pack(pady=5)
        tk.Frame(card, height=2, bg=bg_color).pack(fill='x', pady=5)
        
        # Data Labels
        for key, value in data.items():
            display_value = f"{DISPLAY_CURRENCY}{value:,.2f}" if 'total' in key or 'cost' in key else value
            
            # Format key for display
            display_key = key.replace('_', ' ').title()
            if key == 'period_name':
                continue # Skip period name here

            tk.Label(card, text=f"{display_key}: {display_value}", 
                     font=("Segoe UI", 10), bg="white", fg="#666", anchor='w').pack(fill='x', pady=2)

        # Detail Button
        if detail_action:
            tk.Button(card, text="View Details", bg=bg_color, fg="white", 
                      width=15, command=detail_action).pack(pady=10)

    # --- Sales Report Card ---
    sales_data = get_sales_summary(period='day')
    sales_title = f"Daily Sales Summary ({sales_data['period_name']})"
    
    create_report_card(
        frame_reports,
        sales_title,
        sales_data,
        COLOR_BUTTON_SALES,
        lambda: messagebox.showinfo("Sales Detail", "Detailed Sales Data Grid (Coming Soon)")
    )

    # --- Purchases Report Card ---
    purchases_data = get_purchases_summary(period='month')
    purchases_title = f"{purchases_data['period_name']} Purchases Summary"
    
    create_report_card(
        frame_reports,
        purchases_title,
        purchases_data,
        COLOR_BUTTON_PURCHASE,
        lambda: messagebox.showinfo("Purchase Detail", "Detailed Purchase Order List (Coming Soon)")
    )

# -------------------------------
# NEW: TRANSACTION FUNCTIONS
# -------------------------------
def record_sale(product_id, quantity_sold, price, transaction_window, refresh_callback):
    """Records a sale, decreases inventory, and closes the transaction window."""
    try:
        quantity_sold = int(quantity_sold)
        sale_price = float(price) # The price per unit at sale time

        if quantity_sold <= 0:
            messagebox.showwarning("Input Error", "Quantity sold must be greater than zero.")
            return

        # 1. Get current product details
        cursor.execute("SELECT name, quantity, price FROM products WHERE id=?", (product_id,))
        product = cursor.fetchone()
        if not product:
            messagebox.showerror("Error", "Product not found.")
            return

        product_name, current_quantity, current_price = product
        
        if quantity_sold > current_quantity:
            messagebox.showwarning("Inventory Error", f"Cannot sell {quantity_sold} units. Only {current_quantity} in stock.")
            return

        # 2. Update Inventory (Decrease Quantity)
        new_quantity = current_quantity - quantity_sold
        cursor.execute("UPDATE products SET quantity=? WHERE id=?", (new_quantity, product_id))

        # 3. Record Sale Transaction
        total_price = quantity_sold * sale_price
        sale_date = datetime.date.today().strftime("%Y-%m-%d")
        cursor.execute(
            "INSERT INTO sales (product_id, quantity_sold, total_price, sale_date) VALUES (?, ?, ?, ?)",
            (product_id, quantity_sold, total_price, sale_date)
        )
        
        conn.commit()
        messagebox.showinfo("Success", f"Sale of {quantity_sold}x {product_name} recorded. Total: {DISPLAY_CURRENCY}{total_price:,.2f}")
        refresh_callback() # Refresh the main inventory table
        transaction_window.destroy()

    except ValueError:
        messagebox.showerror("Input Error", "Quantity and Price must be valid numbers.")
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

def record_purchase(product_id, quantity_bought, unit_cost, transaction_window, refresh_callback):
    """Records a purchase (stocking), increases inventory, and closes the transaction window."""
    try:
        quantity_bought = int(quantity_bought)
        unit_cost = float(unit_cost)

        if quantity_bought <= 0 or unit_cost <= 0:
            messagebox.showwarning("Input Error", "Quantity and Unit Cost must be greater than zero.")
            return

        # 1. Get current product details
        cursor.execute("SELECT name, quantity FROM products WHERE id=?", (product_id,))
        product = cursor.fetchone()
        if not product:
            messagebox.showerror("Error", "Product not found.")
            return

        product_name, current_quantity = product

        # 2. Update Inventory (Increase Quantity)
        new_quantity = current_quantity + quantity_bought
        cursor.execute("UPDATE products SET quantity=? WHERE id=?", (new_quantity, product_id))
        
        # 3. Record Purchase Transaction
        total_cost = quantity_bought * unit_cost
        purchase_date = datetime.date.today().strftime("%Y-%m-%d")
        cursor.execute(
            "INSERT INTO purchases (product_id, quantity_bought, total_cost, purchase_date) VALUES (?, ?, ?, ?)",
            (product_id, quantity_bought, total_cost, purchase_date)
        )
        
        conn.commit()
        messagebox.showinfo("Success", f"Purchase of {quantity_bought}x {product_name} recorded. Total Cost: {DISPLAY_CURRENCY}{total_cost:,.2f}")
        refresh_callback() # Refresh the main inventory table
        transaction_window.destroy()

    except ValueError:
        messagebox.showerror("Input Error", "Quantity and Unit Cost must be valid numbers.")
    except Exception as e:
        messagebox.showerror("Database Error", str(e))


# -------------------------------
# NEW: TRANSACTION WINDOWS
# -------------------------------
def sales_transaction_window(parent, product_details, refresh_callback):
    """Creates a modal window to record a sale for a selected product."""
    product_id, name, quantity, price_str = product_details

    sale_win = tk.Toplevel(parent)
    sale_win.title(f"Record Sale: {name}")
    center_window(sale_win, 450, 300)
    sale_win.configure(bg=COLOR_MAIN_BG)
    sale_win.grab_set()

    current_price = float(price_str.replace(DISPLAY_CURRENCY, '').replace(',', '').strip())

    tk.Label(sale_win, text=f"Record Sale: {name}", font=("Segoe UI", 14, "bold"), bg=COLOR_MAIN_BG).pack(pady=10)
    
    # Frame for inputs
    frame = tk.Frame(sale_win, bg=COLOR_MAIN_BG)
    frame.pack(pady=10, padx=20)
    
    # Current Stock/Price
    tk.Label(frame, text=f"Current Stock: {quantity}", bg=COLOR_MAIN_BG, fg="#333").grid(row=0, column=0, columnspan=2, pady=5)
    tk.Label(frame, text=f"Sale Price (per unit): {price_str}", bg=COLOR_MAIN_BG, fg="#333").grid(row=1, column=0, columnspan=2, pady=5)
    
    # Quantity Input
    tk.Label(frame, text="Quantity Sold:", bg=COLOR_MAIN_BG).grid(row=2, column=0, sticky="e", pady=10)
    entry_quantity = tk.Entry(frame, width=15, justify='center')
    entry_quantity.insert(0, "1")
    entry_quantity.grid(row=2, column=1, sticky="w", padx=5, pady=10)
    
    # Unit Price Input (User can override default price)
    tk.Label(frame, text=f"Unit Price ({DISPLAY_CURRENCY}):", bg=COLOR_MAIN_BG).grid(row=3, column=0, sticky="e", pady=5)
    entry_price = tk.Entry(frame, width=15, justify='center')
    entry_price.insert(0, f"{current_price:.2f}")
    entry_price.grid(row=3, column=1, sticky="w", padx=5, pady=5)

    # Record Button
    tk.Button(sale_win, text="Confirm Sale", bg=COLOR_BUTTON_SALES, fg="white", width=20, 
              command=lambda: record_sale(product_id, entry_quantity.get(), entry_price.get(), sale_win, refresh_callback)
    ).pack(pady=20)

def purchase_transaction_window(parent, product_details, refresh_callback):
    """Creates a modal window to record a purchase/restock for a selected product."""
    product_id, name, quantity, price_str = product_details

    purchase_win = tk.Toplevel(parent)
    purchase_win.title(f"Record Purchase: {name}")
    center_window(purchase_win, 450, 300)
    purchase_win.configure(bg=COLOR_MAIN_BG)
    purchase_win.grab_set()

    current_price = float(price_str.replace(DISPLAY_CURRENCY, '').replace(',', '').strip())

    tk.Label(purchase_win, text=f"Record Purchase/Restock: {name}", font=("Segoe UI", 14, "bold"), bg=COLOR_MAIN_BG).pack(pady=10)
    
    # Frame for inputs
    frame = tk.Frame(purchase_win, bg=COLOR_MAIN_BG)
    frame.pack(pady=10, padx=20)
    
    # Current Stock/Price
    tk.Label(frame, text=f"Current Stock: {quantity}", bg=COLOR_MAIN_BG, fg="#333").grid(row=0, column=0, columnspan=2, pady=5)
    tk.Label(frame, text=f"Last Sale Price (Unit): {price_str}", bg=COLOR_MAIN_BG, fg="#333").grid(row=1, column=0, columnspan=2, pady=5)
    
    # Quantity Input
    tk.Label(frame, text="Quantity Bought:", bg=COLOR_MAIN_BG).grid(row=2, column=0, sticky="e", pady=10)
    entry_quantity = tk.Entry(frame, width=15, justify='center')
    entry_quantity.insert(0, "10")
    entry_quantity.grid(row=2, column=1, sticky="w", padx=5, pady=10)
    
    # Unit Cost Input (Cost to us, not sale price)
    tk.Label(frame, text=f"Unit Cost ({DISPLAY_CURRENCY}):", bg=COLOR_MAIN_BG).grid(row=3, column=0, sticky="e", pady=5)
    entry_cost = tk.Entry(frame, width=15, justify='center')
    entry_cost.insert(0, f"{current_price * 0.7:.2f}") # Mocking a 30% margin
    entry_cost.grid(row=3, column=1, sticky="w", padx=5, pady=5)

    # Record Button
    tk.Button(purchase_win, text="Confirm Purchase", bg=COLOR_BUTTON_PURCHASE, fg="white", width=20, 
              command=lambda: record_purchase(product_id, entry_quantity.get(), entry_cost.get(), purchase_win, refresh_callback)
    ).pack(pady=20)


# -------------------------------
# LOGIN WINDOW (Unchanged)
# -------------------------------
def login_window():
    login = tk.Tk()
    login.title("SmartStock Login")
    window_width = 400
    window_height = 400
    center_window(login, window_width, window_height)
    login.configure(bg="#f2f2f2")

    tk.Label(login, text="SmartStock System", font=("Segoe UI", 16, "bold"),
             bg="#f2f2f2", fg="#2b2b2b").pack(pady=30)

    tk.Label(login, text="Username:", bg="#f2f2f2").pack(pady=5)
    entry_user = tk.Entry(login, width=30)
    entry_user.pack()

    tk.Label(login, text="Password:", bg="#f2f2f2").pack(pady=5)
    entry_pass = tk.Entry(login, show="*", width=30)
    entry_pass.pack()

    def check_login():
        username = entry_user.get().strip()
        password = entry_pass.get().strip()
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return

        cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            role = user[0]
            login.destroy()
            open_inventory_window(role)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    tk.Button(login, text="Login", bg="#4CAF50", fg="white", width=20, command=check_login).pack(pady=15)
    tk.Label(login, text="(Admin or Staff Access Only)", bg="#f2f2f2", fg="#666").pack()

    login.mainloop()


# -------------------------------
# INVENTORY WINDOW (MAIN APPLICATION)
# -------------------------------
def open_inventory_window(role):
    root = tk.Tk()
    root.title(f"🛒 SmartStock Inventory System ({role.capitalize()})")
    
    window_width = 1000 # Increased width
    window_height = 650 
    center_window(root, window_width, window_height)
    
    root.configure(bg=COLOR_MAIN_BG)

    tk.Label(root, text="SmartStock Inventory System", font=("Segoe UI", 18, "bold"),
             bg=COLOR_MAIN_BG, fg="#333").pack(pady=10)

    # --- Frame for Inputs ---
    frame_inputs = tk.Frame(root, bg=COLOR_MAIN_BG)
    frame_inputs.pack(pady=5)
    
    # ... (Input fields and grid layout remain the same) ...

    tk.Label(frame_inputs, text="Product Name:", bg=COLOR_MAIN_BG).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_name = tk.Entry(frame_inputs, width=25)
    entry_name.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_inputs, text="Quantity:", bg=COLOR_MAIN_BG).grid(row=0, column=2, padx=5, pady=5, sticky="e")
    
    # Quantity Entry and +/- Buttons Frame
    frame_quantity = tk.Frame(frame_inputs, bg=COLOR_MAIN_BG)
    frame_quantity.grid(row=0, column=3, padx=5, pady=5, sticky="w")
    entry_quantity = tk.Entry(frame_quantity, width=8, justify='center')
    entry_quantity.pack(side=tk.LEFT, padx=(0, 2))

    def adjust_quantity(delta):
        try:
            current_q = int(entry_quantity.get() or 0)
            new_q = current_q + delta
            if new_q < 0:
                messagebox.showwarning("Input Error", "Quantity cannot go below zero.")
                return
            entry_quantity.delete(0, tk.END)
            entry_quantity.insert(0, str(new_q))
        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be a number.")

    tk.Button(frame_quantity, text="+", command=lambda: adjust_quantity(1), 
              width=3, bg="#4CAF50", fg="white", font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT, padx=1)
    tk.Button(frame_quantity, text="-", command=lambda: adjust_quantity(-1), 
              width=3, bg="#E74C3C", fg="white", font=("Segoe UI", 8, "bold")).pack(side=tk.LEFT, padx=1)
    
    tk.Label(frame_inputs, text=f"Price ({DISPLAY_CURRENCY}):", bg=COLOR_MAIN_BG).grid(row=0, column=4, padx=5, pady=5, sticky="e")
    entry_price = tk.Entry(frame_inputs, width=10)
    entry_price.grid(row=0, column=5, padx=5, pady=5)

    tk.Label(frame_inputs, text="Search:", bg=COLOR_MAIN_BG).grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_search = tk.Entry(frame_inputs, width=25)
    entry_search.grid(row=1, column=1, padx=5, pady=5)
    tk.Button(frame_inputs, text="Search", bg=COLOR_ACCENT, fg="white", width=10, command=lambda: refresh_table(search=True)).grid(row=1, column=2, padx=5)


    # --- Functions (add_product, update_product, delete_product, refresh_table, on_tree_select remain the same) ---
    def add_product():
        name = entry_name.get().strip()
        quantity = entry_quantity.get().strip()
        price = entry_price.get().strip()
        if not (name and quantity and price):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return
        try:
            quantity_val = int(quantity)
            price_val = float(price)
            if quantity_val < 0 or price_val < 0:
                messagebox.showwarning("Input Error", "Quantity and price must be positive.")
                return
            cursor.execute("INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)",
                           (name, quantity_val, price_val))
            conn.commit()
            refresh_table()
            messagebox.showinfo("Success", f"Product '{name}' added.")
            entry_name.delete(0, tk.END)
            entry_quantity.delete(0, tk.END)
            entry_price.delete(0, tk.END)
            entry_name.focus()
        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be a whole number and Price must be a number.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_product():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a product to update.")
            return
        pid = tree.item(selected)['values'][0]
        name = entry_name.get().strip()
        quantity = entry_quantity.get().strip()
        price = entry_price.get().strip()
        if not (name and quantity and price):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return
        try:
            quantity_val = int(quantity)
            price_val = float(price)
            if quantity_val < 0 or price_val < 0:
                messagebox.showwarning("Input Error", "Quantity and price must be positive.")
                return
            cursor.execute("UPDATE products SET name=?, quantity=?, price=? WHERE id=?",
                           (name, quantity_val, price_val, pid))
            conn.commit()
            refresh_table()
            messagebox.showinfo("Success", f"Product ID {pid} updated.")
            entry_name.delete(0, tk.END)
            entry_quantity.delete(0, tk.END)
            entry_price.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be a whole number and Price must be a number.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_product():
        if role != "admin":
            messagebox.showwarning("Access Denied", "Only Admin can delete products.")
            return
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a product to delete.")
            return
        pid = tree.item(selected)['values'][0]
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete Product ID {pid}?")
        if confirm:
            try:
                cursor.execute("DELETE FROM products WHERE id=?", (pid,))
                conn.commit()
                refresh_table()
                entry_name.delete(0, tk.END)
                entry_quantity.delete(0, tk.END)
                entry_price.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def refresh_table(search=False):
        for row in tree.get_children():
            tree.delete(row)

        search_term = entry_search.get().strip()
        query = "SELECT * FROM products"
        params = []

        if search_term:
            query += " WHERE name LIKE ?"
            params.append('%' + search_term + '%')
            
        cursor.execute(query, tuple(params))

        for row in cursor.fetchall():
            product_id, name, quantity, price = row
            formatted_price = f"{DISPLAY_CURRENCY}{price:,.2f}"
            tree.insert("", tk.END, values=(product_id, name, quantity, formatted_price))
            
        if search and not search_term:
            entry_search.delete(0, tk.END)

    def on_tree_select(event):
        selected = tree.selection()
        if selected:
            values = tree.item(selected)['values']
            
            price_str = str(values[3]).replace(DISPLAY_CURRENCY, '').replace(',', '').strip()
            
            entry_name.delete(0, tk.END)
            entry_name.insert(0, values[1])
            entry_quantity.delete(0, tk.END)
            entry_quantity.insert(0, values[2])
            entry_price.delete(0, tk.END)
            entry_price.insert(0, price_str)
            
    # NEW: Function to open transaction window for selected item
    def open_sale_transaction():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a product to record a sale.")
            return
        product_details = tree.item(selected)['values']
        sales_transaction_window(root, product_details, refresh_table)

    def open_purchase_transaction():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a product to record a purchase/restock.")
            return
        
        # --- FIX AREA ---
        values = tree.item(selected)['values']
        # Convert the formatted price string back to a clean number string
        raw_price_str = str(values[3]).replace(DISPLAY_CURRENCY, '').replace(',', '').strip()
        # Pass the ID, Name, Quantity, and the raw price string
        product_details = (values[0], values[1], values[2], raw_price_str)


    # --- Buttons (Updated to include transaction buttons) ---
    frame_buttons = tk.Frame(root, bg=COLOR_MAIN_BG)
    frame_buttons.pack(pady=5)

    # 1. Product Management Buttons
    tk.Button(frame_buttons, text="Add Product", bg=COLOR_BUTTON_ADD, fg="white", width=15, command=add_product).grid(row=0, column=0, padx=5)
    tk.Button(frame_buttons, text="Update Product", bg="#F39C12", fg="white", width=15, command=update_product).grid(row=0, column=1, padx=5)

    delete_btn = tk.Button(frame_buttons, text="Delete Product", bg="#E74C3C", fg="white", width=15, command=delete_product)
    delete_btn.grid(row=0, column=2, padx=5)
    if role != "admin":
        delete_btn.config(state=tk.DISABLED, bg="#ccc", fg="#666")

    tk.Button(frame_buttons, text="Refresh Table", bg=COLOR_ACCENT, fg="white", width=15, command=refresh_table).grid(row=0, column=3, padx=5)
    
    # 2. Transaction Buttons
    frame_transactions = tk.Frame(root, bg=COLOR_MAIN_BG)
    frame_transactions.pack(pady=10)
    
    tk.Label(frame_transactions, text="Record Transactions:", bg=COLOR_MAIN_BG, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=10)
    
    tk.Button(frame_transactions, text="⬇️ Record Sale", bg=COLOR_BUTTON_SALES, fg="white", width=15, 
              command=open_sale_transaction).pack(side=tk.LEFT, padx=5)
    
    tk.Button(frame_transactions, text="⬆️ Record Purchase", bg=COLOR_BUTTON_PURCHASE, fg="white", width=15, 
              command=open_purchase_transaction).pack(side=tk.LEFT, padx=5)

    # 3. Reports Button
    tk.Button(frame_transactions, text="📊 View Reports", bg="#8e44ad", fg="white", width=15, 
              command=lambda: reports_window(root)).pack(side=tk.LEFT, padx=15)


    # --- Table ---
    columns = ("ID", "Name", "Quantity", f"Price ({DISPLAY_CURRENCY})")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=15) # Increased height
    for col in columns:
        tree.heading(col, text=col)
        if col.startswith("Price"):
            tree.column(col, anchor="e", width=150)
        elif col == "Quantity":
            tree.column(col, anchor="center", width=100)
        else:
            tree.column(col, anchor="w", width=200 if col == "Name" else 100)

    tree.bind("<<TreeviewSelect>>", on_tree_select)

    # Scrollbar
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(pady=10, fill="x", padx=10)

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
    style.configure("Treeview", font=("Segoe UI", 10))

    refresh_table()

    # Handle window close safely
    def on_close():
        conn.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


# -------------------------------
# Start Program
# -------------------------------
if __name__ == "__main__":
    login_window()
