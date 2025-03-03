from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QComboBox, QDialog, QDoubleSpinBox, QHBoxLayout,
                             QHeaderView, QLabel, QLineEdit, QMessageBox,
                             QPushButton, QSpinBox, QTableWidget,
                             QTableWidgetItem, QTabWidget, QVBoxLayout,
                             QWidget)

from config.database import create_connection


class ImportDialog(QDialog):
    def __init__(self, item_id, item_name, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self.item_name = item_name
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Nhập kho")
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Thông tin sản phẩm
        layout.addWidget(QLabel(f"Sản phẩm: {self.item_name}"))

        # Số lượng nhập
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel("Số lượng:"))
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 10000)
        quantity_layout.addWidget(self.quantity_input)
        layout.addLayout(quantity_layout)

        # Giá nhập
        price_layout = QHBoxLayout()
        price_layout.addWidget(QLabel("Giá nhập:"))
        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 1000000000)
        self.price_input.setSuffix(" VNĐ")
        price_layout.addWidget(self.price_input)
        layout.addLayout(price_layout)

        # Nhà cung cấp
        supplier_layout = QHBoxLayout()
        supplier_layout.addWidget(QLabel("Nhà cung cấp:"))
        self.supplier_input = QLineEdit()
        supplier_layout.addWidget(self.supplier_input)
        layout.addLayout(supplier_layout)

        # Ghi chú
        note_layout = QHBoxLayout()
        note_layout.addWidget(QLabel("Ghi chú:"))
        self.note_input = QLineEdit()
        note_layout.addWidget(self.note_input)
        layout.addLayout(note_layout)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Lưu")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Hủy")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def get_data(self):
        return {
            'quantity': self.quantity_input.value(),
            'price': self.price_input.value(),
            'supplier': self.supplier_input.text(),
            'note': self.note_input.text()
        }


class InventoryManager(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Tạo tab widget
        tab_widget = QTabWidget()

        # Tab Tồn kho
        inventory_tab = QWidget()
        inventory_layout = QVBoxLayout()
        inventory_tab.setLayout(inventory_layout)

        # Form nhập liệu
        form_layout = QHBoxLayout()

        # Tên sản phẩm
        name_layout = QVBoxLayout()
        name_layout.addWidget(QLabel("Tên nguyên liệu:"))
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
        self.unit_input = QComboBox()
        self.unit_input.addItems(["g", "kg", "ml", "l", "cái", "gói", "hộp"])
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

        inventory_layout.addLayout(form_layout)

        # Bảng kho
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(7)
        self.inventory_table.setHorizontalHeaderLabels(
            ["ID", "Tên nguyên liệu", "Số lượng", "Đơn vị", "Ngưỡng cảnh báo", "Trạng thái", "Thao tác"])
        self.inventory_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        inventory_layout.addWidget(self.inventory_table)

        # Tab Lịch sử nhập/xuất
        history_tab = QWidget()
        history_layout = QVBoxLayout()
        history_tab.setLayout(history_layout)

        # Bảng lịch sử
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels(
            ["ID", "Ngày giờ", "Loại", "Sản phẩm", "Số lượng", "Đơn giá", "Nhà cung cấp", "Ghi chú"])
        self.history_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        history_layout.addWidget(self.history_table)

        # Thêm các tab
        tab_widget.addTab(inventory_tab, "Tồn kho")
        tab_widget.addTab(history_tab, "Lịch sử nhập/xuất")
        layout.addWidget(tab_widget)

        # Load dữ liệu
        self.load_inventory()
        self.load_history()

    def load_inventory(self):
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM inventory ORDER BY name")
            items = cursor.fetchall()

            self.inventory_table.setRowCount(len(items))
            for i, item in enumerate(items):
                for j in range(5):
                    self.inventory_table.setItem(
                        i, j, QTableWidgetItem(str(item[j])))

                # Trạng thái
                status = "Đủ hàng"
                if item[2] <= 0:  # quantity <= 0
                    status = "Hết hàng"
                elif item[2] <= item[4]:  # quantity <= threshold
                    status = "Sắp hết"

                status_item = QTableWidgetItem(status)
                if status == "Hết hàng":
                    status_item.setBackground(Qt.GlobalColor.red)
                elif status == "Sắp hết":
                    status_item.setBackground(Qt.GlobalColor.yellow)
                self.inventory_table.setItem(i, 5, status_item)

                # Buttons
                button_widget = QWidget()
                button_layout = QHBoxLayout(button_widget)
                button_layout.setContentsMargins(0, 0, 0, 0)

                # Nút nhập kho
                import_button = QPushButton("Nhập kho")
                import_button.clicked.connect(
                    lambda checked, row=i: self.show_import_dialog(row))
                button_layout.addWidget(import_button)

                # Nút xóa
                delete_button = QPushButton("Xóa")
                delete_button.clicked.connect(
                    lambda checked, row=i: self.delete_item(row))
                button_layout.addWidget(delete_button)

                self.inventory_table.setCellWidget(i, 6, button_widget)

            conn.close()

    def load_history(self):
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT h.id, h.timestamp, h.type, i.name, h.quantity, h.price, h.supplier, h.note
                FROM inventory_history h
                JOIN inventory i ON h.inventory_id = i.id
                ORDER BY h.timestamp DESC
            """)
            history = cursor.fetchall()

            self.history_table.setRowCount(len(history))
            for i, record in enumerate(history):
                # ID
                self.history_table.setItem(
                    i, 0, QTableWidgetItem(str(record[0])))
                # Thời gian
                timestamp = datetime.strptime(record[1], "%Y-%m-%d %H:%M:%S")
                self.history_table.setItem(i, 1, QTableWidgetItem(
                    timestamp.strftime("%d/%m/%Y %H:%M")))
                # Loại
                type_text = "Nhập kho" if record[2] == "import" else "Xuất kho"
                self.history_table.setItem(i, 2, QTableWidgetItem(type_text))
                # Sản phẩm
                self.history_table.setItem(i, 3, QTableWidgetItem(record[3]))
                # Số lượng
                self.history_table.setItem(
                    i, 4, QTableWidgetItem(str(record[4])))
                # Đơn giá
                self.history_table.setItem(
                    i, 5, QTableWidgetItem(f"{record[5]:,} VNĐ"))
                # Nhà cung cấp
                self.history_table.setItem(
                    i, 6, QTableWidgetItem(record[6] or ""))
                # Ghi chú
                self.history_table.setItem(
                    i, 7, QTableWidgetItem(record[7] or ""))

            conn.close()

    def show_import_dialog(self, row):
        item_id = int(self.inventory_table.item(row, 0).text())
        item_name = self.inventory_table.item(row, 1).text()

        dialog = ImportDialog(item_id, item_name, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.import_inventory(item_id, data)

    def import_inventory(self, item_id, data):
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()

                # Cập nhật số lượng trong kho
                cursor.execute("""
                    UPDATE inventory
                    SET quantity = quantity + ?
                    WHERE id = ?
                """, (data['quantity'], item_id))

                # Thêm lịch sử nhập kho
                cursor.execute("""
                    INSERT INTO inventory_history
                    (inventory_id, type, quantity, price, supplier, note, timestamp)
                    VALUES (?, 'import', ?, ?, ?, ?, datetime('now', 'localtime'))
                """, (item_id, data['quantity'], data['price'],
                      data['supplier'], data['note']))

                conn.commit()
                self.load_inventory()
                self.load_history()
                QMessageBox.information(
                    self, "Thành công", "Đã nhập kho thành công!")
            except Exception as e:
                print(e)
                QMessageBox.warning(self, "Lỗi", "Không thể nhập kho!")
            finally:
                conn.close()

    def add_item(self):
        name = self.name_input.text()
        quantity = self.quantity_input.value()
        unit = self.unit_input.currentText()
        threshold = self.threshold_input.value()

        if not name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên nguyên liệu!")
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
                    self, "Thành công", "Đã thêm nguyên liệu mới!")
            except Exception as e:
                print(e)
                QMessageBox.warning(self, "Lỗi", "Không thể thêm nguyên liệu!")
            finally:
                conn.close()

    def delete_item(self, row):
        item_id = int(self.inventory_table.item(row, 0).text())

        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa nguyên liệu này?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            conn = create_connection()
            if conn is not None:
                try:
                    cursor = conn.cursor()
                    # Xóa lịch sử trước
                    cursor.execute(
                        "DELETE FROM inventory_history WHERE inventory_id = ?", (item_id,))
                    # Sau đó xóa item
                    cursor.execute(
                        "DELETE FROM inventory WHERE id = ?", (item_id,))
                    conn.commit()
                    self.load_inventory()
                    self.load_history()
                    QMessageBox.information(
                        self, "Thành công", "Đã xóa nguyên liệu!")
                except Exception as e:
                    print(e)
                    QMessageBox.warning(
                        self, "Lỗi", "Không thể xóa nguyên liệu!")
                finally:
                    conn.close()

    def clear_inputs(self):
        self.name_input.clear()
        self.quantity_input.setValue(0)
        self.unit_input.setCurrentIndex(0)
        self.threshold_input.setValue(0)
