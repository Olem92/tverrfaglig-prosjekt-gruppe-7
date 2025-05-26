# Henter database-klassen fra database.py
from database import VarehusDatabase
# Henter tkinter som tk og nødvendige moduler for GUI
import tkinter as tk
from tkinter import messagebox, ttk
# Henter PIL for bildebehandling
from PIL import Image, ImageTk
# Henter nødvendige moduler for systemoperasjoner
import os, subprocess, sys, webbrowser
# Henter views for ordre, lagerbeholdning og kontakter
from views.orders_view import OrdersView
from views.inventory_view import InventoryView
from views.contacts_view import ContactsView

# Starter applikasjonen med FastAPI og tkinter GUI
class App:
    def __init__(self):
        # Starter FastAPI slik at WebApp-fungerer
        self.api_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api:app", "--reload"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        ## Initialiserer GUI-vinduer, med satt størrelse
        self.db = VarehusDatabase()
        self.root = tk.Tk()
        self.root.title("Warehouse Mini ERP System")
        self.root.geometry("1000x800")
        self.orders_view = OrdersView(self)             ## De forskjellige views innad i app
        self.inventory_view = InventoryView(self)       ## De forskjellige views innad i app
        self.contacts_view = ContactsView(self)         ## De forskjellige views innad i app
        self.popups = []  # Holder styr på alle popup-vinduer, slik at programmet har kontroll på hva som er åpent og kan lukke dem.
        
        # Legger til tastaturhåndtering
        self.root.bind('<Key>', self.handle_keypress)  # Binder alle tastetrykk

        self.create_menu()
        self.create_main_interface()
        
        # Kobler til databasen ved oppstart
        self.attempt_connection()
        
        # Setter opp vinduet for å håndtere lukking
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Passer på at vinduet kan lukkes både på Mac og Windows
        self.root.quit = self.on_close

    ## Del-funksjon som muliggjør lukking av popup-vinduer
    def register_popup(self, win):
        self.popups.append(win)
        win.transient(self.root)
        win.focus_set()
        win.lift()
        win.protocol("WM_DELETE_WINDOW", lambda w=win: self._close_popup(w))

    ## Lukk popup-vindu fra X
    def _close_popup(self, win):
        if win in self.popups:
            self.popups.remove(win)
        win.destroy()

    ## Lukker alle åpne popups
    def close_all_popups(self):
        for win in self.popups[:]:
            try:
                win.destroy()
            except Exception:
                pass
        self.popups.clear()

    ## Funksjon for å håndtere tastetrykk
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
        
        return 'break'  # Stopper behandling av tastetrykk

    ## Fil-menyen i GUI
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Fil-meny
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Reconnect to Database", command=self.attempt_connection)
        file_menu.add_command(label="Close All Popups", command=self.close_all_popups)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)

    ## Hovedgrensesnittet for applikasjonen
    def create_main_interface(self):

        # Setter vindustatus til 'None' for å indikere at ingen view er aktivt (for Refresh-funksjon)
        self.current_view = None

        # Lager hovedcontainer
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Konfigurerer grid i programmet
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)  # Innholdsområdet skal utvides

        # Toppmeny-bar grid
        menu_bar = ttk.Frame(self.main_frame)
        menu_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Menyknapper venstre
        home_img = Image.open(os.path.join(os.path.dirname(__file__), "icons", "home.png")).convert("RGBA").resize((18, 18), Image.LANCZOS)
        refresh_img = Image.open(os.path.join(os.path.dirname(__file__), "icons", "refresh.png")).convert("RGBA").resize((18, 18), Image.LANCZOS)
        home_icon = ImageTk.PhotoImage(home_img)
        refresh_icon = ImageTk.PhotoImage(refresh_img)

        ## Knapper i toppen av GUI, brukes for navigering mellom views
        # Menyknapper venstre
        home_btn = ttk.Button(menu_bar, image=home_icon, command=self.reload_app)
        home_btn.pack(side=tk.LEFT, padx=6, pady=4, ipadx=4, ipady=2)

        ttk.Button(menu_bar, text="Orders", command=self.show_orders).pack(side=tk.LEFT, padx=2)
        ttk.Button(menu_bar, text="Inventory", command=self.show_inventory).pack(side=tk.LEFT, padx=2)
        ttk.Button(menu_bar, text="Contacts", command=self.show_contacts).pack(side=tk.LEFT, padx=2)
        
        # Menyknapper høyre
        refresh_btn = ttk.Button(menu_bar, image=refresh_icon, command=self.refresh_view)
        refresh_btn.pack(side=tk.RIGHT, padx=6, pady=4, ipadx=4, ipady=2)
        
        # Lagrer referanser til ikoner for å forhindre garbage collection
        self.home_icon = home_icon
        self.refresh_icon = refresh_icon
        
        # Hovedinnholdsområde
        self.content = ttk.Frame(self.main_frame)
        self.content.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Sentrerer hovedvinduet på skjermen
        self.center_window()
        
        # Velkomstmelding på startside
        welcome_label = ttk.Label(self.content, text="Welcome to Warehouse Mini ERP System")
        welcome_label.pack(pady=20)
        style = ttk.Style()
        style.configure("Welcome.TLabel", font=('Helvetica', 16))
        welcome_label.configure(style="Welcome.TLabel")
        
        # Knapp for å åpne WebGUI raskt uten å huske port
        open_web_btn = ttk.Button(self.content, text="Åpne Web App", command=self.open_web_app)
        open_web_btn.pack(pady=10)

        # Statuslinje (kun tilkoblingsinfo)
        status_frame = ttk.Frame(self.root)
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)

        # Connection status
        self.connection_var = tk.StringVar(value="Not connected")
        self.status_label = ttk.Label(status_frame, textvariable=self.connection_var)
        self.status_label.grid(row=0, column=0, sticky=(tk.E), padx=1)

        # Tilkoblingsstil
        style.configure("Connected.TLabel", foreground="green")
        style.configure("Disconnected.TLabel", foreground="red")

    ## Funksjon for å sentrere vinduet
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

            # Prøver ping for å bekrefte at tilkoblingen faktisk er aktiv
            self.db.connection.ping(reconnect=True)

            self.connection_var.set("Successfully connected to varehusdb")
            self.status_label.configure(style="Connected.TLabel")
        except Exception as e:
            self.connection_var.set("Not connected")
            self.status_label.configure(style="Disconnected.TLabel")
            messagebox.showerror("Connection Error", f"Failed to connect to database: {str(e)}")

## Funksjon for å reloade appen, blant annet brukt på hjem-knappen
    def reload_app(self):
        # Fjerner eksisterende innhold
        for widget in self.content.winfo_children():
          widget.destroy()

        # Gjenskaper hovedgrensesnittet
        self.create_main_interface()

        # Prøver å koble til databasen på nytt
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

    # Filterfunksjon for søkefelt, fungerer på alle sidene.
    def filter_tree(self, tree, data, query, column=None):
        query = query.lower()
        tree.delete(*tree.get_children())

        if not query:
            tree.tag_configure("match", background="")  # Tilbakestill match-tag
        else:
            tree.tag_configure("match", background="#ffff99")  # Marker treff

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

    ## Oppdater dersom databasen får nytt innhold
    def refresh_view(self):
        if self.current_view == "orders":  # Checks the current view
            self.show_orders()  # Refreshes orders view
        elif self.current_view == "inventory":  # Checks the current view
            self.show_inventory()  # Refreshes inventory view
        elif self.current_view == "contacts": # Checks the current view
            self.show_contacts() # Refreshes contacts view
        else:
            messagebox.showinfo("Refresh", "No active view to refresh.")

    def on_close(self):
        # Stopper FastAPI-server når appen lukkes, slik at man ikke har hengende tilkoblinger og porten blir frigjort.
        if hasattr(self, "api_process") and self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
            except Exception:
                self.api_process.kill()
            self.api_process = None  # Forhindre dobbelt-stopp
        self.root.destroy()
   
    ## Knapp for å åpne webapp
    def open_web_app(self):
        webbrowser.open_new_tab("http://127.0.0.1:8000/")

    ## Starter applikasjonen
    def start(self):
        print("Starting the app")
        self.root.mainloop()

if __name__ == "__main__":
    app = App()
    app.start()