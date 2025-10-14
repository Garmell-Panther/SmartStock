# app_ui.py
import tkinter as tk
from tkinter import ttk, messagebox
from database_manager import DatabaseManager
import locale

# -------------------------------
# DEFAULT STYLE AND SETTINGS
# -------------------------------
FONT_MAIN = ("Segoe UI", 10)
COLOR_APP_BG = "#f4f6f8"
COLOR_FRAME_BG = "#ffffff"

COLOR_HEADER_BG = "#0078D7"
COLOR_HEADER_TEXT = "#ffffff"

COLOR_BUTTON_ADD = "#28a745"
COLOR_BUTTON_UPDATE = "#007bff"
COLOR_BUTTON_DELETE = "#dc3545"

LOW_STOCK_THRESHOLD = 5

# Set locale for currency formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_PH.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'C')
    except locale.Error:
        pass



def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    window.geometry(f'{width}x{height}+{int(x)}+{int(y)}')


class InventoryApp(tk.Tk):
    def __init__(self, db_manager: DatabaseManager, role: str):
        super().__init__()
        self.db = db_manager
        self.role = role
        self.selected_item_id = None

        self.title(f"SmartStock - Inventory Management ({self.role.upper()})")
        center_window(self, 1100, 700)
        self.configure(bg=COLOR_APP_BG)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self._configure_styles()

        self._create_header()
        self._create_widgets()
        self._create_status_bar()
        self.load_inventory()

    # ---------------------------
    # STYLE CONFIGURATION
    # ---------------------------
    def _configure_styles(self):
        self.style.configure(".", font=FONT_MAIN)

        # Treeview
        self.style.configure(
            "Treeview",
            background="#F9FAFB",
            foreground="#2E2E2E",
            rowheight=28,
            fieldbackground="#F9FAFB",
            bordercolor="#E0E0E0",
            borderwidth=1
        )
        self.style.configure(
            "Treeview.Heading",
            background="#0078D7",
            foreground="white",
            font=("Segoe UI Semibold", 10)
        )
        self.style.map(
            "Treeview",
            background=[("selected", "#0078D7")],
            foreground=[("selected", "white")]
        )

        # Buttons
        button_common = {
            "font": ("Segoe UI", 10, "bold"),
            "padding": 6,
            "relief": "flat",
        }

        self.style.configure("Add.TButton", background=COLOR_BUTTON_ADD, foreground="white", **button_common)
        self.style.configure("Update.TButton", background=COLOR_BUTTON_UPDATE, foreground="white", **button_common)
        self.style.configure("Delete.TButton", background=COLOR_BUTTON_DELETE, foreground="white", **button_common)

        # Hover effects
        self.style.map("Add.TButton", background=[("active", "#218838")])
        self.style.map("Update.TButton", background=[("active", "#0069d9")])
        self.style.map("Delete.TButton", background=[("active", "#c82333")])

    # ---------------------------
    # HEADER BAR
    # ---------------------------
    def _create_header(self):
        header = tk.Frame(self, bg=COLOR_HEADER_BG, height=60)
        header.pack(fill="x")

        tk.Label(
            header,
            text="SmartStock Inventory System",
            bg=COLOR_HEADER_BG,
            fg=COLOR_HEADER_TEXT,
            font=("Segoe UI Semibold", 14)
        ).pack(side="left", padx=20, pady=10)

        tk.Label(
            header,
            text=f"Logged in as: {self.role.upper()}",
            bg=COLOR_HEADER_BG,
            fg="#E3F2FD",
            font=("Segoe UI", 10, "italic")
        ).pack(side="right", padx=20)

    # ---------------------------
    # MAIN LAYOUT / WIDGETS
    # ---------------------------
    def _create_widgets(self):
        # 🔍 Search bar
        search_frame = tk.Frame(self, bg=COLOR_APP_BG)
        search_frame.pack(fill="x", padx=20, pady=(10, 5))

        tk.Label(search_frame, text="Search Item:", bg=COLOR_APP_BG, font=FONT_MAIN).pack(side="left", padx=(0, 8))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=(0, 10))
        ttk.Button(search_frame, text="Search", command=self.search_items, style="Update.TButton").pack(side="left")
        ttk.Button(search_frame, text="Reset", command=self.load_inventory, style="Delete.TButton").pack(side="left", padx=(5, 0))

        # Input frame
        frame_input = tk.Frame(self, bg=COLOR_FRAME_BG, padx=15, pady=15)
        frame_input.pack(fill="x", padx=20, pady=(10, 8))

        labels = ["Name:", "Quantity:", "Price:"]
        self.entries = {}
        for i, text in enumerate(labels):
            tk.Label(frame_input, text=text, bg=COLOR_FRAME_BG, font=FONT_MAIN).grid(
                row=0, column=i * 2, padx=(10, 5), pady=5, sticky="w"
            )
            entry = ttk.Entry(frame_input, width=15, font=FONT_MAIN)
            entry.grid(row=0, column=i * 2 + 1, padx=(0, 15), pady=5, sticky="ew")
            self.entries[text.split(":")[0].lower()] = entry

        # Buttons
        frame_buttons = tk.Frame(frame_input, bg=COLOR_FRAME_BG)
        frame_buttons.grid(row=0, column=6, rowspan=2, padx=10, sticky="nsew")

        ttk.Button(frame_buttons, text="Add", style="Add.TButton",
                   command=self.add_item_ui,
                   state=tk.NORMAL if self.role == "admin" else tk.DISABLED).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_buttons, text="Update", style="Update.TButton",
                   command=self.update_item_ui,
                   state=tk.NORMAL if self.role == "admin" else tk.DISABLED).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_buttons, text="Delete", style="Delete.TButton",
                   command=self.delete_item_ui,
                   state=tk.NORMAL if self.role == "admin" else tk.DISABLED).pack(side=tk.LEFT, padx=5)

        # Inventory Table
        frame_inventory = tk.Frame(self, bg=COLOR_FRAME_BG, padx=20, pady=15)
        frame_inventory.pack(fill="both", expand=True, padx=20, pady=(5, 15))

        scrollbar = ttk.Scrollbar(frame_inventory, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.inventory_tree = ttk.Treeview(
            frame_inventory,
            columns=("ID", "Name", "Quantity", "Price"),
            show="headings",
            yscrollcommand=scrollbar.set,
        )
        self.inventory_tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.inventory_tree.yview)

        self.inventory_tree.heading("ID", text="ID", anchor="center")
        self.inventory_tree.heading("Name", text="Item Name")
        self.inventory_tree.heading("Quantity", text="Qty.", anchor="center")
        self.inventory_tree.heading("Price", text="Price", anchor="e")

        self.inventory_tree.column("ID", width=60, anchor="center")
        self.inventory_tree.column("Name", width=350, stretch=tk.YES)
        self.inventory_tree.column("Quantity", width=100, anchor="center")
        self.inventory_tree.column("Price", width=150, anchor="e")

        # Row tag styles
        self.inventory_tree.tag_configure("low_stock", background="#FFF3CD")  # light yellow for low stock
        self.inventory_tree.bind("<<TreeviewSelect>>", self.item_selected)

    # ---------------------------
    # SEARCH FEATURE
    # ---------------------------
    def search_items(self):
        term = self.search_var.get().strip()
        self.load_inventory(search_term=term)

    # ---------------------------
    # STATUS BAR (non-blocking messages)
    # ---------------------------
    def _create_status_bar(self):
        self.status_var = tk.StringVar(value="Ready.")
        self.status_bar = tk.Label(self, textvariable=self.status_var, bg="#E9ECEF", fg="#333", anchor="w", padx=10)
        self.status_bar.pack(fill="x", side="bottom")

    def set_status(self, message):
        self.status_var.set(message)
        self.after(2500, lambda: self.status_var.set("Ready."))

    # ---------------------------
    # EVENT HANDLERS
    # ---------------------------
    def item_selected(self, event):
        selected_item = self.inventory_tree.focus()
        if selected_item:
            values = self.inventory_tree.item(selected_item, "values")
            for entry in self.entries.values():
                entry.delete(0, tk.END)
            self.entries["name"].insert(0, values[1])
            self.entries["quantity"].insert(0, values[2])
            raw_price = values[3].lstrip("₱").replace(",", "")
            self.entries["price"].insert(0, raw_price)
            self.selected_item_id = values[0]
        else:
            self.selected_item_id = None

    # ---------------------------
    # LOAD INVENTORY
    # ---------------------------
    def load_inventory(self, search_term=None):
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        try:
            items = self.db.get_all_items(search_term)
            for item in items:
                quantity = item[2]
                row_tags = ("low_stock",) if quantity <= LOW_STOCK_THRESHOLD else ()
                formatted_price = locale.currency(item[3], grouping=True, symbol="₱")
                self.inventory_tree.insert("", tk.END, values=(item[0], item[1], item[2], formatted_price), tags=row_tags)
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not load inventory: {e}")

    # ---------------------------
    # VALIDATION
    # ---------------------------
    def _validate_input(self, qty_str: str, price_str: str):
        qty_str = qty_str.strip()
        price_str = price_str.strip().replace(',', '')

        if not qty_str:
            raise ValueError("Quantity cannot be empty.")
        if not qty_str.isdigit():
            raise ValueError("Quantity must be a whole number.")
        quantity = int(qty_str)
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        if not price_str:
            raise ValueError("Price cannot be empty.")
        try:
            price = float(price_str)
        except ValueError:
            raise ValueError("Price must be numeric.")
        if price < 0:
            raise ValueError("Price cannot be negative.")

        return quantity, price

    # ---------------------------
    # CRUD OPERATIONS
    # ---------------------------
    def add_item_ui(self):
        name = self.entries["name"].get().strip()
        qty_str = self.entries["quantity"].get().strip()
        price_str = self.entries["price"].get().strip()

        if not name:
            messagebox.showerror("Input Error", "Item Name cannot be empty.")
            return

        try:
            quantity, price = self._validate_input(qty_str, price_str)
            self.db.add_item(name, quantity, price)
            self.load_inventory()
            self.set_status(f"✅ '{name}' added successfully.")
            for entry in self.entries.values():
                entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_item_ui(self):
        if self.selected_item_id is None:
            messagebox.showwarning("Selection Error", "Please select an item to update.")
            return

        name = self.entries["name"].get().strip()
        qty_str = self.entries["quantity"].get().strip()
        price_str = self.entries["price"].get().strip()

        try:
            quantity, price = self._validate_input(qty_str, price_str)
            self.db.update_item(self.selected_item_id, name, quantity, price)
            self.load_inventory()
            self.set_status(f"✅ Item ID {self.selected_item_id} updated.")
            for entry in self.entries.values():
                entry.delete(0, tk.END)
            self.selected_item_id = None
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_item_ui(self):
        if self.selected_item_id is None:
            messagebox.showwarning("Selection Error", "Please select an item to delete.")
            return

        item_name = self.entries["name"].get()
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{item_name}'?"):
            try:
                self.db.delete_item(self.selected_item_id)
                self.load_inventory()
                self.set_status(f"🗑️ '{item_name}' deleted.")
                for entry in self.entries.values():
                    entry.delete(0, tk.END)
                self.selected_item_id = None
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to delete item: {e}")

    # ---------------------------
    # EXIT HANDLER
    # ---------------------------
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit SmartStock?"):
            self.destroy()


# ---------------------------
# MAIN RUNNER (For Testing)
# ---------------------------
if __name__ == "__main__":
    db = DatabaseManager()
    app = InventoryApp(db, role="admin")
    app.mainloop()
