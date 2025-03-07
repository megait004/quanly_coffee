import os
import sqlite3
from pathlib import Path
from sqlite3 import Error

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "admin123"


def get_db_path():
    """Lấy đường dẫn tới file database"""
    # Lấy đường dẫn thư mục home của user
    home_dir = str(Path.home())

    # Tạo thư mục .coffee_shop trong thư mục home nếu chưa tồn tại
    app_dir = os.path.join(home_dir, '.coffee_shop')
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)

    # Đường dẫn tới file database
    db_path = os.path.join(app_dir, 'coffee_shop.db')
    return db_path


def reset_database():
    """Xóa và tạo lại database"""
    db_path = get_db_path()

    # Xóa file database cũ nếu tồn tại
    if os.path.exists(db_path):
        os.remove(db_path)

    # Tạo database mới
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        initialize_default_data(conn)
        conn.close()
    else:
        print("Error! Cannot create the database connection.")


def initialize_default_data(conn):
    """Khởi tạo dữ liệu mặc định"""
    try:
        cursor = conn.cursor()

        # Tạo tài khoản admin mặc định
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

        # Tạo một số danh mục mặc định
        categories = [
            ("Cà phê", "Các loại cà phê"),
            ("Trà", "Các loại trà"),
            ("Nước ép", "Nước ép trái cây tươi"),
            ("Sinh tố", "Các loại sinh tố")
        ]
        cursor.executemany("""
            INSERT INTO categories (name, description)
            VALUES (?, ?)
        """, categories)

        # Tạo một số bàn mặc định
        tables = [(i, 4, 'available')
                  for i in range(1, 11)]  # 10 bàn, mỗi bàn 4 chỗ
        cursor.executemany("""
            INSERT INTO tables (number, capacity, status)
            VALUES (?, ?, ?)
        """, tables)

        conn.commit()
    except Error as e:
        print(e)


def create_connection():
    """Tạo kết nối tới database"""
    conn = None
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)

        # Tạo các bảng nếu chưa tồn tại
        create_tables(conn)
        return conn
    except sqlite3.Error as e:
        print(e)
        if conn:
            conn.close()
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

        # Bảng Tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                number INTEGER UNIQUE NOT NULL,
                capacity INTEGER NOT NULL,
                status TEXT CHECK (status IN ('available', 'occupied', 'reserved')) NOT NULL DEFAULT 'available'
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
                status TEXT CHECK (status IN ('available', 'out_of_stock', 'discontinued')) NOT NULL DEFAULT 'available',
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
                name TEXT NOT NULL UNIQUE,
                quantity INTEGER DEFAULT 0,
                unit TEXT NOT NULL,
                threshold INTEGER DEFAULT 0
            )
        ''')

        # Bảng Inventory History
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER NOT NULL,
                type TEXT NOT NULL,  -- 'import' hoặc 'export'
                quantity INTEGER NOT NULL,
                price REAL,
                supplier TEXT,
                note TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inventory_id) REFERENCES inventory (id)
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
