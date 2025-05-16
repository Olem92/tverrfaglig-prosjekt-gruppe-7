import tkinter as tk
from tkinter import ttk, messagebox
from views.translations.no_en_translation import NO_EN_TRANSLATION

class ContactsView:
    def __init__(self, app):
        self.app = app  # Reference to the main application instance
        self.tree = None  # Store reference to treeview for updates

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
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Reinsert all contacts
            for item in contacts_data:
                values = [item[col] for col in columns]
                self.tree.insert("", tk.END, values=values)
        
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
        self.tree = ttk.Treeview(tree_frame)  # Main table for contacts
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)  # Vertical scrollbar
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        ## Button frame for Add and Remove buttons
        button_frame = ttk.Frame(self.app.content)
        button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        add_button = ttk.Button(button_frame, text="Add Contact", command=self.show_add_contact_popup)
        add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        edit_button = ttk.Button(button_frame, text="Edit Contact", command=self.show_edit_contact_popup)
        edit_button.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_button = ttk.Button(button_frame, text="Remove Contact", command=self.remove_selected_contact)
        remove_button.pack(side=tk.LEFT)

        edit_button = ttk.Button(button_frame, text="Edit Contact", command=self.edit_selected_contact)
        edit_button.pack(side=tk.LEFT)
        
        ## Henter info til tabell/GUI
        try:
            # Fetch all contacts from the database
            contacts_data = self.app.db.get_contacts()
            if not contacts_data:
                # Show message if no data is available
                ttk.Label(tree_frame, text="No contact data available").pack()
                return
            columns = list(contacts_data[0].keys())  # Extract column names fra første record
            self.tree["columns"] = columns  # Set columns for the treeview
            # Create a mapping of translated column names to original column names
            column_mapping = {NO_EN_TRANSLATION.get(col, col): col for col in columns}
            column_dropdown["values"] = ["All"] + list(column_mapping.keys())  # Populate dropdown with translated column names
            self.tree.column("#0", width=0, stretch=tk.NO)  # Hide the default first column
            for col in columns:
                self.tree.column(col, anchor=tk.CENTER, width=100)  # Set column width and alignment
                # Use translation if available, otherwise use the original column name
                translated_col = NO_EN_TRANSLATION.get(col, col)
                self.tree.heading(col, text=translated_col, anchor=tk.CENTER)  # Set column heading
            for item in contacts_data:
                values = [item[col] for col in columns]  # Extract values for each row
                self.tree.insert("", tk.END, values=values)  # Insert row into treeview
            
            # Bind double-click event to show a popup with contact details
            self.app.bind_treeview_double_click(
                self.tree, columns,
                lambda item_dict: self.show_details_popup("Contact Details", item_dict)
            )
           
            ## Søkelogikk slik at den er "realtime"
            def on_search_change(*_):
                # Called whenever search or column selection changes
                search_text = search_var.get()
                # Don't search if the text is the placeholder or empty
                if search_text == "Search..." or not search_text:
                    # Show all items
                    for item in self.tree.get_children():
                        self.tree.item(item, tags=())
                    return
                
                col = selected_column.get()
                # Convert translated column name back to original column name for filtering
                original_col = column_mapping.get(col, col) if col != "All" else None
                # Filter the treeview based on search query and selected column
                self.app.filter_tree(self.tree, contacts_data, search_text, column=original_col)
            
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
        fields = ["Fornavn", "Etternavn", "Adresse", "PostNr"]
        entries = {}
        
        for field in fields:
            frame = ttk.Frame(form_frame)
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=f"{NO_EN_TRANSLATION.get(field, field)}:").pack(side=tk.LEFT)
            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
            entries[field] = entry
        
        # Add buttons at the bottom
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=lambda: self.save_new_contact(entries, win)).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=win.destroy).pack(side=tk.RIGHT)

    def show_edit_contact_popup(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a contact to edit")
            return

        # Get the current values
        current_values = self.tree.item(selected)['values']
        columns = self.tree["columns"]
        current_data = dict(zip(columns, current_values))

        # Create a popup window for editing the contact
        win = tk.Toplevel(self.app.root)
        win.geometry("400x500")
        self.app.register_popup(win)
        win.title("Edit Contact")
        
        # Create a frame for the form
        form_frame = ttk.Frame(win, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add a label and entry for each field
        fields = ["Fornavn", "Etternavn", "Adresse", "PostNr"]
        entries = {}
        
        for field in fields:
            frame = ttk.Frame(form_frame)
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=f"{NO_EN_TRANSLATION.get(field, field)}:").pack(side=tk.LEFT)
            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
            # Set current value
            entry.insert(0, str(current_data.get(field, "")))
            entries[field] = entry
        
        # Add buttons at the bottom
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=lambda: self.save_edited_contact(entries, current_data, win)).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=win.destroy).pack(side=tk.RIGHT)

    def save_new_contact(self, entries, window):
        # Map GUI fields to database fields
        fornavn = entries["Firstname"].get()
        etternavn = entries["Lastname"].get()
        adresse = entries["Address"].get()
        postnr = entries["ZIP Code"].get()
        # Call the database function
        success = self.app.db.add_contacts(fornavn, etternavn, adresse, postnr)
        window.destroy()
        if success:
            messagebox.showinfo("Success", "Contact added successfully!")
            self.show()  # Refresh the contacts view
        else:
            messagebox.showerror("Error", "Failed to add contact.")
        try:
            # Collect all the values from the entries
            fornavn = entries["Fornavn"].get().strip()
            etternavn = entries["Etternavn"].get().strip()
            adresse = entries["Adresse"].get().strip()
            postnr = entries["PostNr"].get().strip()
            
            # Validate required fields
            if not fornavn or not etternavn:
                messagebox.showerror("Error", "First name and last name are required")
                return

            # Add the contact to the database
            if self.app.db.add_contacts(fornavn, etternavn, adresse, postnr):
                # Refresh the view
                self.show()
                window.destroy()
                messagebox.showinfo("Success", "Contact added successfully!")
            else:
                messagebox.showerror("Error", "Failed to add contact")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add contact: {str(e)}")

    def save_edited_contact(self, entries, current_data, window):
        try:
            # Collect all the values from the entries
            fornavn = entries["Fornavn"].get().strip()
            etternavn = entries["Etternavn"].get().strip()
            adresse = entries["Adresse"].get().strip()
            postnr = entries["PostNr"].get().strip()
            
            # Validate required fields
            if not fornavn or not etternavn:
                messagebox.showerror("Error", "First name and last name are required")
                return

            # Update the contact in the database
            if self.app.db.edit_contacts(current_data["KNr"], fornavn, etternavn, adresse, postnr):
                # Refresh the view
                self.show()
                window.destroy()
                messagebox.showinfo("Success", "Contact updated successfully!")
            else:
                messagebox.showerror("Error", "Failed to update contact")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update contact: {str(e)}")

    def remove_selected_contact(self):
        # Get selected item from the treeview
        tree = self.app.content.winfo_children()[1].winfo_children()[0]  # Assumes treeview is always in this position
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No contact selected.")
            return
        # Get KNr from the selected row (assumes KNr is the first column)
        knr = tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm", "Are you sure you want to remove this contact?"):
            success = self.app.db.remove_contacts(knr)
            if success:
                messagebox.showinfo("Success", "Contact removed successfully!")
                self.show()  # Refresh the contacts view
            else:
                messagebox.showerror("Error", "Failed to remove contact.")

    def edit_selected_contact(self):
        # Get selected item from the treeview
        tree = self.app.content.winfo_children()[1].winfo_children()[0]  # Assumes treeview is always in this position
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No contact selected.")
            return
        # Get current values
        values = tree.item(selected[0])['values']
        columns = tree["columns"]
        # Create popup for editing
        win = tk.Toplevel(self.app.root)
        win.geometry("400x500")
        self.app.register_popup(win)
        win.title("Edit Contact")
        form_frame = ttk.Frame(win, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        fields = ["Firstname", "Lastname", "Address", "ZIP Code"]
        entries = {}
        # Map columns to fields
        col_map = {
            "Firstname": "Fornavn",
            "Lastname": "Etternavn",
            "Address": "Adresse",
            "ZIP Code": "PostNr"
        }
        # Find index of each column
        col_indices = {col: columns.index(col_map[col]) for col in fields if col_map[col] in columns}
        for field in fields:
            frame = ttk.Frame(form_frame)
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=f"{field}:").pack(side=tk.LEFT)
            entry = ttk.Entry(frame)
            # Pre-fill with current value
            idx = col_indices.get(field)
            if idx is not None:
                entry.insert(0, values[idx])
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
            entries[field] = entry
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        def save_edit():
            fornavn = entries["Firstname"].get()
            etternavn = entries["Lastname"].get()
            adresse = entries["Address"].get()
            postnr = entries["ZIP Code"].get()
            knr = values[0]  # Assumes KNr is the first column
            success = self.app.db.edit_contacts(knr, fornavn, etternavn, adresse, postnr)
            win.destroy()
            if success:
                messagebox.showinfo("Success", "Contact updated successfully!")
                self.show()  # Refresh the contacts view
            else:
                messagebox.showerror("Error", "Failed to update contact.")
        ttk.Button(button_frame, text="Save", command=save_edit).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=win.destroy).pack(side=tk.RIGHT)
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a contact to remove")
            return

        # Get the current values
        current_values = self.tree.item(selected)['values']
        columns = self.tree["columns"]
        current_data = dict(zip(columns, current_values))

        # Confirm deletion
        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete this contact?"):
            try:
                # Remove the contact from the database
                if self.app.db.remove_contacts(current_data["KNr"]):
                    # Refresh the view
                    self.show()
                    messagebox.showinfo("Success", "Contact deleted successfully!")
                else:
                    messagebox.showerror("Error", "Failed to delete contact")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete contact: {str(e)}")
