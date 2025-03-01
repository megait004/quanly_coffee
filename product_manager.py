from PyQt6.QtWidgets import (QHBoxLayout, QHeaderView, QLineEdit, QMessageBox,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget)

from database import create_connection


class ProductManager(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_products()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Form nhập liệu
        form_layout = QHBoxLayout()

        # Tên sản phẩm
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Tên sản phẩm")
        form_layout.addWidget(self.name_input)

        # Giá
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Giá")
        form_layout.addWidget(self.price_input)

        # Danh mục
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Danh mục")
        form_layout.addWidget(self.category_input)

        # Nút thêm
        add_button = QPushButton("Thêm")
        add_button.clicked.connect(self.add_product)
        form_layout.addWidget(add_button)

        layout.addLayout(form_layout)

        # Bảng sản phẩm
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Tên", "Giá", "Danh mục", "Thao tác"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

    def load_products(self):
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM products")
            products = cursor.fetchall()

            self.table.setRowCount(len(products))
            for i, product in enumerate(products):
                self.table.setItem(i, 0, QTableWidgetItem(str(product[0])))
                self.table.setItem(i, 1, QTableWidgetItem(product[1]))
                self.table.setItem(i, 2, QTableWidgetItem(str(product[2])))
                self.table.setItem(i, 3, QTableWidgetItem(product[3]))

                # Nút xóa
                delete_button = QPushButton("Xóa")
                delete_button.clicked.connect(
                    lambda checked, row=i: self.delete_product(row))
                self.table.setCellWidget(i, 4, delete_button)

            conn.close()

    def add_product(self):
        name = self.name_input.text()
        price = self.price_input.text()
        category = self.category_input.text()

        if not name or not price:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        try:
            price = float(price)
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Giá phải là số!")
            return

        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO products (name, price, category)
                VALUES (?, ?, ?)
            """, (name, price, category))
            conn.commit()
            conn.close()

            self.name_input.clear()
            self.price_input.clear()
            self.category_input.clear()
            self.load_products()

    def delete_product(self, row):
        product_id = int(self.table.item(row, 0).text())

        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa sản phẩm này?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            conn = create_connection()
            if conn is not None:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM products WHERE id = ?", (product_id,))
                conn.commit()
                conn.close()
                self.load_products()
