import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from config.database import init_db
from utils.styles import setup_theme
from views.dialogs.login_dialog import LoginDialog

if __name__ == '__main__':
    # Khởi tạo database
    init_db()

    # Khởi tạo ứng dụng
    app = QApplication(sys.argv)

    # Thiết lập icon cho ứng dụng
    logo_path = os.path.join("static", "images", "logo.png")
    if os.path.exists(logo_path):
        app.setWindowIcon(QIcon(logo_path))

    # Thiết lập theme cho toàn bộ ứng dụng
    setup_theme(app)

    # Tạo và hiển thị cửa sổ đăng nhập
    login_dialog = LoginDialog()
    login_dialog.show()

    # Chạy ứng dụng
    sys.exit(app.exec())
