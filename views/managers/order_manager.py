from datetime import datetime

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QBrush, QColor, QIcon
from PyQt6.QtWidgets import (QComboBox, QHBoxLayout, QHeaderView, QLabel,
                             QMessageBox, QPushButton, QSpinBox,
                             QSystemTrayIcon, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget)

from config.database import create_connection


class OrderManager(QWidget):
    def __init__(self, user_id, is_staff=True):
        super().__init__()
        self.user_id = user_id
        self.is_staff = is_staff
        self.last_order_id = 0  # Lưu ID đơn hàng cuối cùng đã kiểm tra
        self.init_ui()
        self.current_order_items = []

        # Tạo timer để cập nhật thời gian và kiểm tra đơn hàng mới
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_new_orders)
        self.timer.start(5000)  # Kiểm tra mỗi 5 giây

        # Khởi tạo system tray icon cho thông báo
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("assets/icon.png"))

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

        complete_button = QPushButton("Hoàn tất đơn hàng")
        complete_button.clicked.connect(self.complete_order)
        total_layout.addWidget(complete_button)

        form_layout.addLayout(total_layout)
        layout.addLayout(form_layout)

        # Bảng lịch sử đơn hàng
        self.order_history_table = QTableWidget()
        # Thêm cột cho nút cập nhật trạng thái
        self.order_history_table.setColumnCount(6)
        self.order_history_table.setHorizontalHeaderLabels(
            ["ID", "Bàn", "Thời gian", "Tổng tiền", "Trạng thái", "Thao tác"])
        self.order_history_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.order_history_table)

        # Load lịch sử đơn hàng
        self.load_orders()

    def load_tables(self):
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, number, status FROM tables WHERE status = 'available' ORDER BY number")
            tables = cursor.fetchall()

            self.tables = {f"Bàn {table[1]}": table[0] for table in tables}
            self.table_combo.clear()
            self.table_combo.addItems(self.tables.keys())

            conn.close()

    def load_products(self):
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT m.id, m.name, m.price, m.status
                FROM menu_items m
                WHERE m.status = 'available'
                ORDER BY m.name
            """)
            products = cursor.fetchall()

            self.products = {f"{product[1]} - {product[2]:,} VNĐ": {
                "id": product[0], "price": product[2]} for product in products}
            self.product_combo.clear()
            self.product_combo.addItems(self.products.keys())

            conn.close()

    def add_to_order(self):
        if not self.table_combo.currentText():
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn bàn trước!")
            return

        selected_product = self.product_combo.currentText()
        quantity = self.quantity_spin.value()

        product_id = self.products[selected_product]["id"]
        price = self.products[selected_product]["price"]
        product_name = selected_product.split(" - ")[0]

        # Thêm vào danh sách đơn hàng hiện tại
        self.current_order_items.append({
            "product_id": product_id,
            "name": product_name,
            "quantity": quantity,
            "price": price
        })

        self.update_current_order_table()

    def update_current_order_table(self):
        self.current_order_table.setRowCount(len(self.current_order_items))
        total = 0

        for i, item in enumerate(self.current_order_items):
            self.current_order_table.setItem(
                i, 0, QTableWidgetItem(str(item["product_id"])))
            self.current_order_table.setItem(
                i, 1, QTableWidgetItem(item["name"]))
            self.current_order_table.setItem(
                i, 2, QTableWidgetItem(str(item["quantity"])))
            self.current_order_table.setItem(
                i, 3, QTableWidgetItem(f"{item['price']:,} VNĐ"))

            subtotal = item["quantity"] * item["price"]
            total += subtotal
            self.current_order_table.setItem(
                i, 4, QTableWidgetItem(f"{subtotal:,} VNĐ"))

        self.total_label.setText(f"Tổng tiền: {total:,} VNĐ")

    def complete_order(self):
        if not self.current_order_items:
            QMessageBox.warning(
                self, "Lỗi", "Vui lòng thêm sản phẩm vào đơn hàng!")
            return

        table_name = self.table_combo.currentText()
        if not table_name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn bàn!")
            return

        table_id = self.tables[table_name]

        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()

                # Tạo đơn hàng mới
                total_amount = sum(item["quantity"] * item["price"]
                                   for item in self.current_order_items)
                cursor.execute("""
                    INSERT INTO orders (user_id, table_id, total_amount, status, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.user_id, table_id, total_amount, "pending", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

                order_id = cursor.lastrowid

                # Thêm chi tiết đơn hàng
                for item in self.current_order_items:
                    cursor.execute("""
                        INSERT INTO order_items (order_id, menu_item_id, quantity, price)
                        VALUES (?, ?, ?, ?)
                    """, (order_id, item["product_id"], item["quantity"], item["price"]))

                # Cập nhật trạng thái bàn
                cursor.execute("""
                    UPDATE tables
                    SET status = 'occupied'
                    WHERE id = ?
                """, (table_id,))

                conn.commit()
                self.current_order_items = []
                self.update_current_order_table()
                self.load_orders()
                self.load_tables()  # Reload danh sách bàn trống

                QMessageBox.information(
                    self, "Thành công", "Đã hoàn tất đơn hàng!")
            except Exception as e:
                print(e)
                QMessageBox.warning(self, "Lỗi", "Không thể tạo đơn hàng!")
            finally:
                conn.close()

    def update_order_status(self, order_id, new_status):
        conn = create_connection()
        if conn is not None:
            try:
                cursor = conn.cursor()

                # Lấy table_id của đơn hàng
                cursor.execute(
                    "SELECT table_id FROM orders WHERE id = ?", (order_id,))
                table_id = cursor.fetchone()[0]

                # Cập nhật trạng thái đơn hàng
                cursor.execute("""
                    UPDATE orders
                    SET status = ?
                    WHERE id = ?
                """, (new_status, order_id))

                # Nếu đơn hàng hoàn thành hoặc hủy, cập nhật trạng thái bàn thành trống
                if new_status in ['completed', 'cancelled']:
                    cursor.execute("""
                        UPDATE tables
                        SET status = 'available'
                        WHERE id = ?
                    """, (table_id,))

                conn.commit()
                self.load_orders()  # Reload danh sách đơn hàng
                QMessageBox.information(
                    self, "Thành công", "Đã cập nhật trạng thái đơn hàng!")
            except Exception as e:
                print(e)
                QMessageBox.warning(
                    self, "Lỗi", "Không thể cập nhật trạng thái đơn hàng!")
            finally:
                conn.close()

    def load_orders(self):
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()

            # Nếu là nhân viên, hiển thị tất cả đơn hàng
            # Nếu là khách hàng, chỉ hiển thị đơn hàng của họ
            if self.is_staff:
                cursor.execute("""
                    SELECT o.id, t.number, o.created_at, o.total_amount, o.status,
                           u.username as customer_name
                    FROM orders o
                    LEFT JOIN tables t ON o.table_id = t.id
                    LEFT JOIN users u ON o.user_id = u.id
                    ORDER BY
                        CASE o.status
                            WHEN 'pending' THEN 1
                            WHEN 'preparing' THEN 2
                            WHEN 'served' THEN 3
                            WHEN 'completed' THEN 4
                            WHEN 'cancelled' THEN 5
                        END,
                        o.created_at DESC
                """)
            else:
                cursor.execute("""
                    SELECT o.id, t.number, o.created_at, o.total_amount, o.status,
                           u.username as customer_name
                    FROM orders o
                    LEFT JOIN tables t ON o.table_id = t.id
                    LEFT JOIN users u ON o.user_id = u.id
                    WHERE o.user_id = ?
                    ORDER BY o.created_at DESC
                """, (self.user_id,))

            orders = cursor.fetchall()

            self.order_history_table.setRowCount(len(orders))
            for i, order in enumerate(orders):
                # ID
                self.order_history_table.setItem(
                    i, 0, QTableWidgetItem(str(order[0])))
                # Bàn và tên khách hàng (chỉ cho nhân viên)
                table_text = f"Bàn {order[1]}"
                if self.is_staff:
                    table_text += f" - {order[5]}"  # Thêm tên khách hàng
                self.order_history_table.setItem(
                    i, 1, QTableWidgetItem(table_text))
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
                status_item = QTableWidgetItem(
                    status_map.get(order[4], order[4]))

                # Đánh dấu màu cho trạng thái
                if order[4] == "pending":
                    status_item.setBackground(
                        QBrush(QColor("#FFF3CD")))  # Màu vàng nhạt
                elif order[4] == "preparing":
                    status_item.setBackground(
                        QBrush(QColor("#CCE5FF")))  # Màu xanh nhạt
                elif order[4] == "served":
                    status_item.setBackground(
                        QBrush(QColor("#D4EDDA")))  # Màu xanh lá nhạt
                elif order[4] == "completed":
                    status_item.setBackground(
                        QBrush(QColor("#E2E3E5")))  # Màu xám nhạt
                elif order[4] == "cancelled":
                    status_item.setBackground(
                        QBrush(QColor("#F8D7DA")))  # Màu đỏ nhạt

                self.order_history_table.setItem(i, 4, status_item)

                if self.is_staff:
                    # Thêm nút cập nhật trạng thái
                    action_widget = QWidget()
                    action_layout = QHBoxLayout(action_widget)
                    action_layout.setContentsMargins(0, 0, 0, 0)

                    status_combo = QComboBox()
                    status_combo.addItems(
                        ["Chờ xử lý", "Đang chuẩn bị", "Đã phục vụ", "Hoàn thành", "Đã hủy"])
                    current_status = status_map.get(order[4], order[4])
                    status_combo.setCurrentText(current_status)

                    # Tạo mapping ngược để chuyển từ tiếng Việt sang giá trị trong database
                    reverse_status_map = {v: k for k, v in status_map.items()}

                    # Kết nối signal với lambda function để cập nhật trạng thái
                    status_combo.currentTextChanged.connect(
                        lambda text, order_id=order[0]: self.update_order_status(
                            order_id, reverse_status_map[text]))

                    action_layout.addWidget(status_combo)
                    self.order_history_table.setCellWidget(i, 5, action_widget)

            conn.close()

    def check_new_orders(self):
        """Kiểm tra đơn hàng mới và hiển thị thông báo"""
        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.id, t.number, o.created_at
                FROM orders o
                LEFT JOIN tables t ON o.table_id = t.id
                WHERE o.id > ? AND o.status = 'pending'
                ORDER BY o.id DESC
                LIMIT 1
            """, (self.last_order_id,))

            new_order = cursor.fetchone()
            if new_order:
                order_id, table_number, created_at = new_order
                self.last_order_id = order_id

                # Hiển thị thông báo
                message = f"Đơn hàng mới từ Bàn {table_number}\nThời gian: {created_at}"
                self.tray_icon.showMessage(
                    "Đơn hàng mới", message, QSystemTrayIcon.MessageIcon.Information)

                # Cập nhật bảng đơn hàng
                self.load_orders()

            conn.close()
