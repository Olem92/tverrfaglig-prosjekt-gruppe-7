import tkinter as tk
from tkinter import ttk, messagebox

class ContactsView:
    def __init__(self, app):
        self.app = app

    def show(self):
        for widget in self.app.content.winfo_children():
            widget.destroy()
        self.app.current_view = "contacts"
        search_frame = ttk.Frame(self.app.content)
        search_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        search_var = tk.StringVar()
        selected_column = tk.StringVar(value="All")
        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        column_dropdown = ttk.Combobox(search_frame, textvariable=selected_column, state="readonly")
        column_dropdown.pack(side=tk.LEFT, padx=(5, 0))
        tree_frame = ttk.Frame(self.app.content)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        tree = ttk.Treeview(tree_frame)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
        try:
            contacts_data = self.app.db.get_contacts()
            if not contacts_data:
                ttk.Label(tree_frame, text="No contact data available").pack()
                return
            columns = list(contacts_data[0].keys())
            tree["columns"] = columns
            column_dropdown["values"] = ["All"] + columns
            tree.column("#0", width=0, stretch=tk.NO)
            for col in columns:
                tree.column(col, anchor=tk.CENTER, width=100)
                tree.heading(col, text=col.title(), anchor=tk.CENTER)
            for item in contacts_data:
                values = [item[col] for col in columns]
                tree.insert("", tk.END, values=values)
            self.app.bind_treeview_double_click(
                tree, columns,
                lambda item_dict: self.app.show_details_popup("Contact Details", item_dict)
            )
            def on_search_change(*_):
                col = selected_column.get()
                self.app.filter_tree(tree, contacts_data, search_var.get(), column=None if col == "All" else col)
            search_var.trace_add("write", on_search_change)
            selected_column.trace_add("write", on_search_change)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load contacts: {str(e)}")

    def show_details_popup(self, title, item_dict):
        win = tk.Toplevel(self.app.root)
        self.app.register_popup(win)
        win.title(title)
        frame = ttk.Frame(win, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        for key, value in item_dict.items():
            row = ttk.Frame(frame)
            row.pack(fill=tk.X, pady=2)
            ttk.Label(row, text=f"{key}:", width=20, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(row, text=str(value), anchor=tk.W).pack(side=tk.LEFT)
