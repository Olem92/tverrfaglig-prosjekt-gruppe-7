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
        self.app.current_view = "inventory"     # Set current view for refresh logic
        
        ## Søkefelt-funksjonalitet
        search_frame = ttk.Frame(self.app.content)
        search_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        search_var = tk.StringVar()             ## Search Query
        selected_column = tk.StringVar(value="All")              ## Holds the selected column, slik man kan filtrere
        
        # Create search entry with placeholder
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add placeholder text
        search_entry.insert(0, "Search...")
        search_entry.config(foreground='grey')
        
        # Function to handle placeholder behavior
        def on_focus_in(event):
            if search_entry.get() == "Search...":
                search_entry.delete(0, tk.END)
                search_entry.config(foreground='black')
        
        def on_focus_out(event):
            if not search_entry.get():
                search_entry.insert(0, "Search...")
                search_entry.config(foreground='grey')
        
        # Function to clear search
        def clear_search():
            search_entry.delete(0, tk.END)
            search_entry.insert(0, "Search...")
            search_entry.config(foreground='grey')
            
            # Clear and reload the treeview
            for item in tree.get_children():
                tree.delete(item)
            
            # Reinsert all inventory items
            for item in inventory_data:
                values = [item[col] for col in columns]
                tree.insert("", tk.END, values=values)
        
        # Bind focus events
        search_entry.bind('<FocusIn>', on_focus_in)
        search_entry.bind('<FocusOut>', on_focus_out)
        
        # Add clear button
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
                ## Show message if no data is avaliable
                ttk.Label(tree_frame, text="No inventory data available").pack()
                return
            
            columns = list(inventory_data[0].keys())    # Extract column names fra første record
            tree["columns"] = columns                   ## Colomns til treeview
            # Create a mapping of translated column names to original column names
            column_mapping = {NO_EN_TRANSLATION.get(col, col): col for col in columns}
            column_dropdown["values"] = ["All"] + list(column_mapping.keys())  # Populate dropdown with translated column names
            tree.column("#0", width=0, stretch=tk.NO)       # Hide first column
            
            for col in columns:
                tree.column(col, anchor=tk.CENTER, width=100)       # Set column width and headings
                # Use translation if available, otherwise use the original column name
                translated_col = NO_EN_TRANSLATION.get(col, col)
                tree.heading(col, text=translated_col, anchor=tk.CENTER)
            for item in inventory_data:
                values = [item[col] for col in columns]
                tree.insert("", tk.END, values=values)

            # Bind double click event to show popup with contact details
            self.app.bind_treeview_double_click(
                tree, columns,
                lambda item_dict: self.show_details_popup("Inventory Item Details", item_dict)
            )

            ## Søkelogikk slik at den er "realtime"
            def on_search_change(*_):
                search_text = search_var.get()
                # Don't search if the text is the placeholder or empty
                if search_text == "Search..." or not search_text:
                    # Show all items
                    for item in tree.get_children():
                        tree.item(item, tags=())
                    return
                
                col = selected_column.get()
                # Convert translated column name back to original column name for filtering
                original_col = column_mapping.get(col, col) if col != "All" else None
                # Filter the treeview
                self.app.filter_tree(tree, inventory_data, search_text, column=original_col)

            # Realtime!
            search_var.trace_add("write", on_search_change)
            selected_column.trace_add("write", on_search_change)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory: {str(e)}")

    def show_details_popup(self, title, item_dict):
        # Show a popup windows with all details
        win = tk.Toplevel(self.app.root)
        win.geometry("800x600")  # Set a reasonable size for the popup
        self.app.register_popup(win)    ## Register popup for bulk close support
        win.title(title)
        frame = ttk.Frame(win, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Display each key value pair in the contact as a row
        for key, value in item_dict.items():
            row = ttk.Frame(frame)
            row.pack(fill=tk.X, pady=2)
            # Use translation if available, otherwise use the original key
            translated_key = NO_EN_TRANSLATION.get(key, key)
            ttk.Label(row, text=f"{translated_key}:", width=20, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(row, text=str(value), anchor=tk.W).pack(side=tk.LEFT)
