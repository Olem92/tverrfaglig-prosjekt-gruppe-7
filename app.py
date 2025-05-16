from database import VarehusDatabase
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os, subprocess, sys, webbrowser
from views.orders_view import OrdersView
from views.inventory_view import InventoryView
from views.contacts_view import ContactsView

class App:
    def __init__(self):
        # Start FastAPI slik at WebApp-fungerer
        self.api_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api:app", "--reload"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        ## Initaliserer GUI-vinduer, med satt størrelse
        self.db = VarehusDatabase()
        self.root = tk.Tk()
        self.root.title("Warehouse Mini ERP System")
        self.root.geometry("1000x800")
        self.orders_view = OrdersView(self)             ## De forskjellige views innad i app
        self.inventory_view = InventoryView(self)       ## De forskjellige views innad i app
        self.contacts_view = ContactsView(self)         ## De forskjellige views innad i app
        self.popups = []  # Track all popup windows, slik man programmet selv har kontroll på hva som er åpent, og derav også kan lukke.
        
        # Add keyboard event bindings
        self.root.bind('<Key>', self.handle_keypress)  # Bind all keypresses

        self.create_menu()
        self.create_main_interface()
        
        # Attempt to connect on startup
        self.attempt_connection()
        
        # Ensure proper cleanup on window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Ensure CMD+Q and other quit events also call on_close (macOS compatibility), slik at prosess med WebGUI lukkes og port frigjøres
        self.root.quit = self.on_close

    ## Del-funksjon som muliggjør close-windows
    def register_popup(self, win):
        self.popups.append(win)
        win.transient(self.root)
        win.focus_set()
        win.lift()
        win.protocol("WM_DELETE_WINDOW", lambda w=win: self._close_popup(w))

    ## Close Windows fra X
    def _close_popup(self, win):
        if win in self.popups:
            self.popups.remove(win)
        win.destroy()

    ## Close Windows fra File menu
    def close_all_popups(self):
        for win in self.popups[:]:
            try:
                win.destroy()
            except Exception:
                pass
        self.popups.clear()

    ## Litt shortcuts!
    def handle_keypress(self, event):
        # F5 or Ctrl + R = Refresh
        if event.keysym == 'F5' or event.keysym.lower() == 'r' and (event.state & 0x0004):
            self.refresh_view()
        
        # Ctrl+O = Orders
        elif event.keysym.lower() == 'o' and (event.state & 0x0004):  # 0x0004 = Control key
            self.show_orders()
        
        # Ctrl+I = Inventory
        elif event.keysym.lower() == 'i' and (event.state & 0x0004):
            self.show_inventory()
        
        return 'break'  # Stop key handling

    ## File menu i topp
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Reconnect to Database", command=self.attempt_connection)
        file_menu.add_command(label="Close All Popups", command=self.close_all_popups)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)

    ## "Homepage"
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
        home_img = Image.open(os.path.join(os.path.dirname(__file__), "icons", "home.png")).convert("RGBA").resize((18, 18), Image.LANCZOS)
        refresh_img = Image.open(os.path.join(os.path.dirname(__file__), "icons", "refresh.png")).convert("RGBA").resize((18, 18), Image.LANCZOS)
        home_icon = ImageTk.PhotoImage(home_img)
        refresh_icon = ImageTk.PhotoImage(refresh_img)

        ## Knapper i topp av GUI, brukes for navigering mellom views
        # Menu buttons left
        home_btn = ttk.Button(menu_bar, image=home_icon, command=self.reload_app)
        home_btn.pack(side=tk.LEFT, padx=6, pady=4, ipadx=4, ipady=2)

        ttk.Button(menu_bar, text="Orders", command=self.show_orders).pack(side=tk.LEFT, padx=2)
        ttk.Button(menu_bar, text="Inventory", command=self.show_inventory).pack(side=tk.LEFT, padx=2)
        ttk.Button(menu_bar, text="Contacts", command=self.show_contacts).pack(side=tk.LEFT, padx=2)
        
        # Menu buttons right
        refresh_btn = ttk.Button(menu_bar, image=refresh_icon, command=self.refresh_view)
        refresh_btn.pack(side=tk.RIGHT, padx=6, pady=4, ipadx=4, ipady=2)
        
        # Store references to icons to prevent garbage collection
        self.home_icon = home_icon
        self.refresh_icon = refresh_icon
        
        # Main content area
        self.content = ttk.Frame(self.main_frame)
        self.content.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Center the main window on the screen
        self.center_window()
        
        # Default welcome content
        welcome_label = ttk.Label(self.content, text="Welcome to Warehouse Mini ERP System")
        welcome_label.pack(pady=20)
        style = ttk.Style()
        style.configure("Welcome.TLabel", font=('Helvetica', 16))
        welcome_label.configure(style="Welcome.TLabel")
        
        # Knapp for å åpne WebGUI kjapt uten å huske porter...
        open_web_btn = ttk.Button(self.content, text="Open Web App", command=self.open_web_app)
        open_web_btn.pack(pady=10)

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

    ## Funksjon for å sette vindu i center
    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")


## Funksjon som muliggjør info i høyre-hjørne
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

## Funksjon for å reload app, som blant annet brukes på hus/hjem
    def reload_app(self):
        # Clear existing content
        for widget in self.content.winfo_children():
          widget.destroy()

        # Recreate the main interface
        self.create_main_interface()

        # Attempt to reconnect to the database
        self.attempt_connection()

## Muliggjør dobbelklikk på info i views for å få opp som eget vindu
    def bind_treeview_double_click(self, tree, columns, callback):
        def on_double_click(event):
            selected = tree.focus()
            if not selected:
                return
            item_data = tree.item(selected)['values']
            item_dict = dict(zip(columns, item_data))
            callback(item_dict)
        tree.bind("<Double-1>", on_double_click)

## Alle disse show_* henter fra views og legger inn i GUI.

    def show_orders(self):
        self.orders_view.show()

    def show_inventory(self):
        self.inventory_view.show()

    def show_contacts(self):
        self.contacts_view.show()

    def show_order_contents(self, order_id):
        # Show a dialog with the contents of the order
        ## Litt mer komplekst enn de andre, da det trenger mer info i popup

        try:
            contents = self.db.get_order_contents(order_id)
            if not contents:
                messagebox.showinfo("Order Contents", "No contents found for this order.")
                return
            win = tk.Toplevel(self.root)
            self.register_popup(win)
            win.title(f"Order {order_id}")
            frame = ttk.Frame(win, padding=10)
            frame.pack(fill=tk.BOTH, expand=True)
            tree = ttk.Treeview(frame)
            tree.pack(fill=tk.BOTH, expand=True)
            columns = ["Item", "Item Number", "Quantity", "Price per Item", "Price total"]
            tree["columns"] = columns
            tree.column("#0", width=0, stretch=tk.NO)
            tree.column("Item", anchor=tk.W, width=200)
            tree.heading("Item", text="Item", anchor=tk.W)
            for col in columns[1:]:
                tree.column(col, anchor=tk.CENTER, width=120)
                tree.heading(col, text=col, anchor=tk.CENTER)
            for item in contents:
                # Map DB fields to display columns, gir mye finere navn. Tanken er å gjøre lignende for flere kolonner som bør bli navngitt på nytt
                item_name = item.get("VareNavn") or item.get("Betegnelse") or item.get("Item") or ""
                part_number = item.get("VNr") or item.get("ol.VNr") or item.get("Item Number") or ""
                quantity = item.get("Antall") or item.get("Quantity") or 0
                price_per_item = (
                    item.get("PrisPrEnhet") or item.get("PrisprEnhet") or item.get("PrisEnhet") or item.get("Price per Item") or 0
                )
                try:
                    quantity_val = float(quantity)
                except Exception:
                    quantity_val = 0
                try:
                    price_per_item_val = float(price_per_item)
                except Exception:
                    price_per_item_val = 0
                price_total = price_per_item_val * quantity_val
                values = [
                    str(item_name),
                    str(part_number),
                    int(quantity_val) if quantity_val == int(quantity_val) else quantity_val,
                    f"{price_per_item_val:,.2f}",
                    f"{price_total:,.2f}"
                ]
                tree.insert("", tk.END, values=values)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load order contents: {str(e)}")

    # Filter function for search bar, fungerer på alle sidene.
    def filter_tree(self, tree, data, query, column=None):
        query = query.lower()
        tree.delete(*tree.get_children())

        if not query:
            tree.tag_configure("match", background="")  # Reset match tag
        else:
            tree.tag_configure("match", background="#ffff99")  # Highlight color

        for item in data:
            values = [item[col] for col in tree["columns"]]
            should_display = False

            if not query:
                should_display = True
            elif column and query in str(item[column]).lower():
                should_display = True
            elif not column and any(query in str(val).lower() for val in item.values()):
                should_display = True

            if should_display:
                item_id = tree.insert("", tk.END, values=values)
                if query and any(query in str(val).lower() for val in values):
                    tree.item(item_id, tags=("match",))

    ## Refresh dersom database får nytt innhold
    def refresh_view(self):
        if self.current_view == "orders":  # Checks the current view
            self.show_orders()  # Refreshes orders view
        elif self.current_view == "inventory":  # Checks the current view
            self.show_inventory()  # Refreshes inventory view
        elif self.current_view == "contacts": # Checks the current view
            self.show_contacts() # Refreshes contacts view
        else:
            messagebox.showinfo("Refresh", "No active view to refresh.")

    ## Popup for å vise innhold i de forskjellige views, generic slik den fungerer på alle sider.
    def show_details_popup(self, title, item_dict):
        win = tk.Toplevel(self.root)
        win.geometry("800x600")  # Setter størrelse på popup

        self.register_popup(win) ## Registerer vindu slik at Python har kontroll på vinduene selv, og funskjonalitet for å lukke fungerer
        win.title(title)

        frame = ttk.Frame(win, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        for key, value in item_dict.items():
            row = ttk.Frame(frame)
            row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=f"{key}:", width=20, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(row, text=str(value), anchor=tk.W).pack(side=tk.LEFT)

    def on_close(self):
        # Stop FastAPI server when closing the app, slik at man ikke har stale connections, og port blir holdt.
        if hasattr(self, "api_process") and self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
            except Exception:
                self.api_process.kill()
            self.api_process = None  # Prevent double-kill
        self.root.destroy()
   
    ## Knapp for å åpne webapp
    def open_web_app(self):
        webbrowser.open_new_tab("http://127.0.0.1:8000/")

    ## Lets start!
    def start(self):
        print("Starting the app")
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()