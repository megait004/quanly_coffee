from PyQt6.QtWidgets import (QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                             QMessageBox, QPushButton, QSpinBox, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from database import create_connection


class InventoryManager(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_inventory()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Form nhập liệu
        form_layout = QHBoxLayout()

        # Tên sản phẩm
        name_layout = QVBoxLayout()
        name_layout.addWidget(QLabel("Tên sản phẩm:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        form_layout.addLayout(name_layout)

        # Số lượng
        quantity_layout = QVBoxLayout()
        quantity_layout.addWidget(QLabel("Số lượng:"))
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 10000)
        quantity_layout.addWidget(self.quantity_input)
        form_layout.addLayout(quantity_layout)

        # Đơn vị
        unit_layout = QVBoxLayout()
        unit_layout.addWidget(QLabel("Đơn vị:"))
        self.unit_input = QLineEdit()
        unit_layout.addWidget(self.unit_input)
        form_layout.addLayout(unit_layout)

        # Ngưỡng cảnh báo
        threshold_layout = QVBoxLayout()
        threshold_layout.addWidget(QLabel("Ngưỡng cảnh báo:"))
        self.threshold_input = QSpinBox()
        self.threshold_input.setRange(0, 1000)
        threshold_layout.addWidget(self.threshold_input)
        form_layout.addLayout(threshold_layout)

        # Nút thêm
        add_button = QPushButton("Thêm")
        add_button.clicked.connect(self.add_item)
        form_layout.addWidget(add_button)

        layout.addLayout(form_layout)

        # Bảng kho
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Tên sản phẩm", "Số lượng", "Đơn vị", "Ngưỡng cảnh báo", "Thao tác"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

    def load_inventory(self):
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM inventory ORDER BY name")
            items = cursor.fetchall()

            self.table.setRowCount(len(items))
            for i, item in enumerate(items):
                for j in range(5):
                    self.table.setItem(i, j, QTableWidgetItem(str(item[j])))

                # Highlight items below threshold
                if item[2] <= item[4]:  # quantity <= threshold
                    for j in range(5):
                        cell = self.table.item(i, j)
                        cell.setBackground(Qt.GlobalColor.yellow)

                # Nút xóa
                delete_button = QPushButton("Xóa")
                delete_button.clicked.connect(
                    lambda checked, row=i: self.delete_item(row))
                self.table.setCellWidget(i, 5, delete_button)

            conn.close()

    def add_item(self):
        name = self.name_input.text()
        quantity = self.quantity_input.value()
        unit = self.unit_input.text()
        threshold = self.threshold_input.value()

        if not all([name, unit]):
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO inventory (name, quantity, unit, threshold)
                    VALUES (?, ?, ?, ?)
                """, (name, quantity, unit, threshold))
                conn.commit()

                self.clear_inputs()
                self.load_inventory()
                QMessageBox.information(
                    self, "Thành công", "Đã thêm sản phẩm vào kho!")
            except Exception as e:
                print(e)
                QMessageBox.warning(self, "Lỗi", "Không thể thêm sản phẩm!")
            finally:
                conn.close()

    def delete_item(self, row):
        item_id = int(self.table.item(row, 0).text())

        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa sản phẩm này?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            conn = create_connection()
            if conn is not None:
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        "DELETE FROM inventory WHERE id = ?", (item_id,))
                    conn.commit()
                    self.load_inventory()
                    QMessageBox.information(
                        self, "Thành công", "Đã xóa sản phẩm!")
                except Exception as e:
                    print(e)
                    QMessageBox.warning(self, "Lỗi", "Không thể xóa sản phẩm!")
                finally:
                    conn.close()

    def clear_inputs(self):
        self.name_input.clear()
        self.quantity_input.setValue(0)
        self.unit_input.clear()
        self.threshold_input.setValue(0)
