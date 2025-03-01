from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QMainWindow, QMessageBox,
                             QPushButton, QStackedWidget, QVBoxLayout, QWidget)

from order_manager import OrderManager
from table_manager import TableManager


class StaffWindow(QMainWindow):
    logout_signal = pyqtSignal()

    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Quản lý Quán Cà Phê - Nhân viên")
        self.setMinimumSize(1000, 700)

        # Widget chính
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("QUẢN LÝ BÁN HÀNG")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)

        user_info = QLabel(f"Nhân viên: {self.username}")
        user_info.setAlignment(Qt.AlignmentFlag.AlignRight)
        header_layout.addWidget(user_info)

        layout.addLayout(header_layout)

        # Content area
        content_layout = QHBoxLayout()

        # Menu buttons
        menu_layout = QVBoxLayout()
        self.create_menu_buttons(menu_layout)
        content_layout.addLayout(menu_layout, 1)

        # Main content area
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget, 4)

        layout.addLayout(content_layout)

        # Thêm các trang quản lý
        self.order_manager = OrderManager(self.user_id)
        self.table_manager = TableManager()

        self.stacked_widget.addWidget(self.order_manager)
        self.stacked_widget.addWidget(self.table_manager)

    def create_menu_buttons(self, layout):
        buttons = [
            ("Quản lý Đơn hàng", lambda: self.stacked_widget.setCurrentWidget(
                self.order_manager)),
            ("Quản lý Bàn", lambda: self.stacked_widget.setCurrentWidget(
                self.table_manager))
        ]

        for text, slot in buttons:
            button = QPushButton(text)
            button.setMinimumHeight(50)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #2980b9;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 16px;
                    text-align: left;
                    padding-left: 20px;
                }
                QPushButton:hover {
                    background-color: #3498db;
                }
            """)
            button.clicked.connect(slot)
            layout.addWidget(button)

        # Thêm khoảng trống
        layout.addStretch()

        # Nút đăng xuất
        logout_button = QPushButton("Đăng xuất")
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        logout_button.clicked.connect(self.logout)
        layout.addWidget(logout_button)

    def logout(self):
        reply = QMessageBox.question(self, "Xác nhận", "Bạn có chắc muốn đăng xuất?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.logout_signal.emit()
            self.close()
