import tkinter as tk
from tkinter import ttk, messagebox
from views.translations.no_en_translation import NO_EN_TRANSLATION

class InventoryView:
    def __init__(self, app):
        self.app = app

    def show(self):
    # Fjern all tidligere innhold, slik at det er plass til nytt vindu
        for widget in self.app.content.winfo_children():
            widget.destroy()
        self.app.current_view = "inventory"     # Setter current view til inventory (refresh funksjon)
        
        ## Søkefelt-funksjonalitet
        search_frame = ttk.Frame(self.app.content)
        search_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        search_var = tk.StringVar()
        selected_column = tk.StringVar(value="All")
        
        # Lag søkefelt og dropdown for kolonner
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Legg til placeholder-tekst
        search_entry.insert(0, "Search...")
        search_entry.config(foreground='grey')
        
        # Funksjon for å håndtere fokus på søkefeltet
        def on_focus_in(event):
            if search_entry.get() == "Search...":
                search_entry.delete(0, tk.END)
                search_entry.config(foreground='black')
        
        def on_focus_out(event):
            if not search_entry.get():
                search_entry.insert(0, "Search...")
                search_entry.config(foreground='grey')
        
        # Funksjon for å tømme søkefeltet
        def clear_search():
            search_entry.delete(0, tk.END)
            search_entry.insert(0, "Search...")
            search_entry.config(foreground='grey')
            
            for item in tree.get_children():
                tree.delete(item)
            
            # Oppdaterer tabell med ny data
            for item in inventory_data:
                values = [item[col] for col in columns]
                tree.insert("", tk.END, values=values)
        
        # Binder fokus til søkefeltet
        search_entry.bind('<FocusIn>', on_focus_in)
        search_entry.bind('<FocusOut>', on_focus_out)
        
        # Legger til knapp for å tømme søkefeltet
        clear_button = ttk.Button(search_frame, text="✕", width=3, command=clear_search)
        clear_button.pack(side=tk.LEFT, padx=(5, 0))

        column_dropdown = ttk.Combobox(search_frame, textvariable=selected_column, state="readonly")    # Dropdown for columns
        column_dropdown.pack(side=tk.LEFT, padx=(5, 0))

        ## Treeview aka Popups
        tree_frame = ttk.Frame(self.app.content)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        tree = ttk.Treeview(tree_frame)     ## main table inventory
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)        # Scrollbar!
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        ## Henter info til tabell/gui
        try:
            inventory_data = self.app.db.get_inventory()
            if not inventory_data:
                ## Viser feilmelding hvis ingen data er tilgjengelig
                ttk.Label(tree_frame, text="No inventory data available").pack()
                return
            
            columns = list(inventory_data[0].keys())    # Henterer kolonnenavn fra første rad
            tree["columns"] = columns                   ## Kolonnenavn i tabellen
            # Lager mapping for oversettelse av kolonnenavn
            column_mapping = {NO_EN_TRANSLATION.get(col, col): col for col in columns}
            column_dropdown["values"] = ["All"] + list(column_mapping.keys())  # Legger til "All" som standard filtrering i søkefelt
            tree.column("#0", width=0, stretch=tk.NO)
            
            for col in columns:
                tree.column(col, anchor=tk.CENTER, width=100)       # Setter bredde på kolonnene
                # Bruker oversettelse hvis tilgjengelig
                translated_col = NO_EN_TRANSLATION.get(col, col)
                tree.heading(col, text=translated_col, anchor=tk.CENTER)
            for item in inventory_data:
                values = [item[col] for col in columns]
                tree.insert("", tk.END, values=values)

            # Binder dobbeltklikk på rader for å vise detaljer
            self.app.bind_treeview_double_click(
                tree, columns,
                lambda item_dict: self.show_details_popup("Inventory Item Details", item_dict)
            )

            ## Søkelogikk slik at den er "realtime"
            def on_search_change(*_):
                search_text = search_var.get()
                # Søker ikke om søkefeltet er tomt
                if search_text == "Search..." or not search_text:
                    # Viser alle elementer fra søket
                    for item in tree.get_children():
                        tree.item(item, tags=())
                    return
                
                col = selected_column.get()
                original_col = column_mapping.get(col, col) if col != "All" else None
                self.app.filter_tree(tree, inventory_data, search_text, column=original_col)

            search_var.trace_add("write", on_search_change)
            selected_column.trace_add("write", on_search_change)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory: {str(e)}")

    ## Viser detaljer i popup-vindu
    def show_details_popup(self, title, item_dict):
        win = tk.Toplevel(self.app.root)
        win.geometry("800x600")  # Setter vindusstørrelse
        self.app.register_popup(win)    ## Registerer popup-vinduet, slik alle kan lukkes med knapp i meny
        win.title(title)
        frame = ttk.Frame(win, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        for key, value in item_dict.items():
            row = ttk.Frame(frame)
            row.pack(fill=tk.X, pady=2)
            translated_key = NO_EN_TRANSLATION.get(key, key)
            ttk.Label(row, text=f"{translated_key}:", width=20, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(row, text=str(value), anchor=tk.W).pack(side=tk.LEFT)
