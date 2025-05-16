## Noe spesiell i forhold til de andre på grunn av furnksjonalitet rundt popups
import tkinter as tk
from tkinter import ttk, messagebox

class OrdersView:
    def __init__(self, app):
        self.app = app  # Reference to main App instance

    def show(self):
        # Clear existing content
        for widget in self.app.content.winfo_children():
            widget.destroy()

        self.app.current_view = "orders"

        # Search bar
        search_frame = ttk.Frame(self.app.content)
        search_frame.pack(fill=tk.X, padx=5, pady=(0, 5))

        search_var = tk.StringVar()
        selected_column = tk.StringVar(value="All")

        search_entry = ttk.Entry(search_frame, textvariable=search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        column_dropdown = ttk.Combobox(search_frame, textvariable=selected_column, state="readonly")
        column_dropdown.pack(side=tk.LEFT, padx=(5, 0))

        # Create frame for Treeview
        tree_frame = ttk.Frame(self.app.content)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create Treeview with scrollbar
        tree = ttk.Treeview(tree_frame)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Pack the Treeview and scrollbar
        tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # Hent ordre fra databasen
        try:
            orders_data = self.app.db.get_orders()
            if not orders_data:
                ttk.Label(tree_frame, text="No inventory data available").pack()
                return
            columns = list(orders_data[0].keys())
            tree["columns"] = columns
            column_dropdown["values"] = ["All"] + columns
            tree.column("#0", width=0, stretch=tk.NO)
            for col in columns:
                tree.column(col, anchor=tk.CENTER, width=100)
                tree.heading(col, text=col.title(), anchor=tk.CENTER)
            for item in orders_data:
                values = [item[col] for col in columns]
                tree.insert("", tk.END, values=values)
            self.app.bind_treeview_double_click(
                tree, columns,
                lambda item_dict: self.show_order_details_popup(item_dict)
            )

            # Search funksjonalitet
            def on_search_change(*_):
                col = selected_column.get()
                self.app.filter_tree(tree, orders_data, search_var.get(), column=None if col == "All" else col)
            search_var.trace_add("write", on_search_change)
            selected_column.trace_add("write", on_search_change)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load orders: {str(e)}")

    ## Popup for ordre detaljer, som åpnes ved dobbeltklikk
    def show_order_details_popup(self, order_dict):
        win = tk.Toplevel(self.app.root)
        self.app.register_popup(win)        ## registrer popup-vindu
        # Use order number in the title if available
        order_id = order_dict.get("OrdreNr") or list(order_dict.values())[0]
        win.title(f"{order_id} Order Contents")
        frame = ttk.Frame(win, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Create a top frame for two-column layout (customer left, order info right)
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        left_frame = ttk.Frame(top_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        right_frame = ttk.Frame(top_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.Y, anchor=tk.N)

        # Fetch order contents (which now includes Fornavn, Etternavn, Adresse, PostNr)
        contents = self.app.db.get_order_contents(order_id)
        if contents and 'Fornavn' in contents[0] and 'Etternavn' in contents[0]:
            customer_name = f"{contents[0]['Fornavn']} {contents[0]['Etternavn']}"
        else:
            customer_name = "Unknown"
        if contents and 'Adresse' in contents[0]:
            customer_address = contents[0]['Adresse']
        else:
            customer_address = "Unknown"
        if contents and 'PostNr' in contents[0]:
            customer_zip = contents[0]['PostNr']
        else:
            customer_zip = "Unknown"

        # Show customer info in left column
        row = ttk.Frame(left_frame)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Name:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        ttk.Label(row, text=customer_name, anchor=tk.W).pack(side=tk.LEFT)
        row = ttk.Frame(left_frame)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Adress:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        ttk.Label(row, text=customer_address, anchor=tk.W).pack(side=tk.LEFT)
        row = ttk.Frame(left_frame)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="ZIP Code:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        ttk.Label(row, text=customer_zip, anchor=tk.W).pack(side=tk.LEFT)

        # Show order info in right column
        translations = {
            "OrdreNr": "Order Number",
            "OrdreDato": "Order Date",
            "SendtDato": "Sent Date",
            "BetaltDato": "Paid Date",
            "KNr": "Customer Number"
        }
        for key in ["OrdreNr", "KNr", "OrdreDato", "SendtDato", "BetaltDato"]:
            value = order_dict.get(key, "")
            row = ttk.Frame(right_frame)
            row.pack(fill=tk.X, pady=2)
            label_text = translations.get(key, key)
            ttk.Label(row, text=f"{label_text}:", width=16, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(row, text=str(value), anchor=tk.W).pack(side=tk.LEFT)

        # Show order contents below both columns
        contents = self.app.db.get_order_contents(order_id) ## denne henter ekstra contents gjennom funksjonen get_order_contents
        if not contents:
            ttk.Label(frame, text="No contents found for this order.").pack()
        else:
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
            total_sum = 0
            for item in contents:
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
                total_sum += price_total
                values = [
                    str(item_name),
                    str(part_number),
                    int(quantity_val) if quantity_val == int(quantity_val) else quantity_val,
                    f"{price_per_item_val:,.2f}",
                    f"{price_total:,.2f}"
                ]
                tree.insert("", tk.END, values=values)

            # Totalsum helt i bunn, right-aligned, same font/size as order info rows
            total_row = ttk.Frame(frame)
            total_row.pack(fill=tk.X, pady=(10, 2))
            ttk.Label(total_row, text=f"{total_sum:,.2f}", anchor=tk.E, font=("Helvetica", 10)).pack(side=tk.RIGHT)
            ttk.Label(total_row, text="Total:", width=12, anchor=tk.E, font=("Helvetica", 10)).pack(side=tk.RIGHT)
