import hashlib
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QApplication, QComboBox, QDialog, QHBoxLayout,
                             QLabel, QLineEdit, QMessageBox, QPushButton,
                             QVBoxLayout)

from admin_window import AdminWindow
from customer_window import CustomerWindow
from database import (DEFAULT_ADMIN_PASSWORD, DEFAULT_ADMIN_USERNAME,
                      create_connection, init_db)
from staff_window import StaffWindow


class RegisterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Đăng ký")
        self.setMinimumWidth(400)
        layout = QVBoxLayout()

        # Title
        title = QLabel("ĐĂNG KÝ TÀI KHOẢN")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Tên đăng nhập")
        layout.addWidget(self.username_input)

        # Password
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mật khẩu")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        # Confirm Password
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Xác nhận mật khẩu")
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_password)

        # Full Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Họ và tên")
        layout.addWidget(self.name_input)

        # Email
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(self.email_input)

        # Phone
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Số điện thoại")
        layout.addWidget(self.phone_input)

        # Role selection
        role_layout = QHBoxLayout()
        role_layout.addWidget(QLabel("Vai trò:"))
        self.role_combo = QComboBox()
        self.role_combo.addItems(["customer", "staff"])
        role_layout.addWidget(self.role_combo)
        layout.addLayout(role_layout)

        # Register button
        register_button = QPushButton("Đăng ký")
        register_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        register_button.clicked.connect(self.try_register)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def try_register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_pass = self.confirm_password.text()
        name = self.name_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        role = self.role_combo.currentText()

        # Kiểm tra thông tin
        if not all([username, password, confirm_pass, name, email]):
            QMessageBox.warning(
                self, "Lỗi", "Vui lòng nhập đầy đủ thông tin bắt buộc!")
            return

        if password != confirm_pass:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp!")
            return

        # Kiểm tra username và email đã tồn tại chưa
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
            if cursor.fetchone():
                QMessageBox.warning(
                    self, "Lỗi", "Tên đăng nhập hoặc email đã tồn tại!")
                conn.close()
                return

            # Thêm user mới
            try:
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute("""
                    INSERT INTO users (username, password, role, email, phone)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, hashed_password, role, email, phone))

                user_id = cursor.lastrowid

                # Thêm thông tin bổ sung tùy theo role
                if role == "staff":
                    cursor.execute("""
                        INSERT INTO employees (user_id, name, position)
                        VALUES (?, ?, ?)
                    """, (user_id, name, "Staff"))
                else:  # customer
                    cursor.execute("""
                        INSERT INTO customers (user_id, name)
                        VALUES (?, ?)
                    """, (user_id, name))

                conn.commit()
                QMessageBox.information(
                    self, "Thành công", "Đăng ký tài khoản thành công!")
                self.accept()
            except Exception as e:
                print(e)
                QMessageBox.warning(self, "Lỗi", "Không thể tạo tài khoản!")
            finally:
                conn.close()


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.window = None

    def init_ui(self):
        self.setWindowTitle("Đăng nhập")
        self.setMinimumWidth(300)
        layout = QVBoxLayout()

        # Title
        title = QLabel("ĐĂNG NHẬP HỆ THỐNG")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Default admin credentials notice
        if self.check_admin_exists():
            admin_notice = QLabel(
                f"Tài khoản admin mặc định:\nUsername: {DEFAULT_ADMIN_USERNAME}\nPassword: {DEFAULT_ADMIN_PASSWORD}")
            admin_notice.setStyleSheet("color: #666; font-size: 12px;")
            admin_notice.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(admin_notice)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Tên đăng nhập")
        layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Mật khẩu")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        # Buttons layout
        buttons_layout = QHBoxLayout()

        # Login button
        login_button = QPushButton("Đăng nhập")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        login_button.clicked.connect(self.try_login)
        buttons_layout.addWidget(login_button)

        # Register button
        register_button = QPushButton("Đăng ký")
        register_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        register_button.clicked.connect(self.show_register)
        buttons_layout.addWidget(register_button)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def check_admin_exists(self):
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM users WHERE username = ? AND role = 'admin'", (DEFAULT_ADMIN_USERNAME,))
            count = cursor.fetchone()[0]
            conn.close()
            return count == 0
        return False

    def show_register(self):
        register_dialog = RegisterDialog()
        if register_dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(
                self, "Thông báo", "Vui lòng đăng nhập với tài khoản vừa tạo!")

    def try_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        # Kiểm tra đăng nhập
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            cursor.execute("""
                SELECT id, username, role FROM users
                WHERE username = ? AND password = ?
            """, (username, hashed_password))

            user = cursor.fetchone()
            conn.close()

            if user:
                self.user_id = user[0]
                self.username = user[1]
                self.role = user[2]
                self.show_main_window()
            else:
                QMessageBox.warning(
                    self, "Lỗi", "Sai tên đăng nhập hoặc mật khẩu!")

    def show_main_window(self):
        # Đóng cửa sổ cũ nếu có
        if self.window:
            self.window.close()

        # Tùy theo role để hiển thị giao diện tương ứng
        if self.role == 'admin':
            self.window = AdminWindow(self.user_id, self.username)
        elif self.role == 'staff':
            self.window = StaffWindow(self.user_id, self.username)
        else:  # customer
            self.window = CustomerWindow(self.user_id, self.username)

        # Kết nối signal logout từ main window
        self.window.logout_signal.connect(self.handle_logout)
        self.window.show()
        self.hide()

    def handle_logout(self):
        if self.window:
            self.window.close()
            self.window = None
        # Clear input fields
        self.username_input.clear()
        self.password_input.clear()
        # Show login dialog again
        self.show()


if __name__ == '__main__':
    # Khởi tạo database
    init_db()

    # Khởi tạo ứng dụng
    app = QApplication(sys.argv)

    # Hiển thị form đăng nhập
    login_dialog = LoginDialog()
    login_dialog.show()
    sys.exit(app.exec())
