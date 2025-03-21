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

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Connection closed")
