# 📦 **Warehouse Mini ERP System**

Welcome to the **Warehouse Mini ERP System** – a modern, user-friendly solution for managing your warehouse's inventory, orders, and contacts.

---

## 🚀 **Features**

- 🗃️ **Inventory Management:** Track stock levels, search and filter products, and keep your warehouse organized.
- 📦 **Order Handling:** View, search, and manage customer orders with ease and accuracy.
- 📇 **Contact Directory:** Maintain a searchable list of customers.
- ✏️ **Contact Management:** Add, edit, and remove customers via web or desktop GUI.
- 🌐 **Modern Web Interface:** FastAPI, Jinja2 templates, and custom CSS.
- 🖥️ **Desktop GUI:** Tkinter-based application for local management.

---

## 🛠️ **Installation**

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Olem92/tverrfaglig-prosjekt-gruppe-7.git
cd tverrfaglig-prosjekt-gruppe-7
```

### 2️⃣ Install Python & MySQL

- [Python 3.10+](https://www.python.org/downloads/)
- [MySQL Server](https://dev.mysql.com/downloads/installer/)

### 3️⃣ Configure Database Access

Add a `.env` file in the root directory with your MySQL credentials, or use the provided `.env` example as a template:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=varehusdb
```

---

### 4️⃣ Install Dependencies & Set Up Database

#### Install Python dependencies:

```bash
pip install -r requirements.txt
```

#### Set up your MySQL database by running the SQL script in your MySQL client:

```bash
mysql -u your_mysql_user -p varehusdb < sql-db/varehusdb.sql
```

_Alternatively, run the contents of `varehusdb.sql` manually. File location:_
```
tverrfaglig-prosjekt-gruppe-7/sql-db/varehusdb.sql
```

---

### 5️⃣ Add Stored Procedures and changes to the Database:

Run the contents of the `varehusdb_changes.sql` either through your MySQL client or manually in a query:
```bash
mysql -u your_mysql_user -p varehusdb < sql-db/varehusdb_changes.sql
```

---

## 🏃 **Usage**

Start the application (web and desktop GUI):

```bash
python app.py
```

---

## 📚 **Project Structure**

```text
tverrfaglig-prosjekt-gruppe-7/
├── app.py                         # Tkinter GUI & FastAPI web server
├── api.py                         # API endpoints and calls
├── database.py                    # DB connection logic and functions
├── requirements.txt               # Python dependencies
├── sql-db/varehusdb.sql           # Sample database
├── sql-db/varehusdb_changes.sql   # Stored Procedures and database changes
├── views/                         # Tkinter GUI modules
├── templates/                     # FastAPI Jinja2 HTML templates
├── static/                        # CSS & Image files
└── .env                           # Environment variables
```

---

## ⚙️ **Key Components**

- **SQL Schema:**
  - Tables for inventory, orders, contacts, etc.
  - Stored procedures for contact management (`AddContacts`, `EditContacts`, `RemoveContacts`).
- **Backend:**
  - FastAPI for REST endpoints and web pages.
  - Robust error handling and clear API responses.
- **Frontend:**
  - Jinja2 templates for web UI.
  - Tkinter for desktop GUI.
  - HTML templates pushed through FastAPI.

---

## 🧪 **Testing & Debugging**

- ✅ All core features (add/edit/remove/search contacts) are tested in both web and desktop GUIs.
- ⚠️ Error messages are shown for failed operations (e.g., DB connection issues).

---

## 🤝 **Credits**

Developed by 24ITDNett Group 7, 2025. For questions or contributions, please open an issue or pull request.

---

## 📄 **License**

This project is licensed for educational use. See LICENSE for details.
