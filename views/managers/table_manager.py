from PyQt6.QtWidgets import (QComboBox, QHBoxLayout, QHeaderView, QLabel,
                             QMessageBox, QPushButton, QSpinBox, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from config.database import create_connection


class TableManager(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_tables()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Form thêm bàn
        form_layout = QHBoxLayout()

        # Số bàn
        number_layout = QVBoxLayout()
        number_layout.addWidget(QLabel("Số bàn:"))
        self.number_input = QSpinBox()
        self.number_input.setMinimum(1)
        self.number_input.setMaximum(100)
        number_layout.addWidget(self.number_input)
        form_layout.addLayout(number_layout)

        # Sức chứa
        capacity_layout = QVBoxLayout()
        capacity_layout.addWidget(QLabel("Sức chứa:"))
        self.capacity_input = QSpinBox()
        self.capacity_input.setMinimum(1)
        self.capacity_input.setMaximum(20)
        self.capacity_input.setValue(4)  # Default value
        capacity_layout.addWidget(self.capacity_input)
        form_layout.addLayout(capacity_layout)

        # Trạng thái
        status_layout = QVBoxLayout()
        status_layout.addWidget(QLabel("Trạng thái:"))
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Trống", "Đang sử dụng", "Đã đặt"])
        status_layout.addWidget(self.status_combo)
        form_layout.addLayout(status_layout)

        # Nút thêm
        add_button = QPushButton("Thêm bàn")
        add_button.clicked.connect(self.add_table)
        form_layout.addWidget(add_button)

        # Thêm stretch để đẩy các widget về bên trái
        form_layout.addStretch()

        layout.addLayout(form_layout)

        # Bảng danh sách bàn
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Số bàn", "Sức chứa", "Trạng thái", "Thao tác"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

    def load_tables(self):
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tables ORDER BY number")
            tables = cursor.fetchall()

            self.table.setRowCount(len(tables))
            for i, table in enumerate(tables):
                for j in range(4):
                    value = table[j]
                    if j == 3:  # Trạng thái
                        status_map = {
                            "available": "Trống",
                            "occupied": "Đang sử dụng",
                            "reserved": "Đã đặt"
                        }
                        value = status_map.get(value, value)
                    self.table.setItem(i, j, QTableWidgetItem(str(value)))

                # Thêm nút thao tác
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(0, 0, 0, 0)

                # Nút đổi trạng thái
                status_combo = QComboBox()
                status_combo.addItems(["Trống", "Đang sử dụng", "Đã đặt"])
                status_combo.setCurrentText(status_map.get(table[3], table[3]))
                status_combo.currentTextChanged.connect(
                    lambda status, row=i: self.change_status(row, status))
                action_layout.addWidget(status_combo)

                # Nút xóa
                delete_button = QPushButton("Xóa")
                delete_button.clicked.connect(
                    lambda checked, row=i: self.delete_table(row))
                action_layout.addWidget(delete_button)

                self.table.setCellWidget(i, 4, action_widget)

            conn.close()

    def add_table(self):
        number = self.number_input.value()
        capacity = self.capacity_input.value()
        status = self.status_combo.currentText()

        # Map status to database values
        status_map = {
            "Trống": "available",
            "Đang sử dụng": "occupied",
            "Đã đặt": "reserved"
        }
        status_db = status_map.get(status, "available")

        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO tables (number, capacity, status)
                    VALUES (?, ?, ?)
                """, (number, capacity, status_db))
                conn.commit()

                self.number_input.setValue(self.number_input.value() + 1)
                self.load_tables()
                QMessageBox.information(self, "Thành công", "Đã thêm bàn mới!")
            except Exception as e:
                print(e)
                QMessageBox.warning(self, "Lỗi", "Số bàn đã tồn tại!")
            finally:
                conn.close()

    def change_status(self, row, new_status):
        table_id = int(self.table.item(row, 0).text())

        # Map status to database values
        status_map = {
            "Trống": "available",
            "Đang sử dụng": "occupied",
            "Đã đặt": "reserved"
        }
        status_db = status_map.get(new_status, "available")

        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE tables
                    SET status = ?
                    WHERE id = ?
                """, (status_db, table_id))
                conn.commit()
                self.load_tables()
            except Exception as e:
                print(e)
                QMessageBox.warning(
                    self, "Lỗi", "Không thể cập nhật trạng thái bàn!")
            finally:
                conn.close()

    def delete_table(self, row):
        table_id = int(self.table.item(row, 0).text())

        # Kiểm tra xem bàn có đang được sử dụng không
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM orders
                WHERE table_id = ? AND status NOT IN ('completed', 'cancelled')
            """, (table_id,))
            if cursor.fetchone()[0] > 0:
                QMessageBox.warning(
                    self, "Lỗi", "Không thể xóa bàn đang có đơn hàng!")
                conn.close()
                return

            reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa bàn này?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    cursor.execute(
                        "DELETE FROM tables WHERE id = ?", (table_id,))
                    conn.commit()
                    self.load_tables()
                    QMessageBox.information(self, "Thành công", "Đã xóa bàn!")
                except Exception as e:
                    print(e)
                    QMessageBox.warning(self, "Lỗi", "Không thể xóa bàn!")
                finally:
                    conn.close()
