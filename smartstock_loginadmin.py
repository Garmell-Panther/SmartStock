import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

# -------------------------------
# Database Connection
# -------------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",      # your MySQL password if you have one
    database="smartstock"
)
cursor = conn.cursor()

# -------------------------------
# LOGIN WINDOW
# -------------------------------
def login_window():
    login = tk.Tk()
    login.title("SmartStock Login")
    login.geometry("400x500")
    login.configure(bg="#f2f2f2")

    # --- Load Logo ---
    
    try:
        image_path = r"C:\Users\Zed\Documents\SmartStock\logo.png"
        # Use __file__ to get script directory
        image_path = os.path.join(os.path.dirname(__file__), "logo.png")
        logo = Image.open(image_path)
        logo = logo.resize((150, 150))
        logo_img = ImageTk.PhotoImage(logo)

        # Display image
        label_logo = tk.Label(login, image=logo_img, bg="#f2f2f2")
        label_logo.pack(pady=15)

        # Keep a reference to prevent garbage collection
        label_logo.image = logo_img
    except Exception as e:
        tk.Label(login, text="SmartStock System", font=("Segoe UI", 16, "bold"),
                 bg="#f2f2f2", fg="#2b2b2b").pack(pady=10)
        print("⚠️ Image load error:", e)


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

        cursor.execute("SELECT role FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()

        if user:
            role = user[0]
            messagebox.showinfo("Login Success", f"Welcome, {role.capitalize()} {username}!")
            login.destroy()
            open_inventory_window(role)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    tk.Button(login, text="Login", bg="#4CAF50", fg="white", width=20, command=check_login).pack(pady=15)
    tk.Label(login, text="(Admin or Staff Access Only)", bg="#f2f2f2", fg="#666").pack()

    login.mainloop()

# -------------------------------
# INVENTORY WINDOW
# -------------------------------
def open_inventory_window(role):
    root = tk.Tk()
    root.title(f"🛒 SmartStock Inventory System ({role})")
    root.geometry("750x500")
    root.configure(bg="#f9f9f9")

    tk.Label(root, text="SmartStock Inventory System", font=("Segoe UI", 18, "bold"), bg="#f9f9f9", fg="#333").pack(pady=10)

    # --- Frame for Inputs ---
    frame_inputs = tk.Frame(root, bg="#f9f9f9")
    frame_inputs.pack(pady=5)

    tk.Label(frame_inputs, text="Product Name:", bg="#f9f9f9").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_name = tk.Entry(frame_inputs, width=25)
    entry_name.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_inputs, text="Quantity:", bg="#f9f9f9").grid(row=0, column=2, padx=5, pady=5, sticky="e")
    entry_quantity = tk.Entry(frame_inputs, width=10)
    entry_quantity.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(frame_inputs, text="Price:", bg="#f9f9f9").grid(row=0, column=4, padx=5, pady=5, sticky="e")
    entry_price = tk.Entry(frame_inputs, width=10)
    entry_price.grid(row=0, column=5, padx=5, pady=5)

    # --- Functions ---
    def add_product():
        name = entry_name.get().strip()
        quantity = entry_quantity.get().strip()
        price = entry_price.get().strip()
        if not (name and quantity and price):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return
        try:
            cursor.execute("INSERT INTO products (name, quantity, price) VALUES (%s, %s, %s)",
                           (name, int(quantity), float(price)))
            conn.commit()
            refresh_table()
            messagebox.showinfo("Success", f"Product '{name}' added.")
            entry_name.delete(0, tk.END)
            entry_quantity.delete(0, tk.END)
            entry_price.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute("SELECT * FROM products")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

    def delete_product():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a product to delete.")
            return
        pid = tree.item(selected)['values'][0]
        confirm = messagebox.askyesno("Confirm", "Delete this product?")
        if confirm:
            cursor.execute("DELETE FROM products WHERE id=%s", (pid,))
            conn.commit()
            refresh_table()

    # --- Buttons ---
    frame_buttons = tk.Frame(root, bg="#f9f9f9")
    frame_buttons.pack(pady=5)

    tk.Button(frame_buttons, text="Add Product", bg="#4CAF50", fg="white", width=15, command=add_product).grid(row=0, column=0, padx=5)
    tk.Button(frame_buttons, text="Delete Product", bg="#E74C3C", fg="white", width=15, command=delete_product).grid(row=0, column=1, padx=5)
    tk.Button(frame_buttons, text="Refresh Table", bg="#3498DB", fg="white", width=15, command=refresh_table).grid(row=0, column=2, padx=5)

    # --- Table ---
    columns = ("ID", "Name", "Quantity", "Price")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=12)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=150)
    tree.pack(pady=10, fill="x")

    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
    style.configure("Treeview", font=("Segoe UI", 10))

    refresh_table()
    root.mainloop()

# -------------------------------
# Start Program
# -------------------------------
login_window()

# Close DB connection
cursor.close()
conn.close()
