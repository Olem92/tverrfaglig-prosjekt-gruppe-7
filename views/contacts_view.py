import tkinter as tk
from tkinter import ttk, messagebox
from views.translations.no_en_translation import NO_EN_TRANSLATION

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
            
            # Reinsert all contacts
            for item in contacts_data:
                values = [item[col] for col in columns]
                tree.insert("", tk.END, values=values)
        
        # Bind focus events
        search_entry.bind('<FocusIn>', on_focus_in)
        search_entry.bind('<FocusOut>', on_focus_out)
        
        # Add clear button
        clear_button = ttk.Button(search_frame, text="✕", width=3, command=clear_search)
        clear_button.pack(side=tk.LEFT, padx=(5, 0))
        
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

        ## Button frame for Add and Remove buttons
        button_frame = ttk.Frame(self.app.content)
        button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        add_button = ttk.Button(button_frame, text="Add Contact", command=self.show_add_contact_popup)
        add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_button = ttk.Button(button_frame, text="Remove Contact", command=self.remove_selected_contact)
        remove_button.pack(side=tk.LEFT)
        
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
            # Create a mapping of translated column names to original column names
            column_mapping = {NO_EN_TRANSLATION.get(col, col): col for col in columns}
            column_dropdown["values"] = ["All"] + list(column_mapping.keys())  # Populate dropdown with translated column names
            tree.column("#0", width=0, stretch=tk.NO)  # Hide the default first column
            for col in columns:
                tree.column(col, anchor=tk.CENTER, width=100)  # Set column width and alignment
                # Use translation if available, otherwise use the original column name
                translated_col = NO_EN_TRANSLATION.get(col, col)
                tree.heading(col, text=translated_col, anchor=tk.CENTER)  # Set column heading
            for item in contacts_data:
                values = [item[col] for col in columns]  # Extract values for each row
                tree.insert("", tk.END, values=values)  # Insert row into treeview
            
            # Bind double-click event to show a popup with contact details
            self.app.bind_treeview_double_click(
                tree, columns,
                lambda item_dict: self.show_details_popup("Contact Details", item_dict)
            )
           
            ## Søkelogikk slik at den er "realtime"
            def on_search_change(*_):
                # Called whenever search or column selection changes
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
                # Filter the treeview based on search query and selected column
                self.app.filter_tree(tree, contacts_data, search_text, column=original_col)
            
            search_var.trace_add("write", on_search_change)  # React to typing in search box
            selected_column.trace_add("write", on_search_change)  # React to column dropdown changes
        
        except Exception as e:
            # Show error popup if something goes wrong
            messagebox.showerror("Error", f"Failed to load contacts: {str(e)}")

    def show_details_popup(self, title, item_dict):
        # Show a popup window with all details for a contact
        win = tk.Toplevel(self.app.root)
        win.geometry("800x600")  # Set a reasonable size for the popup
        self.app.register_popup(win)  # Register popup for bulk close support
        win.title(title)
        frame = ttk.Frame(win, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        # Display each key-value pair in the contact as a row
        for key, value in item_dict.items():
            row = ttk.Frame(frame)
            row.pack(fill=tk.X, pady=2)
            # Use translation if available, otherwise use the original key
            translated_key = NO_EN_TRANSLATION.get(key, key)
            ttk.Label(row, text=f"{translated_key}:", width=20, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(row, text=str(value), anchor=tk.W).pack(side=tk.LEFT)

    def show_add_contact_popup(self):
        # Create a popup window for adding a new contact
        win = tk.Toplevel(self.app.root)
        win.geometry("400x500")
        self.app.register_popup(win)
        win.title("Add New Contact")
        
        # Create a frame for the form
        form_frame = ttk.Frame(win, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a label and entry for each field
        # This is a basic structure - you can modify the fields based on your needs
        fields = ["Firstname", "Lastname", "Address", "ZIP Code"]
        entries = {}
        
        for field in fields:
            frame = ttk.Frame(form_frame)
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=f"{field}:").pack(side=tk.LEFT)
            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
            entries[field] = entry
        
        # Add buttons at the bottom
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=lambda: self.save_new_contact(entries, win)).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=win.destroy).pack(side=tk.RIGHT)

    def save_new_contact(self, entries, window):
        # This is a placeholder for the save functionality
        # You can implement the actual save logic later
        window.destroy()
        messagebox.showinfo("Success", "Contact added successfully!")

    def remove_selected_contact(self):
        # This is a placeholder for the remove functionality
        # You can implement the actual remove logic later
        messagebox.showinfo("Info", "Remove functionality will be implemented later")
