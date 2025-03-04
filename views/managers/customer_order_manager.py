from datetime import datetime

from PyQt6.QtWidgets import (QComboBox, QHBoxLayout, QHeaderView, QLabel,
                             QPushButton, QSpinBox, QTableWidget,
                             QTableWidgetItem, QVBoxLayout)

from config.database import create_connection
from views.managers.order_manager import OrderManager


class CustomerOrderManager(OrderManager):
    def __init__(self, user_id):
        super().__init__(user_id, is_staff=False)

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Form tạo đơn hàng mới
        form_layout = QVBoxLayout()

        # Chọn bàn
        table_layout = QHBoxLayout()
        table_layout.addWidget(QLabel("Bàn:"))
        self.table_combo = QComboBox()
        self.load_tables()
        table_layout.addWidget(self.table_combo)
        form_layout.addLayout(table_layout)

        # Chọn sản phẩm
        self.product_combo = QComboBox()
        self.load_products()
        product_layout = QHBoxLayout()
        product_layout.addWidget(QLabel("Sản phẩm:"))
        product_layout.addWidget(self.product_combo)

        # Số lượng
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(100)
        product_layout.addWidget(QLabel("Số lượng:"))
        product_layout.addWidget(self.quantity_spin)

        # Nút thêm vào đơn hàng
        add_to_order_button = QPushButton("Thêm vào đơn hàng")
        add_to_order_button.clicked.connect(self.add_to_order)
        product_layout.addWidget(add_to_order_button)

        form_layout.addLayout(product_layout)

        # Bảng đơn hàng hiện tại
        self.current_order_table = QTableWidget()
        self.current_order_table.setColumnCount(5)
        self.current_order_table.setHorizontalHeaderLabels(
            ["ID", "Tên sản phẩm", "Số lượng", "Đơn giá", "Thành tiền"])
        self.current_order_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        form_layout.addWidget(self.current_order_table)

        # Tổng tiền và nút hoàn tất
        total_layout = QHBoxLayout()
        self.total_label = QLabel("Tổng tiền: 0 VNĐ")
        total_layout.addWidget(self.total_label)

        complete_button = QPushButton("Đặt món")
        complete_button.clicked.connect(self.complete_order)
        total_layout.addWidget(complete_button)

        form_layout.addLayout(total_layout)
        layout.addLayout(form_layout)

        # Bảng lịch sử đơn hàng
        self.order_history_table = QTableWidget()
        self.order_history_table.setColumnCount(5)  # Bỏ cột thao tác
        self.order_history_table.setHorizontalHeaderLabels(
            ["ID", "Bàn", "Thời gian", "Tổng tiền", "Trạng thái"])
        self.order_history_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.order_history_table)

        # Load lịch sử đơn hàng
        self.load_orders()

    def load_orders(self):
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.id, t.number, o.created_at, o.total_amount, o.status
                FROM orders o
                LEFT JOIN tables t ON o.table_id = t.id
                WHERE o.user_id = ?
                ORDER BY o.created_at DESC
            """, (self.user_id,))
            orders = cursor.fetchall()

            self.order_history_table.setRowCount(len(orders))
            for i, order in enumerate(orders):
                # ID
                self.order_history_table.setItem(
                    i, 0, QTableWidgetItem(str(order[0])))
                # Bàn
                self.order_history_table.setItem(
                    i, 1, QTableWidgetItem(f"Bàn {order[1]}"))
                # Thời gian
                time = datetime.strptime(
                    order[2], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
                self.order_history_table.setItem(i, 2, QTableWidgetItem(time))
                # Tổng tiền
                self.order_history_table.setItem(
                    i, 3, QTableWidgetItem(f"{order[3]:,} VNĐ"))
                # Trạng thái
                status_map = {
                    "pending": "Chờ xử lý",
                    "preparing": "Đang chuẩn bị",
                    "served": "Đã phục vụ",
                    "completed": "Hoàn thành",
                    "cancelled": "Đã hủy"
                }
                self.order_history_table.setItem(
                    i, 4, QTableWidgetItem(status_map.get(order[4], order[4])))

            conn.close()
