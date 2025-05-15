import tkinter as tk
from tkinter import ttk, messagebox

class ContactsView:
    def __init__(self, app):
        self.app = app  # Reference to the main application instance

    def show(self):
        # Fjern all tidligere innhold, slik at det er plass til nytt vindu
        for widget in self.app.content.winfo_children():
            widget.destroy()
        self.app.current_view = "contacts"  # Set current view for refresh logic

        ## Søkefelt-funksjonalitet
        search_frame = ttk.Frame(self.app.content)
        search_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        search_var = tk.StringVar()  # Holds the search query
        selected_column = tk.StringVar(value="All")  # Holds the selected column for filtering
        search_entry = ttk.Entry(search_frame, textvariable=search_var)  # Text entry for search
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        column_dropdown = ttk.Combobox(search_frame, textvariable=selected_column, state="readonly")  # Dropdown for columns
        column_dropdown.pack(side=tk.LEFT, padx=(5, 0))

        ## Treeview aka Popups
        tree_frame = ttk.Frame(self.app.content)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        tree = ttk.Treeview(tree_frame)  # Main table for contacts
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)  # Vertical scrollbar
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
        
        ## Henter info til tabell/GUI
        try:
            # Fetch all contacts from the database
            contacts_data = self.app.db.get_contacts()
            if not contacts_data:
                # Show message if no data is available
                ttk.Label(tree_frame, text="No contact data available").pack()
                return
            columns = list(contacts_data[0].keys())  # Extract column names fra første record
            tree["columns"] = columns  # Set columns for the treeview
            column_dropdown["values"] = ["All"] + columns  # Populate dropdown with column names
            tree.column("#0", width=0, stretch=tk.NO)  # Hide the default first column
            for col in columns:
                tree.column(col, anchor=tk.CENTER, width=100)  # Set column width and alignment
                tree.heading(col, text=col.title(), anchor=tk.CENTER)  # Set column heading
            for item in contacts_data:
                values = [item[col] for col in columns]  # Extract values for each row
                tree.insert("", tk.END, values=values)  # Insert row into treeview
            
            # Bind double-click event to show a popup with contact details
            self.app.bind_treeview_double_click(
                tree, columns,
                lambda item_dict: self.app.show_details_popup("Contact Details", item_dict)
            )
           
            ## Søkelogikk slik at den er "realtime"
            def on_search_change(*_):
                # Called whenever search or column selection changes
                col = selected_column.get()
                # Filter the treeview based on search query and selected column
                self.app.filter_tree(tree, contacts_data, search_var.get(), column=None if col == "All" else col)
            
            search_var.trace_add("write", on_search_change)  # React to typing in search box
            selected_column.trace_add("write", on_search_change)  # React to column dropdown changes
        
        except Exception as e:
            # Show error popup if something goes wrong
            messagebox.showerror("Error", f"Failed to load contacts: {str(e)}")

    def show_details_popup(self, title, item_dict):
        # Show a popup window with all details for a contact
        win = tk.Toplevel(self.app.root)
        self.app.register_popup(win)  # Register popup for bulk close support
        win.title(title)
        frame = ttk.Frame(win, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        # Display each key-value pair in the contact as a row
        for key, value in item_dict.items():
            row = ttk.Frame(frame)
            row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=f"{key}:", width=20, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(row, text=str(value), anchor=tk.W).pack(side=tk.LEFT)
