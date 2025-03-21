import sqlite3

def create_database():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Create inventory table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            item_number INTEGER PRIMARY KEY,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL
        )
    ''')

    # Create orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            total_price REAL NOT NULL
        )
    ''')

    # Create customers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL
        )
    ''')

    # Create invoices table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            invoice_number INTEGER PRIMARY KEY,
            order_id INTEGER,
            FOREIGN KEY (order_id) REFERENCES orders (order_id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
