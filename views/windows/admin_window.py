from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, pyqtSignal
from PyQt6.QtWidgets import (QFrame, QHBoxLayout, QLabel, QMainWindow,
                             QMessageBox, QPushButton, QStackedWidget,
                             QVBoxLayout, QWidget)

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
        self.current_button = None
        self.init_ui()
        self.setup_animations()

    def init_ui(self):
        self.setWindowTitle("Quản lý Quán Cà Phê - Admin Panel")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
        """)

        # Widget chính
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        main_widget.setLayout(layout)

        # Header
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1a237e, stop:1 #0d47a1);
                border-bottom: 2px solid #1565c0;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        # Logo và tiêu đề
        title_layout = QHBoxLayout()
        title = QLabel("ADMIN DASHBOARD")
        title.setStyleSheet("""
            QLabel {
                color: #d59595;
                font-size: 26px;
                font-weight: bold;
                font-family: 'Segoe UI', Arial;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                letter-spacing: 1px;
                background: transparent;
            }
        """)
        title_layout.addWidget(title)
        header_layout.addLayout(title_layout)

        # User info
        user_info = QLabel(f"Xin chào, {self.username}")
        user_info.setStyleSheet("""
            QLabel {
                color: #96aab9;
                font-size: 15px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial;
                text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
            }
        """)
        user_info.setAlignment(Qt.AlignmentFlag.AlignRight)
        header_layout.addWidget(user_info)

        layout.addWidget(header)

        # Content area
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: #878a8f;
            }
        """)
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Sidebar menu
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #cf9999;
                border-right: 1px solid #e0e0e0;
            }
        """)
        menu_layout = QVBoxLayout(sidebar)
        menu_layout.setContentsMargins(10, 20, 10, 20)
        menu_layout.setSpacing(10)
        self.create_menu_buttons(menu_layout)
        content_layout.addWidget(sidebar)

        # Main content area
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("""
            QStackedWidget {
                background-color: #d6b1b1;
                border-radius: 10px;
                margin: 20px;
            }
        """)
        content_layout.addWidget(self.stacked_widget)

        layout.addWidget(content_widget)

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
            ("Quản lý Nhân viên", "👥", lambda: self.change_page(self.employee_manager)),
            ("Quản lý Menu", "🍽️", lambda: self.change_page(self.menu_manager)),
            ("Quản lý Kho", "📦", lambda: self.change_page(self.inventory_manager)),
            ("Báo cáo & Thống kê", "📊", lambda: self.change_page(self.report_manager))
        ]

        for text, icon, slot in buttons:
            button = QPushButton(f"{icon} {text}")
            button.setMinimumHeight(50)
            button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #424242;
                    border: none;
                    border-radius: 8px;
                    padding: 10px;
                    font-size: 14px;
                    font-weight: 500;
                    text-align: left;
                    font-family: 'Segoe UI', Arial;
                }
                QPushButton:hover {
                    background-color: #f5f5f5;
                    color: #1565c0;
                }
                QPushButton[active="true"] {
                    background-color: #e3f2fd;
                    color: #1565c0;
                    font-weight: bold;
                }
            """)
            button.clicked.connect(slot)
            layout.addWidget(button)

        # Thêm khoảng trống
        layout.addStretch()

        # Nút đăng xuất
        logout_button = QPushButton("🚪 Đăng xuất")
        logout_button.setMinimumHeight(50)
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #ffebee;
                color: #d32f2f;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial;
            }
            QPushButton:hover {
                background-color: #ffcdd2;
            }
        """)
        logout_button.clicked.connect(self.logout)
        layout.addWidget(logout_button)

    def setup_animations(self):
        self.page_animation = QPropertyAnimation(
            self.stacked_widget, b"geometry")
        self.page_animation.setDuration(300)
        self.page_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def change_page(self, widget):
        # Cập nhật trạng thái active của buttons
        sender = self.sender()
        if self.current_button:
            self.current_button.setProperty("active", False)
            self.current_button.setStyle(self.current_button.style())
        sender.setProperty("active", True)
        sender.setStyle(sender.style())
        self.current_button = sender

        # Animation khi chuyển trang
        self.stacked_widget.setCurrentWidget(widget)

    def logout(self):
        reply = QMessageBox.question(
            self,
            "Xác nhận đăng xuất",
            "Bạn có chắc muốn đăng xuất khỏi hệ thống?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.logout_signal.emit()
            self.close()
