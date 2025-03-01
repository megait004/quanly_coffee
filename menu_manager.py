from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox, QHBoxLayout,
                             QHeaderView, QLabel, QLineEdit, QMessageBox,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget)

from database import create_connection


class MenuManager(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_categories()
        self.load_menu_items()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Form quản lý danh mục
        category_group = QVBoxLayout()
        category_group.addWidget(QLabel("Quản lý Danh mục"))

        category_form = QHBoxLayout()
        self.category_name = QLineEdit()
        self.category_name.setPlaceholderText("Tên danh mục")
        category_form.addWidget(self.category_name)

        self.category_desc = QLineEdit()
        self.category_desc.setPlaceholderText("Mô tả")
        category_form.addWidget(self.category_desc)

        add_category_btn = QPushButton("Thêm danh mục")
        add_category_btn.clicked.connect(self.add_category)
        category_form.addWidget(add_category_btn)

        category_group.addLayout(category_form)
        layout.addLayout(category_group)

        # Form thêm món
        item_form = QHBoxLayout()

        # Chọn danh mục
        self.category_combo = QComboBox()
        item_form.addWidget(self.category_combo)

        # Tên món
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Tên món")
        item_form.addWidget(self.name_input)

        # Mô tả
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Mô tả")
        item_form.addWidget(self.desc_input)

        # Giá
        self.price_input = QDoubleSpinBox()
        self.price_input.setMinimum(0)
        self.price_input.setMaximum(1000000)
        self.price_input.setSuffix(" VNĐ")
        item_form.addWidget(self.price_input)

        # Trạng thái
        self.available_check = QCheckBox("Có sẵn")
        self.available_check.setChecked(True)
        item_form.addWidget(self.available_check)

        # Nút thêm
        add_button = QPushButton("Thêm món")
        add_button.clicked.connect(self.add_menu_item)
        item_form.addWidget(add_button)

        layout.addLayout(item_form)

        # Bảng menu
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Danh mục", "Tên món", "Mô tả", "Giá", "Trạng thái", "Thao tác"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

    def load_categories(self):
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM categories")
            categories = cursor.fetchall()

            self.category_combo.clear()
            self.categories = {cat[1]: cat[0] for cat in categories}
            self.category_combo.addItems(self.categories.keys())

            conn.close()

    def add_category(self):
        name = self.category_name.text()
        description = self.category_desc.text()

        if not name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên danh mục!")
            return

        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO categories (name, description)
                VALUES (?, ?)
            """, (name, description))
            conn.commit()
            conn.close()

            self.category_name.clear()
            self.category_desc.clear()
            self.load_categories()
            QMessageBox.information(
                self, "Thành công", "Đã thêm danh mục mới!")

    def load_menu_items(self):
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.id, c.name, m.name, m.description, m.price, m.available
                FROM menu_items m
                LEFT JOIN categories c ON m.category_id = c.id
            """)
            items = cursor.fetchall()

            self.table.setRowCount(len(items))
            for i, item in enumerate(items):
                for j in range(6):
                    value = item[j]
                    if j == 4:  # Giá
                        value = f"{value:,.0f} VNĐ"
                    elif j == 5:  # Trạng thái
                        value = "Có sẵn" if value else "Hết hàng"
                    self.table.setItem(i, j, QTableWidgetItem(str(value)))

                # Nút xóa
                delete_button = QPushButton("Xóa")
                delete_button.clicked.connect(
                    lambda checked, row=i: self.delete_menu_item(row))
                self.table.setCellWidget(i, 6, delete_button)

            conn.close()

    def add_menu_item(self):
        category_name = self.category_combo.currentText()
        name = self.name_input.text()
        description = self.desc_input.text()
        price = self.price_input.value()
        available = self.available_check.isChecked()

        if not all([category_name, name, price]):
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO menu_items (category_id, name, description, price, available)
                VALUES (?, ?, ?, ?, ?)
            """, (self.categories[category_name], name, description, price, available))
            conn.commit()
            conn.close()

            self.name_input.clear()
            self.desc_input.clear()
            self.price_input.setValue(0)
            self.available_check.setChecked(True)

            self.load_menu_items()
            QMessageBox.information(
                self, "Thành công", "Đã thêm món mới vào menu!")

    def delete_menu_item(self, row):
        item_id = int(self.table.item(row, 0).text())

        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa món này?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            conn = create_connection()
            if conn is not None:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM menu_items WHERE id = ?", (item_id,))
                conn.commit()
                conn.close()

                self.load_menu_items()
                QMessageBox.information(self, "Thành công", "Đã xóa món!")
