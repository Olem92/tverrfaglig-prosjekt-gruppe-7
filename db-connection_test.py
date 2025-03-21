import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve values from environment variables
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

# Connect to MySQL
mydb = mysql.connector.connect(
    host=DATABASE_HOST,
    user=DATABASE_USER,
    password=DATABASE_PASSWORD
)

mycursor = mydb.cursor()

# Create a database
mycursor.execute("CREATE DATABASE testDB_python")

print("Database created successfully!")
