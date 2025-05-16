## Noe spesiell i forhold til de andre på grunn av furnksjonalitet rundt popups
import tkinter as tk
from tkinter import ttk, messagebox
from views.translations.no_en_translation import NO_EN_TRANSLATION
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import datetime
import webbrowser
import os

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
            
            # Reinsert all orders
            for item in orders_data:
                values = [item[col] for col in columns]
                tree.insert("", tk.END, values=values)
        
        # Bind focus events
        search_entry.bind('<FocusIn>', on_focus_in)
        search_entry.bind('<FocusOut>', on_focus_out)
        
        # Add clear button
        clear_button = ttk.Button(search_frame, text="✕", width=3, command=clear_search)
        clear_button.pack(side=tk.LEFT, padx=(5, 0))

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
            # Create a mapping of translated column names to original column names
            column_mapping = {NO_EN_TRANSLATION.get(col, col): col for col in columns}
            column_dropdown["values"] = ["All"] + list(column_mapping.keys())  # Populate dropdown with translated column names
            tree.column("#0", width=0, stretch=tk.NO)
            for col in columns:
                tree.column(col, anchor=tk.CENTER, width=100)
                # Use translation if available, otherwise use the original column name
                translated_col = NO_EN_TRANSLATION.get(col, col)
                tree.heading(col, text=translated_col, anchor=tk.CENTER)
            for item in orders_data:
                values = [item[col] for col in columns]
                tree.insert("", tk.END, values=values)
            self.app.bind_treeview_double_click(
                tree, columns,
                lambda item_dict: self.show_order_details_popup(item_dict)
            )

            # Search funksjonalitet
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
                self.app.filter_tree(tree, orders_data, search_text, column=original_col)
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
        ttk.Label(row, text="Address:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        ttk.Label(row, text=customer_address, anchor=tk.W).pack(side=tk.LEFT)
        row = ttk.Frame(left_frame)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="ZIP Code:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        ttk.Label(row, text=customer_zip, anchor=tk.W).pack(side=tk.LEFT)

        # Show order info in right column
        for key in ["OrdreNr", "KNr", "OrdreDato", "SendtDato", "BetaltDato"]:
            value = order_dict.get(key, "")
            row = ttk.Frame(right_frame)
            row.pack(fill=tk.X, pady=2)
            # Use translation if available, otherwise use the original key
            translated_key = NO_EN_TRANSLATION.get(key, key)
            ttk.Label(row, text=f"{translated_key}:", width=16, anchor=tk.W).pack(side=tk.LEFT)
            ttk.Label(row, text=str(value), anchor=tk.W).pack(side=tk.LEFT)

        # Show order contents below both columns
        contents = self.app.db.get_order_contents(order_id)
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

        # Add PDF export button (bottom left)
        def generate_pdf_and_open():
            self.generate_invoice_pdf(order_dict)
        pdf_btn = ttk.Button(frame, text="Generate Invoice PDF", command=generate_pdf_and_open)
        pdf_btn.pack(side=tk.LEFT, anchor=tk.SW, pady=8)

    def generate_invoice_pdf(self, order_dict):
        order_id = order_dict.get("OrdreNr") or list(order_dict.values())[0]
        contents = self.app.db.get_order_contents(order_id)
        if not contents:
            messagebox.showerror("PDF Error", "No order contents found.")
            return
        customer_name = f"{contents[0].get('Fornavn', '')} {contents[0].get('Etternavn', '')}".strip()
        customer_address = contents[0].get('Adresse', '')
        customer_zip = contents[0].get('PostNr', '')
        order_date = order_dict.get('OrdreDato', str(datetime.date.today()))
        pdf_dir = os.path.join(os.path.dirname(__file__), '..', 'pdf-exports')
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.abspath(os.path.join(pdf_dir, f"invoice_{order_id}.pdf"))
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        y = height - 30 * mm
        # Add logo to top right
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'icons', 'gpt-logo.png'))
        if os.path.exists(logo_path):
            try:
                c.drawImage(logo_path, width - 50 * mm, height - 35 * mm, width=30 * mm, height=30 * mm, preserveAspectRatio=True, mask='auto')
            except Exception as e:
                print(f"Could not add logo: {e}")
        c.setFont("Helvetica-Bold", 16)
        c.drawString(20 * mm, y, "INVOICE")
        y -= 12 * mm
        c.setFont("Helvetica", 10)
        c.drawString(20 * mm, y, f"Order #: {order_id}")
        c.drawString(100 * mm, y, f"Date: {order_date}")
        y -= 8 * mm
        c.drawString(20 * mm, y, f"Customer: {customer_name}")
        y -= 6 * mm
        c.drawString(20 * mm, y, f"Address: {customer_address}")
        y -= 6 * mm
        c.drawString(20 * mm, y, f"ZIP: {customer_zip}")
        y -= 12 * mm
        c.setFont("Helvetica-Bold", 10)
        c.drawString(20 * mm, y, "Item")
        c.drawString(70 * mm, y, "Item No.")
        c.drawString(100 * mm, y, "Qty")
        c.drawString(120 * mm, y, "Unit Price")
        c.drawString(150 * mm, y, "Total")
        y -= 6 * mm
        c.setFont("Helvetica", 10)
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
            c.drawString(20 * mm, y, str(item_name))
            c.drawString(70 * mm, y, str(part_number))
            c.drawRightString(110 * mm, y, str(int(quantity_val) if quantity_val == int(quantity_val) else quantity_val))
            c.drawRightString(135 * mm, y, f"{price_per_item_val:,.2f}")
            c.drawRightString(180 * mm, y, f"{price_total:,.2f}")
            y -= 6 * mm
            if y < 30 * mm:
                c.showPage()
                y = height - 30 * mm
        c.setFont("Helvetica-Bold", 12)
        c.drawString(120 * mm, y-4*mm, "Total:")
        c.drawRightString(180 * mm, y-4*mm, f"{total_sum:,.2f}")
        c.save()
        webbrowser.open_new(pdf_path)
