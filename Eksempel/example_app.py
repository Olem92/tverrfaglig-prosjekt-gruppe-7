import sqlite3
from tkinter import Tk, Frame, Label, Button, messagebox, Listbox, Scrollbar
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Database connection
def connect_db():
    conn = sqlite3.connect('inventory.db')  # Connect to the database
    return conn

# Function to fetch inventory items
def fetch_inventory():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT item_number, item_name, quantity, price FROM inventory")
    items = cursor.fetchall()
    conn.close()
    return items

# GUI setup and Order Management
def setup_gui():
    root = Tk()
    root.title("Inventory Management App")

    frame = Frame(root)
    frame.pack()

    Label(frame, text="Inventory Items").grid(row=0, column=0, columnspan=2)
    inventory_listbox = Listbox(frame)
    inventory_listbox.grid(row=1, column=0)

    scrollbar = Scrollbar(frame)
    scrollbar.grid(row=1, column=1, sticky='ns')
    inventory_listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=inventory_listbox.yview)

    items = fetch_inventory()
    for item in items:
        inventory_listbox.insert('end', f"{item[0]}: {item[1]}, Qty: {item[2]}, Price: {item[3]}")

    Button(frame, text="View Orders", command=view_orders).grid(row=len(items) + 1, column=0)
    Button(frame, text="Exit", command=root.quit).grid(row=len(items) + 1, column=1)

    root.mainloop()

# Function to fetch orders
def fetch_orders():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT order_id, customer_name, total_price FROM orders")
    orders = cursor.fetchall()
    conn.close()
    return orders

# Function to fetch customers
def fetch_customers():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id, customer_name FROM customers")
    customers = cursor.fetchall()
    conn.close()
    return customers

# Function to generate an invoice
def generate_invoice(order_id):
    print(f"Generating invoice for Order ID: {order_id}")  # Debugging statement
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    order = cursor.fetchone()
    if order:
        print(f"Order details: {order}")  # Debugging statement
        invoice_number = generate_unique_invoice_number()
        
        # Create a PDF invoice with error handling
        try:
            pdf_file = f"invoice_{invoice_number}.pdf"
            c = canvas.Canvas(pdf_file, pagesize=letter)
            c.drawString(100, 750, f"Invoice Number: {invoice_number}")
            c.drawString(100, 730, f"Order ID: {order[0]}")
            c.drawString(100, 710, f"Customer Name: {order[1]}")
            c.drawString(100, 690, f"Total Price: {order[2]}")
            c.save()
            print(f"Invoice saved as: {pdf_file}")  # Debugging statement
        except Exception as e:
            print(f"Error generating invoice: {e}")

        cursor.execute("INSERT INTO invoices (invoice_number, order_id) VALUES (?, ?)", (invoice_number, order_id))
        conn.commit()
    conn.close()

# Function to generate a unique invoice number
def generate_unique_invoice_number():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(invoice_number) FROM invoices")
    max_invoice_number = cursor.fetchone()[0]
    new_invoice_number = max_invoice_number + 1 if max_invoice_number else 1
    conn.close()
    return new_invoice_number

def add_customer(customer_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customers (customer_name) VALUES (?)", (customer_name,))
    conn.commit()
    conn.close()

# Function to remove a customer
def remove_customer(customer_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE customer_id = ?", (customer_id,))
    conn.commit()
    conn.close()

def view_customers():
    customers = fetch_customers()
    customer_window = Tk()
    customer_window.title("Customers")

    for index, customer in enumerate(customers):
        Label(customer_window, text=f"Customer ID: {customer[0]}, Name: {customer[1]}").pack()

    Button(customer_window, text="Close", command=customer_window.destroy).pack()
    Button(customer_window, text="Add Customer", command=lambda: add_customer("New Customer")).pack()
    Button(customer_window, text="Remove Customer", command=lambda: remove_customer(1)).pack()  # Example ID
    Button(customer_window, text="Generate Invoice", command=lambda: generate_invoice(1)).pack()  # Example Order ID

def view_orders():
    orders = fetch_orders()
    order_window = Tk()
    order_window.title("Orders")

    for index, order in enumerate(orders):
        Label(order_window, text=f"Order ID: {order[0]}, Customer: {order[1]}, Total: {order[2]}").pack()

    Button(order_window, text="Close", command=order_window.destroy).pack()
    Button(order_window, text="View Customers", command=view_customers).pack()

if __name__ == "__main__":
    setup_gui()
