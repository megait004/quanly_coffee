import sqlite3
from sqlite3 import Error

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"


def create_connection():
    try:
        conn = sqlite3.connect('database.db')
        return conn
    except Error as e:
        print(e)
        return None


def create_tables(conn):
    try:
        cursor = conn.cursor()

        # Bảng Users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT CHECK (role IN ('admin', 'staff', 'customer')) NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Bảng Categories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT
            )
        ''')

        # Bảng Menu Items
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                available BOOLEAN DEFAULT 1,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')

        # Bảng Orders
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                table_id INTEGER,
                status TEXT CHECK (status IN ('pending', 'preparing', 'served', 'completed', 'cancelled')) NOT NULL,
                total_amount REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (table_id) REFERENCES tables(id)
            )
        ''')

        # Bảng Order Items
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                menu_item_id INTEGER,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
            )
        ''')

        # Bảng Tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number INTEGER UNIQUE NOT NULL,
                capacity INTEGER NOT NULL,
                status TEXT CHECK (status IN ('available', 'occupied', 'reserved')) NOT NULL
            )
        ''')

        # Bảng Employees
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                name TEXT NOT NULL,
                position TEXT NOT NULL,
                salary REAL,
                shift_start TIME,
                shift_end TIME,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Bảng Customers
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                name TEXT NOT NULL,
                loyalty_points INTEGER DEFAULT 0,
                member_since DATE DEFAULT CURRENT_DATE,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Bảng Inventory
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit TEXT NOT NULL,
                threshold INTEGER NOT NULL
            )
        ''')

        # Tạo tài khoản admin mặc định nếu chưa tồn tại
        cursor.execute("SELECT id FROM users WHERE username = ?",
                       (DEFAULT_ADMIN_USERNAME,))
        if not cursor.fetchone():
            import hashlib
            admin_password = hashlib.sha256(
                DEFAULT_ADMIN_PASSWORD.encode()).hexdigest()
            cursor.execute("""
                INSERT INTO users (username, password, role, email)
                VALUES (?, ?, ?, ?)
            """, (DEFAULT_ADMIN_USERNAME, admin_password, 'admin', 'admin@coffee.com'))

            # Thêm thông tin employee cho admin
            cursor.execute("""
                INSERT INTO employees (user_id, name, position, salary)
                VALUES (last_insert_rowid(), 'Administrator', 'Admin', 0)
            """)

        conn.commit()
    except Error as e:
        print(e)


def init_db():
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        conn.close()
    else:
        print("Error! Cannot create the database connection.")
