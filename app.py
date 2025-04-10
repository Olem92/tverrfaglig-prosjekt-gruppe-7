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
        
        self.create_menu()
        self.create_main_interface()
        # Attempt to connect on startup
        self.attempt_connection()

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
        # Create main container 
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)  # Content area should expand

        # Top menu bar
        menu_bar = ttk.Frame(self.main_frame)
        menu_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Menu buttons i topp av program
        ttk.Button(menu_bar, text="Refresh", command=self.refresh_view).pack(side=tk.RIGHT, padx=2)
        ttk.Button(menu_bar, text="Orders", command=self.show_orders).pack(side=tk.LEFT, padx=2)
        ttk.Button(menu_bar, text="Inventory", command=self.show_inventory).pack(side=tk.LEFT, padx=2)        

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
        status_right = ttk.Label(status_frame, textvariable=self.connection_var)
        status_right.grid(row=0, column=0, sticky=(tk.E), padx=1)

    def attempt_connection(self):
        try:
            self.db.connect()
            self.connection_var.set("Successfully connected to varehusdb")
        except Exception as e:
            self.connection_var.set("Not connected")
            messagebox.showerror("Connection Error", f"Failed to connect to database: {str(e)}")

    def show_orders(self):
        messagebox.showinfo("Orders", "Orders view not implemented yet")

    def show_inventory(self):
        messagebox.showinfo("Inventory", "Inventory view not implemented yet")    

    def refresh_view(self):
        messagebox.showinfo("Refresh", "Refresh functionality not implemented yet")

    def start(self):
        print("Starting the app")
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()