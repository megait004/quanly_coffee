import hashlib
import os

from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QDialog, QHBoxLayout, QLabel, QLineEdit,
                             QMessageBox, QPushButton, QVBoxLayout, QWidget)

from config.database import DEFAULT_ADMIN_USERNAME, create_connection
from utils.styles import COLORS
from views.dialogs.register_dialog import RegisterDialog
from views.windows.admin_window import AdminWindow
from views.windows.customer_window import CustomerWindow
from views.windows.staff_window import StaffWindow


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.window = None
        self.drag_position = QPoint()

        # Thiết lập cửa sổ
        self.setWindowTitle("Đăng nhập")
        self.setFixedSize(400, 650)  # Tăng chiều cao để chứa logo

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
            QPushButton#loginButton {{
                background-color: {COLORS['primary']};
            }}
            QPushButton#loginButton:hover {{
                background-color: {COLORS['primary_dark']};
            }}
            QPushButton#registerButton {{
                background-color: {COLORS['secondary']};
            }}
            QPushButton#registerButton:hover {{
                background-color: {COLORS['secondary_dark']};
            }}
        """)

        # Khởi tạo giao diện
        self.init_ui()

        # Đặt vị trí cửa sổ ở giữa màn hình
        self.center_on_screen()

    def center_on_screen(self):
        """Đặt cửa sổ ở giữa màn hình"""
        screen = self.screen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Logo
        logo_label = QLabel()
        logo_path = os.path.join("static", "images", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Scale logo to fit width while maintaining aspect ratio
            scaled_pixmap = pixmap.scaledToWidth(
                200, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(logo_label)

        # Tiêu đề
        title = QLabel("Café Tranquiilité")
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            margin: 10px 0;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("ĐĂNG NHẬP HỆ THỐNG")
        subtitle.setStyleSheet("""
            font-size: 18px;
            color: #7f8c8d;
            margin-bottom: 20px;
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

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

        # Username input
        username_label = QLabel("Tên đăng nhập:")
        form_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập tên đăng nhập")
        form_layout.addWidget(self.username_input)

        # Password input
        password_label = QLabel("Mật khẩu:")
        form_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Nhập mật khẩu")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addWidget(self.password_input)

        layout.addWidget(form_container)

        # Buttons container
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(10)

        # Login button
        login_button = QPushButton("Đăng nhập")
        login_button.setObjectName("loginButton")
        login_button.setFixedHeight(40)
        login_button.clicked.connect(self.try_login)
        buttons_layout.addWidget(login_button)

        # Register button
        register_button = QPushButton("Đăng ký")
        register_button.setObjectName("registerButton")
        register_button.setFixedHeight(40)
        register_button.clicked.connect(self.show_register)
        buttons_layout.addWidget(register_button)

        layout.addWidget(buttons_container)

        # Add stretch to push everything up
        layout.addStretch()

        self.setLayout(layout)

    def show_register(self):
        register_dialog = RegisterDialog(self)
        if register_dialog.exec() == QDialog.DialogCode.Accepted:
            QMessageBox.information(
                self, "Thông báo", "Vui lòng đăng nhập với tài khoản vừa tạo!")

    def try_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(
                self, "Lỗi", "Vui lòng nhập đầy đủ thông tin đăng nhập!")
            return

        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()
                hashed_password = hashlib.sha256(password.encode()).hexdigest()

                cursor.execute("""
                    SELECT id, role FROM users
                    WHERE username = ? AND password = ?
                """, (username, hashed_password))

                user = cursor.fetchone()

                if user:
                    user_id, role = user
                    self.show_main_window(user_id, username, role)
                else:
                    QMessageBox.warning(
                        self, "Lỗi", "Tên đăng nhập hoặc mật khẩu không đúng!")

            except Exception as e:
                print(e)
                QMessageBox.warning(
                    self, "Lỗi", "Có lỗi xảy ra khi đăng nhập!")
            finally:
                conn.close()

    def show_main_window(self, user_id, username, role):
        # Đóng cửa sổ cũ nếu có
        if self.window:
            self.window.close()

        # Mở cửa sổ mới theo role
        if role == 'admin':
            self.window = AdminWindow(user_id, username)
        elif role == 'staff':
            self.window = StaffWindow(user_id, username)
        else:
            self.window = CustomerWindow(user_id, username)

        # Kết nối signal logout
        self.window.logout_signal.connect(self.handle_logout)

        # Hiển thị cửa sổ mới
        self.window.show()
        self.hide()

    def handle_logout(self):
        """Xử lý khi người dùng đăng xuất"""
        if self.window:
            self.window.close()
            self.window = None

        # Clear input fields
        self.username_input.clear()
        self.password_input.clear()

        # Show login dialog again
        self.show()
        self.center_on_screen()

    def check_admin_exists(self):
        """Kiểm tra xem tài khoản admin mặc định đã tồn tại chưa"""
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username = ?", (DEFAULT_ADMIN_USERNAME,))
            exists = cursor.fetchone() is not None
            conn.close()
            return exists
        return False


if __name__ == "__main__":
    import sys

    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    login_dialog = LoginDialog()
    login_dialog.show()
    sys.exit(app.exec())
