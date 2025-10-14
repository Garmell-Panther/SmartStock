# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import atexit
from database_manager import DatabaseManager
from app_ui import InventoryApp, center_window

# --- Global Font & Colors ---
FONT_MAIN = ("Segoe UI", 10)
COLOR_APP_BG = "#f4f6f8"
COLOR_CARD_BG = "#ffffff"
COLOR_HEADER = "#0078D7"

# -------------------------------
# Initialize Database
# -------------------------------
db_manager = None
try:
    db_manager = DatabaseManager()
except Exception as e:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Initialization Error", f"Could not connect to database: {e}")
    root.destroy()
    exit()

# Ensure DB closes when program exits
atexit.register(lambda: db_manager.close() if db_manager else None)


# -------------------------------
# LOGIN WINDOW
# -------------------------------
def login_window():
    login = tk.Tk()
    login.title("🔐 SmartStock Login")
    center_window(login, 420, 420)
    login.configure(bg=COLOR_APP_BG)
    login.resizable(False, False)

    # Modern theme
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TEntry", padding=5, relief="flat", font=FONT_MAIN)
    style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8, relief="flat", background=COLOR_HEADER, foreground="white")
    style.map("TButton", background=[("active", "#005FA3")])

    # --- Header Section ---
    header = tk.Label(
        login,
        text="🧠 SmartStock Inventory",
        font=("Segoe UI Semibold", 18),
        bg=COLOR_APP_BG,
        fg=COLOR_HEADER
    )
    header.pack(pady=(30, 10))

    tk.Label(
        login,
        text="Sign in to continue",
        bg=COLOR_APP_BG,
        fg="#6c757d",
        font=("Segoe UI", 10)
    ).pack()

    # --- Login Card ---
    frame_login = tk.Frame(login, bg=COLOR_CARD_BG, bd=1, relief=tk.FLAT)
    frame_login.pack(pady=20, padx=30, fill="x")
    frame_login.configure(highlightbackground="#dcdcdc", highlightthickness=1)

    # Username
    tk.Label(frame_login, text="👤 Username", bg=COLOR_CARD_BG, font=FONT_MAIN).pack(pady=(15, 0))
    entry_user = ttk.Entry(frame_login, width=30)
    entry_user.pack(pady=(0, 10), padx=10)

    # Password
    tk.Label(frame_login, text="🔒 Password", bg=COLOR_CARD_BG, font=FONT_MAIN).pack(pady=(5, 0))
    entry_pass = ttk.Entry(frame_login, show="*", width=30)
    entry_pass.pack(pady=(0, 15), padx=10)

    # --- Button & Event ---
    def check_login():
        username = entry_user.get().strip()
        password = entry_pass.get().strip()

        # Validate credentials
        user = db_manager.check_user_login(username, password)
        if user:
            role = user[0]
            login.destroy()
            app = InventoryApp(db_manager, role)
            app.mainloop()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password. Please try again.")

    login.bind("<Return>", lambda e: check_login())

    ttk.Button(frame_login, text="Login", command=check_login, style="TButton").pack(pady=10)

    # Footer
    tk.Label(
        login,
        text="(Admin or Staff Access Only)",
        bg=COLOR_APP_BG,
        fg="#868e96",
        font=("Segoe UI", 9, "italic")
    ).pack(pady=(0, 10))

    login.mainloop()


# -------------------------------
# Run Program
# -------------------------------
if __name__ == "__main__":
    login_window()

