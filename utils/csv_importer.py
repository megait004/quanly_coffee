import csv
import hashlib

from config.database import create_connection


class CSVImporter:
    @staticmethod
    def import_categories(file_path):
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    cursor.execute("""
                        INSERT INTO categories (name, description)
                        VALUES (?, ?)
                    """, (row['name'], row['description']))
            conn.commit()
            conn.close()

    @staticmethod
    def import_menu_items(file_path):
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    cursor.execute("""
                        INSERT INTO menu_items (category_id, name, description, price, available)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        int(row['category_id']),
                        row['name'],
                        row['description'],
                        float(row['price']),
                        int(row['available'])
                    ))
            conn.commit()
            conn.close()

    @staticmethod
    def import_users(file_path):
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    # Hash mật khẩu
                    hashed_password = hashlib.sha256(
                        row['password'].encode()).hexdigest()

                    # Thêm user
                    cursor.execute("""
                        INSERT INTO users (username, password, role, email, phone)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        row['username'],
                        hashed_password,
                        row['role'],
                        row['email'],
                        row['phone']
                    ))

                    user_id = cursor.lastrowid

                    # Thêm thông tin bổ sung tùy theo role
                    if row['role'] == 'staff':
                        cursor.execute("""
                            INSERT INTO employees (user_id, name, position, salary)
                            VALUES (?, ?, ?, ?)
                        """, (
                            user_id,
                            row['name'],
                            row['position'],
                            float(row['salary'])
                        ))
                    elif row['role'] == 'customer':
                        cursor.execute("""
                            INSERT INTO customers (user_id, name)
                            VALUES (?, ?)
                        """, (user_id, row['name']))

            conn.commit()
            conn.close()

    @staticmethod
    def import_tables(file_path):
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    cursor.execute("""
                        INSERT INTO tables (number, capacity, status)
                        VALUES (?, ?, ?)
                    """, (
                        int(row['number']),
                        int(row['capacity']),
                        row['status']
                    ))
            conn.commit()
            conn.close()

    @staticmethod
    def import_inventory(file_path):
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    cursor.execute("""
                        INSERT INTO inventory (name, quantity, unit, threshold)
                        VALUES (?, ?, ?, ?)
                    """, (
                        row['name'],
                        int(row['quantity']),
                        row['unit'],
                        int(row['threshold'])
                    ))
            conn.commit()
            conn.close()
