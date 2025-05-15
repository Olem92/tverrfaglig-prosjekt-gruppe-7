import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os


class VarehusDatabase:
    def __init__(self):
        load_dotenv()

        self.host = os.getenv("DATABASE_HOST")
        self.port = os.getenv("DATABASE_PORT")
        self.user = os.getenv("DATABASE_USER")
        self.password = os.getenv("DATABASE_PASSWORD")
        self.database = os.getenv("DATABASE_NAME")
        self.connection = None
        print(f"Connecting to {self.database} on {self.host}:{self.port} as {self.user}")

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to the database")
        except Error as e:
            print(e)

    def insert_data(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO example_table (name) VALUES ('Sample Data')")
            self.connection.commit()
            print("Initial data inserted into 'example_table'.")
        except Error as e:
            print(f"Error inserting data into table. {e}")
        finally:
            cursor.close()

    def delete_data(self, record_id):
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM example_table WHERE id = %s", (record_id,))
            deleted_rows = cursor.rowcount
            self.connection.commit()
            if deleted_rows > 0:
                print(f"Deleted {deleted_rows} record(s) with ID {record_id}.")
            else:
                print(f"No record found with ID {record_id}.")
        except Error as e:
            print(f"Error deleting data from 'example_table': {e}")
            self.connection.rollback()  # Rollback in case of error
        finally:
            cursor.close()

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Connection closed")

    def get_orders(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.callproc('ShowOrders')
            # Fetch results from the stored procedure
            for result in cursor.stored_results():
                return result.fetchall()
        except Exception as e:
            print(f"Error fetching orders: {e}")
            return []
        finally:
            cursor.close()

    def get_inventory(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.callproc('ShowInventory')
            # Fetch results from the stored procedure
            for result in cursor.stored_results():
                return result.fetchall()
        except Exception as e:
            print(f"Error fetching inventory: {e}")
            return []
        finally:
            cursor.close()

    def get_contacts(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.callproc('ShowContacts')
            # Fetch results from the stored procedure
            for result in cursor.stored_results():
                return result.fetchall()
        except Exception as e:
            print(f"Error fetching inventory: {e}")
            return []
        finally:
            cursor.close()
    
    def get_contacts_amount(self):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.callproc('ShowContactsAmount')
            # Fetch results from the stored procedure
            for result in cursor.stored_results():
                return result.fetchall()
        except Exception as e:
            print(f"Error fetching inventory: {e}")
            return []
        finally:
            cursor.close()

    def get_order_contents(self, order_id):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.callproc('ShowOrderContents', (order_id,))
            for result in cursor.stored_results():
                return result.fetchall()
        except Exception as e:
            print(f"Error fetching order contents: {e}")
            return []
        finally:
            cursor.close()
