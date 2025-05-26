import tkinter as tk
from tkinter import ttk, messagebox
from views.translations.no_en_translation import NO_EN_TRANSLATION

class ContactsView:
    def __init__(self, app):
        self.app = app  # Referanse til hovedapplikasjonen
        self.tree = None  # Referanse til treeview for oppdateringer

    def show(self):
        # Fjerner alt tidligere innhold slik at nytt vindu kan vises
        for widget in self.app.content.winfo_children():
            widget.destroy()
        self.app.current_view = "contacts"  # Angir nåværende visning for oppdateringslogikk

        ## Søkefelt-funksjonalitet
        search_frame = ttk.Frame(self.app.content)
        search_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        search_var = tk.StringVar()  # Holder søketeksten
        selected_column = tk.StringVar(value="All")  # Holder valgt kolonne for filtrering
        
        # Lager søkefelt med plassholder
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Legger til plassholdertekst
        search_entry.insert(0, "Search...")
        search_entry.config(foreground='grey')
        
        # Funksjon for å håndtere plassholder ved fokus
        def on_focus_in(event):
            if search_entry.get() == "Search...":
                search_entry.delete(0, tk.END)
                search_entry.config(foreground='black')
        
        def on_focus_out(event):
            if not search_entry.get():
                search_entry.insert(0, "Search...")
                search_entry.config(foreground='grey')
        
        # Funksjon for å tømme søkefeltet og oppdatere treeview
        def clear_search():
            search_entry.delete(0, tk.END)
            search_entry.insert(0, "Search...")
            search_entry.config(foreground='grey')
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            for item in contacts_data:
                values = [item[col] for col in columns]
                self.tree.insert("", tk.END, values=values)
        
        # Binder vindu i fokus
        search_entry.bind('<FocusIn>', on_focus_in)
        search_entry.bind('<FocusOut>', on_focus_out)
        
        # Legger til knapp for å tømme søk
        clear_button = ttk.Button(search_frame, text="✕", width=3, command=clear_search)
        clear_button.pack(side=tk.LEFT, padx=(5, 0))
        
        column_dropdown = ttk.Combobox(search_frame, textvariable=selected_column, state="readonly")  # Nedtrekksmeny for kolonner
        column_dropdown.pack(side=tk.LEFT, padx=(5, 0))

        ## Treeview (tabell med kontakter)
        tree_frame = ttk.Frame(self.app.content)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree = ttk.Treeview(tree_frame)  # Hovedtabell for kontakter
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)  # Vertikal rullefelt
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        ## Knapperamme for Legg til, Rediger og Fjern
        button_frame = ttk.Frame(self.app.content)
        button_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        add_button = ttk.Button(button_frame, text="Add Contact", command=self.show_add_contact_popup)
        add_button.pack(side=tk.LEFT, padx=(0, 5))
        
        edit_button = ttk.Button(button_frame, text="Edit Contact", command=self.show_edit_contact_popup)
        edit_button.pack(side=tk.LEFT, padx=(0, 5))
        
        remove_button = ttk.Button(button_frame, text="Remove Contact", command=self.remove_selected_contact)
        remove_button.pack(side=tk.LEFT)
        
        ## Henter informasjon til tabell/GUI
        try:
            # Henter alle kontakter fra databasen
            contacts_data = self.app.db.get_contacts()
            if not contacts_data:
                # Viser melding hvis ingen data er tilgjengelig
                ttk.Label(tree_frame, text="No contact data available").pack()
                return
            columns = list(contacts_data[0].keys())  # Henter kolonnenavn
            self.tree["columns"] = columns
            # Lager mapping fra oversatte kolonnenavn
            column_mapping = {NO_EN_TRANSLATION.get(col, col): col for col in columns}
            column_dropdown["values"] = ["All"] + list(column_mapping.keys())  # Fyller nedtrekksmeny med oversatte kolonnenavn
            self.tree.column("#0", width=0, stretch=tk.NO)  # Skjuler første kolonne
            for col in columns:
                self.tree.column(col, anchor=tk.CENTER, width=100)  # Setter bredde
                # Bruker oversettelse hvis tilgjengelig
                translated_col = NO_EN_TRANSLATION.get(col, col)
                self.tree.heading(col, text=translated_col, anchor=tk.CENTER)  # Setter kolonneoverskrift
            for item in contacts_data:
                values = [item[col] for col in columns]  # Henter verdier for hver rad
                self.tree.insert("", tk.END, values=values)  # Legger til rad i treeview
            
            # Binder dobbeltklikk for å vise popup med kontaktinfo
            self.app.bind_treeview_double_click(
                self.tree, columns,
                lambda item_dict: self.show_details_popup("Contact Details", item_dict)
            )
           
            ## Søkelogikk slik at søk skjer "live"
            def on_search_change(*_):
                # Kalles når søk eller kolonnevalg endres
                search_text = search_var.get()
                # Ikke søk hvis tekstboks er tom
                if search_text == "Search..." or not search_text:
                    # Viser alle rader
                    for item in self.tree.get_children():
                        self.tree.item(item, tags=())
                    return
                
                col = selected_column.get()
                # Konverterer oversatt kolonnenavn tilbake til originalt for filtrering
                original_col = column_mapping.get(col, col) if col != "All" else None
                # Filtrerer treeview basert på søk og valgt kolonne
                self.app.filter_tree(self.tree, contacts_data, search_text, column=original_col)
            
            search_var.trace_add("write", on_search_change)  # Reagerer på skriving i søkefelt
            selected_column.trace_add("write", on_search_change)  # Reagerer på endring i kolonnevalg
        
        except Exception as e:
            # Viser feilmelding hvis noe går galt
            messagebox.showerror("Error", f"Failed to load contacts: {str(e)}")

    def show_details_popup(self, title, item_dict):
        # Viser popup-vindu med alle detaljer for en kontakt
        win = tk.Toplevel(self.app.root)
        win.geometry("800x600")  # Setter størrelse på popup
        self.app.register_popup(win)  # Registrerer popup for lukking
        win.title(title)
        frame = ttk.Frame(win, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        # Viser hver nøkkel-verdi som en rad
        for key, value in item_dict.items():
            row = ttk.Frame(frame)
            row.pack(fill=tk.X, pady=2)
            # Bruker oversettelse hvis tilgjengelig, ellers original nøkkel
            translated_key = NO_EN_TRANSLATION.get(key, key)
            ttk.Label(row, text=f"{translated_key}:", width=20, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(row, text=str(value), anchor=tk.W).pack(side=tk.LEFT)

    def show_add_contact_popup(self):
        # Lager popup-vindu for å legge til ny kontakt
        win = tk.Toplevel(self.app.root)
        win.geometry("400x500")
        self.app.register_popup(win)
        win.title("Add New Contact")
        
        # Lager ramme for skjema
        form_frame = ttk.Frame(win, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Legger til etikett og felt for hver kolonne
        fields = ["Fornavn", "Etternavn", "Adresse", "PostNr"]
        entries = {}
        
        for field in fields:
            frame = ttk.Frame(form_frame)
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=f"{NO_EN_TRANSLATION.get(field, field)}:").pack(side=tk.LEFT)
            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
            entries[field] = entry
        
        # Legger til knapper nederst
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=lambda: self.save_new_contact(entries, win)).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=win.destroy).pack(side=tk.RIGHT)

    def show_edit_contact_popup(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Please select a contact to edit")
            return

        # Henter nåværende verdier
        current_values = self.tree.item(selected)['values']
        columns = self.tree["columns"]
        current_data = dict(zip(columns, current_values))

        # Lager popup-vindu for å redigere kontakt
        win = tk.Toplevel(self.app.root)
        win.geometry("400x500")
        self.app.register_popup(win)
        win.title("Edit Contact")
        
        # Lager ramme for skjema
        form_frame = ttk.Frame(win, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # Legger til etikett og felt for hver kolonne
        fields = ["Fornavn", "Etternavn", "Adresse", "PostNr"]
        entries = {}
        
        for field in fields:
            frame = ttk.Frame(form_frame)
            frame.pack(fill=tk.X, pady=5)
            ttk.Label(frame, text=f"{NO_EN_TRANSLATION.get(field, field)}:").pack(side=tk.LEFT)
            entry = ttk.Entry(frame)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
            # Setter nåværende verdi
            entry.insert(0, str(current_data.get(field, "")))
            entries[field] = entry
        
        # Legger til knapper nederst
        button_frame = ttk.Frame(form_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=lambda: self.save_edited_contact(entries, current_data, win)).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=win.destroy).pack(side=tk.RIGHT)

    # Funksjon for å lagre ny kontakt
    def save_new_contact(self, entries, window):
        try:
            fornavn = entries["Fornavn"].get().strip()
            etternavn = entries["Etternavn"].get().strip()
            adresse = entries["Adresse"].get().strip()
            postnr = entries["PostNr"].get().strip()
            if not fornavn or not etternavn:
                messagebox.showerror("Error", "First name and last name are required")
                return
            if self.app.db.add_contacts(fornavn, etternavn, adresse, postnr):
                self.show()
                window.destroy()
                messagebox.showinfo("Success", "Contact added successfully!")
            else:
                messagebox.showerror("Error", "Failed to add contact")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add contact: {str(e)}")
    
    # Funksjon for å lagre redigert kontakt
    def save_edited_contact(self, entries, current_data, window):
        try:
            fornavn = entries["Fornavn"].get().strip()
            etternavn = entries["Etternavn"].get().strip()
            adresse = entries["Adresse"].get().strip()
            postnr = entries["PostNr"].get().strip()
            if not fornavn or not etternavn:
                messagebox.showerror("Error", "First name and last name are required")
                return
            if self.app.db.edit_contacts(current_data["KNr"], fornavn, etternavn, adresse, postnr):
                self.show()
                window.destroy()
                messagebox.showinfo("Success", "Contact updated successfully!")
            else:
                messagebox.showerror("Error", "Failed to update contact")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update contact: {str(e)}")

    # Funksjon for å fjerne valgt kontakt
    def remove_selected_contact(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "No contact selected.")
            return
        current_values = self.tree.item(selected)['values']
        columns = self.tree["columns"]
        current_data = dict(zip(columns, current_values))
        if messagebox.askyesno("Confirm", "Are you sure you want to remove this contact?"):
            try:
                if self.app.db.remove_contacts(current_data["KNr"]):
                    self.show()
                    messagebox.showinfo("Success", "Contact removed successfully!")
                else:
                    messagebox.showerror("Error", "Failed to remove contact.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove contact: {str(e)}")