from database import VarehusDatabase
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

class App:
    def __init__(self):
        self.db = VarehusDatabase()
        self.root = tk.Tk()
        self.root.title("Varehus Overview")
        self.root.geometry("800x600")
        
        # Add keyboard event bindings
        self.root.bind('<Key>', self.handle_keypress)  # Bind all keypresses

        self.create_menu()
        self.create_main_interface()
        # Attempt to connect on startup
        self.attempt_connection()

    def handle_keypress(self, event):
        # F5 = Refresh
        if event.keysym == 'F5':
            self.refresh_view()
        
        # Ctrl+O = Orders
        elif event.keysym.lower() == 'o' and (event.state & 0x0004):  # 0x0004 = Control key
            self.show_orders()
        
        # Ctrl+I = Inventory
        elif event.keysym.lower() == 'i' and (event.state & 0x0004):
            self.show_inventory()
        
        return 'break'  # Stop event propagation

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Reconnect to Database", command=self.attempt_connection)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

    def create_main_interface(self):

        # Set current view to None (used for refresh function)
        self.current_view = None

        # Create main container 
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)  # Content area should expand

        # Top menu bar grid
        menu_bar = ttk.Frame(self.main_frame)
        menu_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Menu buttons left
        ttk.Button(menu_bar, text="Home", command=self.reload_app).pack(side=tk.LEFT, padx=2)
        ttk.Button(menu_bar, text="Orders", command=self.show_orders).pack(side=tk.LEFT, padx=2)
        ttk.Button(menu_bar, text="Inventory", command=self.show_inventory).pack(side=tk.LEFT, padx=2)
        
        # Menu buttons right
        ttk.Button(menu_bar, text="Refresh", command=self.refresh_view).pack(side=tk.RIGHT, padx=2)
        
        # Main content area
        self.content = ttk.Frame(self.main_frame)
        self.content.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Default welcome content
        welcome_label = ttk.Label(self.content, text="Welcome to Varehus System")
        welcome_label.pack(pady=20)
        style = ttk.Style()
        style.configure("Welcome.TLabel", font=('Helvetica', 16))
        welcome_label.configure(style="Welcome.TLabel")
        
        ttk.Label(self.content, text="Click Orders to view all orders").pack()

        # Status bar (connection info only)
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)

        # Connection status
        self.connection_var = tk.StringVar(value="Not connected")
        self.status_label = ttk.Label(status_frame, textvariable=self.connection_var)
        self.status_label.grid(row=0, column=0, sticky=(tk.E), padx=1)

        # Connection style
        style.configure("Connected.TLabel", foreground="green")
        style.configure("Disconnected.TLabel", foreground="red")

    def attempt_connection(self):
        try:
            self.db.connect()

            # Try a ping to confirm the connection is actually alive
            self.db.connection.ping(reconnect=True)

            self.connection_var.set("Successfully connected to varehusdb")
            self.status_label.configure(style="Connected.TLabel")
        except Exception as e:
            self.connection_var.set("Not connected")
            self.status_label.configure(style="Disconnected.TLabel")
            messagebox.showerror("Connection Error", f"Failed to connect to database: {str(e)}")

    def reload_app(self):
        # Clear existing content
        for widget in self.content.winfo_children():
          widget.destroy()

        # Recreate the main interface
        self.create_main_interface()

        # Attempt to reconnect to the database
        self.attempt_connection()

    def show_orders(self):
        # Clear existing content
        for widget in self.content.winfo_children():
            widget.destroy()

        # Set current view to orders
        self.current_view = "orders"

        # Create frame for Treeview
        tree_frame = ttk.Frame(self.content)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create Treeview with scrollbar
        tree = ttk.Treeview(tree_frame)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Pack the Treeview and scrollbar
        tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        try:
            # Get inventory data
            orders_data = self.db.get_orders()
            
            if not orders_data:
                ttk.Label(tree_frame, text="No inventory data available").pack()
                return

            # Set up columns based on the first row of data
            columns = list(orders_data[0].keys())
            tree["columns"] = columns
            
            # Configure the columns
            tree.column("#0", width=0, stretch=tk.NO)  # Hide the first empty column
            for col in columns:
                tree.column(col, anchor=tk.CENTER, width=100)
                tree.heading(col, text=col.title(), anchor=tk.CENTER)

            # Insert the data
            for item in orders_data:
                values = [item[col] for col in columns]
                tree.insert("", tk.END, values=values)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load orders: {str(e)}")

    def show_inventory(self):
        # Clear existing content
        for widget in self.content.winfo_children():
            widget.destroy()

        # Set current view to inventory
        self.current_view = "inventory"

        # Create frame for Treeview
        tree_frame = ttk.Frame(self.content)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create Treeview with scrollbar
        tree = ttk.Treeview(tree_frame)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Pack the Treeview and scrollbar
        tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        try:
            # Get inventory data
            inventory_data = self.db.get_inventory()
            
            if not inventory_data:
                ttk.Label(tree_frame, text="No inventory data available").pack()
                return

            # Set up columns based on the first row of data
            columns = list(inventory_data[0].keys())
            tree["columns"] = columns
            
            # Configure the columns
            tree.column("#0", width=0, stretch=tk.NO)  # Hide the first empty column
            for col in columns:
                tree.column(col, anchor=tk.CENTER, width=100)
                tree.heading(col, text=col.title(), anchor=tk.CENTER)

            # Insert the data
            for item in inventory_data:
                values = [item[col] for col in columns]
                tree.insert("", tk.END, values=values)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory: {str(e)}")

    def refresh_view(self):
        if self.current_view == "orders":  # <--- Added to check current view
            self.show_orders()  # Refresh orders view
        elif self.current_view == "inventory":  # <--- Added to check current view
            self.show_inventory()  # Refresh inventory view
        else:
            messagebox.showinfo("Refresh", "No active view to refresh.")  # <--- Added to handle no active view

    def start(self):
        print("Starting the app")
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()