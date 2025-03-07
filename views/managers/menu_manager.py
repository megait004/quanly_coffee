from PyQt6.QtWidgets import (QComboBox, QHBoxLayout, QHeaderView, QLabel,
                             QLineEdit, QMessageBox, QPushButton, QSpinBox,
                             QTableWidget, QTableWidgetItem, QVBoxLayout,
                             QWidget)

from config.database import create_connection


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
        menu_group = QVBoxLayout()
        menu_group.addWidget(QLabel("Thêm món mới"))

        # Form bên trái - thông tin món
        item_form = QHBoxLayout()

        # Cột thông tin cơ bản
        basic_info = QVBoxLayout()

        # Chọn danh mục
        category_select = QHBoxLayout()
        category_select.addWidget(QLabel("Danh mục:"))
        self.category_combo = QComboBox()
        category_select.addWidget(self.category_combo)
        basic_info.addLayout(category_select)

        # Tên món
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Tên món")
        basic_info.addWidget(self.name_input)

        # Mô tả
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Mô tả")
        basic_info.addWidget(self.description_input)

        item_form.addLayout(basic_info)

        # Cột giá và trạng thái
        price_status = QVBoxLayout()

        # Giá
        self.price_input = QSpinBox()
        self.price_input.setRange(0, 1000000)
        self.price_input.setSingleStep(1000)
        self.price_input.setSuffix(" VNĐ")
        self.price_input.setSpecialValueText("Giá")
        price_status.addWidget(self.price_input)

        # Trạng thái
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Trạng thái:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Có sẵn", "Hết hàng", "Ngừng kinh doanh"])
        status_layout.addWidget(self.status_combo)
        price_status.addLayout(status_layout)

        # Nút thêm món
        add_button = QPushButton("Thêm món")
        add_button.clicked.connect(self.add_item)
        price_status.addWidget(add_button)

        item_form.addLayout(price_status)
        menu_group.addLayout(item_form)
        layout.addLayout(menu_group)

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
                SELECT m.id, c.name as category_name, m.name, m.description, m.price, m.status
                FROM menu_items m
                LEFT JOIN categories c ON m.category_id = c.id
                ORDER BY c.name, m.name
            """)
            items = cursor.fetchall()

            self.table.setRowCount(len(items))
            for i, item in enumerate(items):
                # ID
                self.table.setItem(i, 0, QTableWidgetItem(str(item[0])))
                # Danh mục
                self.table.setItem(i, 1, QTableWidgetItem(
                    item[1] if item[1] else ""))
                # Tên món
                self.table.setItem(i, 2, QTableWidgetItem(item[2]))
                # Mô tả
                self.table.setItem(i, 3, QTableWidgetItem(
                    item[3] if item[3] else ""))
                # Giá
                self.table.setItem(i, 4, QTableWidgetItem(f"{item[4]:,} VNĐ"))

                # Trạng thái
                status_map = {
                    "available": "Có sẵn",
                    "out_of_stock": "Hết hàng",
                    "discontinued": "Ngừng kinh doanh"
                }
                status_combo = QComboBox()
                status_combo.addItems(
                    ["Có sẵn", "Hết hàng", "Ngừng kinh doanh"])
                status_combo.setCurrentText(status_map.get(item[5], "Có sẵn"))

                # Tạo mapping ngược để chuyển từ tiếng Việt sang giá trị trong database
                reverse_status_map = {v: k for k, v in status_map.items()}

                # Kết nối signal với lambda function để cập nhật trạng thái
                status_combo.currentTextChanged.connect(
                    lambda text, item_id=item[0]: self.update_item_status(
                        item_id, reverse_status_map[text]))

                self.table.setCellWidget(i, 5, status_combo)

                # Nút xóa
                delete_button = QPushButton("Xóa")
                delete_button.clicked.connect(
                    lambda checked, row=i: self.delete_menu_item(row))
                self.table.setCellWidget(i, 6, delete_button)

            conn.close()

    def add_item(self):
        category_name = self.category_combo.currentText()
        name = self.name_input.text().strip()
        description = self.description_input.text().strip()
        price = self.price_input.value()

        # Chuyển đổi trạng thái từ tiếng Việt sang giá trị database
        status_map = {
            "Có sẵn": "available",
            "Hết hàng": "out_of_stock",
            "Ngừng kinh doanh": "discontinued"
        }
        status = status_map[self.status_combo.currentText()]

        if not category_name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn danh mục!")
            return

        if not name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên món!")
            return

        if price <= 0:
            QMessageBox.warning(self, "Lỗi", "Giá phải lớn hơn 0!")
            return

        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO menu_items (category_id, name, description, price, status)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.categories[category_name], name, description, price, status))
                conn.commit()

                self.name_input.clear()
                self.description_input.clear()
                self.price_input.setValue(0)
                self.status_combo.setCurrentText("Có sẵn")

                self.load_menu_items()
                QMessageBox.information(self, "Thành công", "Đã thêm món mới!")
            except Exception as e:
                print(e)
                QMessageBox.warning(self, "Lỗi", "Không thể thêm món!")
            finally:
                conn.close()

    def update_item_status(self, item_id, new_status):
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE menu_items
                    SET status = ?
                    WHERE id = ?
                """, (new_status, item_id))
                conn.commit()
                QMessageBox.information(
                    self, "Thành công", "Đã cập nhật trạng thái!")
            except Exception as e:
                print(e)
                QMessageBox.warning(
                    self, "Lỗi", "Không thể cập nhật trạng thái!")
            finally:
                conn.close()

    def delete_menu_item(self, row):
        item_id = int(self.table.item(row, 0).text())

        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa món này?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            conn = create_connection()
            if conn is not None:
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        "DELETE FROM menu_items WHERE id = ?", (item_id,))
                    conn.commit()
                    self.load_menu_items()
                    QMessageBox.information(self, "Thành công", "Đã xóa món!")
                except Exception as e:
                    print(e)
                    QMessageBox.warning(self, "Lỗi", "Không thể xóa món!")
                finally:
                    conn.close()
