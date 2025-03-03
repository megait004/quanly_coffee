import hashlib

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtWidgets import (QComboBox, QDialog, QLabel, QLineEdit,
                             QMessageBox, QPushButton, QVBoxLayout, QWidget)

from config.database import create_connection
from utils.styles import COLORS
from utils.validators import validate_email, validate_phone


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.drag_position = QPoint()

        # Thiết lập cửa sổ
        self.setWindowTitle("Đăng ký")
        self.setMinimumWidth(450)

        # Thiết lập window flags
        self.setWindowFlags(Qt.WindowType.Window)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {COLORS['surface']};
                border-radius: 10px;
                border: 1px solid {COLORS['border']};
            }}
            QLabel {{
                color: {COLORS['text']};
                font-size: 14px;
            }}
            QLineEdit {{
                padding: 8px;
                border-radius: 5px;
                border: 1px solid {COLORS['border']};
                background: white;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
            QPushButton {{
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                color: white;
            }}
            QPushButton#registerButton {{
                background-color: {COLORS['primary']};
            }}
            QPushButton#registerButton:hover {{
                background-color: {COLORS['primary_dark']};
            }}
            QComboBox {{
                padding: 8px;
                border-radius: 5px;
                border: 1px solid {COLORS['border']};
                background: white;
            }}
            QComboBox:focus {{
                border: 2px solid {COLORS['primary']};
            }}
        """)

        self.init_ui()

        # Đặt vị trí cửa sổ ở giữa màn hình
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Tiêu đề
        title = QLabel("ĐĂNG KÝ TÀI KHOẢN")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Form container
        form_container = QWidget()
        form_container.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['background']};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)

        # Username
        username_label = QLabel("Tên đăng nhập:")
        form_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập tên đăng nhập")
        form_layout.addWidget(self.username_input)

        # Password
        password_label = QLabel("Mật khẩu:")
        form_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Nhập mật khẩu")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.password_input)

        # Email
        email_label = QLabel("Email:")
        form_layout.addWidget(email_label)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Nhập email")
        self.email_input.textChanged.connect(self.validate_email)
        form_layout.addWidget(self.email_input)

        # Phone
        phone_label = QLabel("Số điện thoại:")
        form_layout.addWidget(phone_label)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Nhập số điện thoại")
        self.phone_input.setMaxLength(10)
        self.phone_input.textChanged.connect(self.validate_phone)
        form_layout.addWidget(self.phone_input)

        # Role
        role_label = QLabel("Vai trò:")
        form_layout.addWidget(role_label)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["customer", "staff"])
        form_layout.addWidget(self.role_combo)

        layout.addWidget(form_container)

        # Register button
        register_button = QPushButton("Đăng ký")
        register_button.setObjectName("registerButton")
        register_button.setFixedHeight(40)
        register_button.clicked.connect(self.register)
        layout.addWidget(register_button)

        self.setLayout(layout)

    def validate_email(self, email):
        """Kiểm tra định dạng email"""
        if not validate_email(email):
            self.email_input.setStyleSheet("""
                QLineEdit {
                    background-color: #ffebee;
                    border: 1px solid #e57373;
                }
            """)
        else:
            self.email_input.setStyleSheet("")

    def validate_phone(self, phone):
        """Kiểm tra định dạng số điện thoại"""
        if not validate_phone(phone):
            self.phone_input.setStyleSheet("""
                QLineEdit {
                    background-color: #ffebee;
                    border: 1px solid #e57373;
                }
            """)
        else:
            self.phone_input.setStyleSheet("")

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        email = self.email_input.text()
        phone = self.phone_input.text()
        role = self.role_combo.currentText()

        # Kiểm tra thông tin bắt buộc
        if not all([username, password, email]):
            QMessageBox.warning(
                self, "Lỗi", "Vui lòng nhập đầy đủ thông tin bắt buộc!")
            return

        # Kiểm tra định dạng email
        if not validate_email(email):
            QMessageBox.warning(
                self, "Lỗi", "Email không đúng định dạng!\nVí dụ: example@gmail.com")
            return

        # Kiểm tra số điện thoại
        if phone and not validate_phone(phone):
            QMessageBox.warning(
                self, "Lỗi", "Số điện thoại phải có 10 chữ số và bắt đầu bằng số 0!")
            return

        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                # Kiểm tra username và email đã tồn tại chưa
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
                """, (username, hashed_password, role, email, phone))

                # Thêm thông tin bổ sung tùy theo role
                user_id = cursor.lastrowid
                if role == 'staff':
                    cursor.execute("""
                        INSERT INTO employees (user_id, name, position)
                        VALUES (?, ?, ?)
                    """, (user_id, username, "Nhân viên mới"))
                else:  # customer
                    cursor.execute("""
                        INSERT INTO customers (user_id, name)
                        VALUES (?, ?)
                    """, (user_id, username))

                conn.commit()
                QMessageBox.information(
                    self, "Thành công", "Đăng ký tài khoản thành công!")
                self.accept()

            except Exception as e:
                print(e)
                QMessageBox.warning(
                    self, "Lỗi", "Không thể đăng ký tài khoản!")
            finally:
                conn.close()
