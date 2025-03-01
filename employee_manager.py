import hashlib

from PyQt6.QtWidgets import (QComboBox, QHBoxLayout, QHeaderView, QLineEdit,
                             QMessageBox, QPushButton, QSpinBox, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from database import create_connection


class EmployeeManager(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_employees()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Form nhập liệu
        form_layout = QHBoxLayout()

        # Tên đăng nhập
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Tên đăng nhập")
        form_layout.addWidget(self.username_input)

        # Mật khẩu
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mật khẩu")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.password_input)

        # Họ tên
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Họ và tên")
        form_layout.addWidget(self.name_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        form_layout.addWidget(self.email_input)

        # Số điện thoại
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Số điện thoại")
        form_layout.addWidget(self.phone_input)

        # Chức vụ
        self.position_input = QComboBox()
        self.position_input.addItems(
            ["Staff", "Manager", "Cashier", "Barista"])
        form_layout.addWidget(self.position_input)

        # Lương
        self.salary_input = QSpinBox()
        self.salary_input.setRange(0, 100000000)
        self.salary_input.setSingleStep(1000000)
        self.salary_input.setSuffix(" VNĐ")
        form_layout.addWidget(self.salary_input)

        # Nút thêm
        add_button = QPushButton("Thêm")
        add_button.clicked.connect(self.add_employee)
        form_layout.addWidget(add_button)

        layout.addLayout(form_layout)

        # Bảng nhân viên
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Tên đăng nhập", "Họ tên", "Email", "SĐT", "Chức vụ", "Lương", "Thao tác"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

    def load_employees(self):
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.id, u.username, e.name, u.email, u.phone, e.position, e.salary
                FROM users u
                JOIN employees e ON u.id = e.user_id
                WHERE u.role = 'staff'
                ORDER BY e.name
            """)
            employees = cursor.fetchall()

            self.table.setRowCount(len(employees))
            for i, emp in enumerate(employees):
                for j in range(7):
                    value = emp[j]
                    if j == 6:  # Lương
                        value = f"{value:,} VNĐ" if value else "0 VNĐ"
                    self.table.setItem(i, j, QTableWidgetItem(
                        str(value) if value is not None else ""))

                # Nút xóa
                delete_button = QPushButton("Xóa")
                delete_button.clicked.connect(
                    lambda checked, row=i: self.delete_employee(row))
                self.table.setCellWidget(i, 7, delete_button)

            conn.close()

    def add_employee(self):
        username = self.username_input.text()
        password = self.password_input.text()
        name = self.name_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        position = self.position_input.currentText()
        salary = self.salary_input.value()

        if not all([username, password, name, email]):
            QMessageBox.warning(
                self, "Lỗi", "Vui lòng nhập đầy đủ thông tin bắt buộc!")
            return

        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            try:
                # Kiểm tra username và email
                cursor.execute(
                    "SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
                if cursor.fetchone():
                    QMessageBox.warning(
                        self, "Lỗi", "Tên đăng nhập hoặc email đã tồn tại!")
                    return

                # Thêm user mới
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO users (username, password, role, email, phone)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, hashed_password, 'staff', email, phone))

                # Thêm thông tin employee
                cursor.execute("""
                    INSERT INTO employees (user_id, name, position, salary)
                    VALUES (last_insert_rowid(), ?, ?, ?)
                """, (name, position, salary))

                conn.commit()
                self.clear_inputs()
                self.load_employees()
                QMessageBox.information(
                    self, "Thành công", "Đã thêm nhân viên mới!")

            except Exception as e:
                print(e)
                QMessageBox.warning(self, "Lỗi", "Không thể thêm nhân viên!")
            finally:
                conn.close()

    def delete_employee(self, row):
        user_id = int(self.table.item(row, 0).text())

        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn xóa nhân viên này?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            conn = create_connection()
            if conn is not None:
                try:
                    cursor = conn.cursor()
                    # Xóa từ bảng employees trước
                    cursor.execute(
                        "DELETE FROM employees WHERE user_id = ?", (user_id,))
                    # Sau đó xóa từ bảng users
                    cursor.execute(
                        "DELETE FROM users WHERE id = ?", (user_id,))
                    conn.commit()
                    self.load_employees()
                    QMessageBox.information(
                        self, "Thành công", "Đã xóa nhân viên!")
                except Exception as e:
                    print(e)
                    QMessageBox.warning(
                        self, "Lỗi", "Không thể xóa nhân viên!")
                finally:
                    conn.close()

    def clear_inputs(self):
        self.username_input.clear()
        self.password_input.clear()
        self.name_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.position_input.setCurrentIndex(0)
        self.salary_input.setValue(0)
