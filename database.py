import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

## Databaseklasse som håndterer tilkobling og forespørsler til databasen
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

## Kobler til databasen
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

## Sjekker om tilkoblingen er aktiv
    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Connection closed")

## Henter ordre via Stored Procedures
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

## Henter lagerbeholdning via Stored Procedures
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

## Henter kontakter via Stored Procedures
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
    
## Henter antall kontakter via Stored Procedures
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

## Henter ordreinnhold via Stored Procedures
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
