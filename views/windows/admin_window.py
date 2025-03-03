from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QMainWindow, QMessageBox,
                             QPushButton, QStackedWidget, QVBoxLayout, QWidget)

from views.managers.employee_manager import EmployeeManager
from views.managers.inventory_manager import InventoryManager
from views.managers.menu_manager import MenuManager
from views.managers.report_manager import ReportManager


class AdminWindow(QMainWindow):
    logout_signal = pyqtSignal()

    def __init__(self, user_id, username):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Quản lý Quán Cà Phê - Admin Panel")
        self.setMinimumSize(1200, 800)

        # Widget chính
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("ADMIN PANEL")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title)

        user_info = QLabel(f"Admin: {self.username}")
        user_info.setAlignment(Qt.AlignmentFlag.AlignRight)
        header_layout.addWidget(user_info)

        layout.addLayout(header_layout)

        # Content area
        content_layout = QHBoxLayout()

        # Sidebar menu
        menu_layout = QVBoxLayout()
        self.create_menu_buttons(menu_layout)
        content_layout.addLayout(menu_layout, 1)

        # Main content area
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget, 4)

        layout.addLayout(content_layout)

        # Thêm các trang quản lý
        self.employee_manager = EmployeeManager()
        self.menu_manager = MenuManager()
        self.inventory_manager = InventoryManager()
        self.report_manager = ReportManager()

        self.stacked_widget.addWidget(self.employee_manager)
        self.stacked_widget.addWidget(self.menu_manager)
        self.stacked_widget.addWidget(self.inventory_manager)
        self.stacked_widget.addWidget(self.report_manager)

    def create_menu_buttons(self, layout):
        buttons = [
            ("Quản lý Nhân viên", lambda: self.stacked_widget.setCurrentWidget(
                self.employee_manager)),
            ("Quản lý Menu", lambda: self.stacked_widget.setCurrentWidget(
                self.menu_manager)),
            ("Quản lý Kho", lambda: self.stacked_widget.setCurrentWidget(
                self.inventory_manager)),
            ("Báo cáo & Thống kê", lambda: self.stacked_widget.setCurrentWidget(
                self.report_manager))
        ]

        for text, slot in buttons:
            button = QPushButton(text)
            button.setMinimumHeight(50)
            button.setStyleSheet("""
                QPushButton {
                    background-color: #2c3e50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 16px;
                    text-align: left;
                    padding-left: 20px;
                }
                QPushButton:hover {
                    background-color: #34495e;
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
