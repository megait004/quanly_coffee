from datetime import datetime, timedelta

from PyQt6.QtWidgets import (QCalendarWidget, QComboBox, QHBoxLayout,
                             QHeaderView, QLabel, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from database import create_connection


class ReportManager(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Bộ lọc thời gian
        filter_layout = QHBoxLayout()

        self.period_combo = QComboBox()
        self.period_combo.addItems(
            ["Hôm nay", "7 ngày qua", "30 ngày qua", "Tùy chọn"])
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        filter_layout.addWidget(QLabel("Thời gian:"))
        filter_layout.addWidget(self.period_combo)

        # Calendar cho tùy chọn thời gian
        self.start_calendar = QCalendarWidget()
        self.start_calendar.setVisible(False)
        self.start_calendar.clicked.connect(self.on_date_selected)

        self.end_calendar = QCalendarWidget()
        self.end_calendar.setVisible(False)
        self.end_calendar.clicked.connect(self.on_date_selected)

        calendar_layout = QHBoxLayout()
        calendar_layout.addWidget(self.start_calendar)
        calendar_layout.addWidget(self.end_calendar)

        layout.addLayout(filter_layout)
        layout.addLayout(calendar_layout)

        # Thống kê tổng quan
        summary_layout = QHBoxLayout()

        self.total_orders = QLabel("Tổng số đơn: 0")
        self.total_revenue = QLabel("Doanh thu: 0 VNĐ")
        self.avg_order_value = QLabel("Giá trị trung bình: 0 VNĐ")

        summary_layout.addWidget(self.total_orders)
        summary_layout.addWidget(self.total_revenue)
        summary_layout.addWidget(self.avg_order_value)

        layout.addLayout(summary_layout)

        # Bảng thống kê theo danh mục
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(4)
        self.category_table.setHorizontalHeaderLabels(
            ["Danh mục", "Số lượng đơn", "Doanh thu", "Tỷ lệ"])
        self.category_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        layout.addWidget(QLabel("Thống kê theo danh mục:"))
        layout.addWidget(self.category_table)

        # Bảng thống kê theo món
        self.item_table = QTableWidget()
        self.item_table.setColumnCount(4)
        self.item_table.setHorizontalHeaderLabels(
            ["Món", "Số lượng đã bán", "Doanh thu", "Tỷ lệ"])
        self.item_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        layout.addWidget(QLabel("Thống kê theo món:"))
        layout.addWidget(self.item_table)

        # Load thống kê mặc định (hôm nay)
        self.load_statistics()

    def on_period_changed(self, period):
        if period == "Tùy chọn":
            self.start_calendar.setVisible(True)
            self.end_calendar.setVisible(True)
        else:
            self.start_calendar.setVisible(False)
            self.end_calendar.setVisible(False)
            self.load_statistics()

    def on_date_selected(self):
        if self.period_combo.currentText() == "Tùy chọn":
            self.load_statistics()

    def get_date_range(self):
        period = self.period_combo.currentText()
        end_date = datetime.now()

        if period == "Hôm nay":
            start_date = end_date.replace(
                hour=0, minute=0, second=0, microsecond=0)
        elif period == "7 ngày qua":
            start_date = end_date - timedelta(days=7)
        elif period == "30 ngày qua":
            start_date = end_date - timedelta(days=30)
        else:  # Tùy chọn
            start_date = self.start_calendar.selectedDate().toPyDate()
            end_date = self.end_calendar.selectedDate().toPyDate()
            end_date = datetime.combine(end_date, datetime.max.time())
            start_date = datetime.combine(start_date, datetime.min.time())

        return start_date, end_date

    def load_statistics(self):
        start_date, end_date = self.get_date_range()

        conn = create_connection()
        if conn is not None:
            cursor = conn.cursor()

            # Thống kê tổng quan
            cursor.execute("""
                SELECT COUNT(*) as total_orders,
                       SUM(total_amount) as total_revenue
                FROM orders
                WHERE created_at BETWEEN ? AND ?
                AND status = 'completed'
            """, (start_date, end_date))

            result = cursor.fetchone()
            total_orders = result[0] or 0
            total_revenue = result[1] or 0
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

            self.total_orders.setText(f"Tổng số đơn: {total_orders}")
            self.total_revenue.setText(f"Doanh thu: {total_revenue:,.0f} VNĐ")
            self.avg_order_value.setText(
                f"Giá trị trung bình: {avg_order_value:,.0f} VNĐ")

            # Thống kê theo danh mục
            cursor.execute("""
                SELECT c.name,
                       COUNT(DISTINCT o.id) as order_count,
                       SUM(oi.quantity * oi.price) as revenue
                FROM categories c
                JOIN menu_items m ON m.category_id = c.id
                JOIN order_items oi ON oi.menu_item_id = m.id
                JOIN orders o ON oi.order_id = o.id
                WHERE o.created_at BETWEEN ? AND ?
                AND o.status = 'completed'
                GROUP BY c.id, c.name
                ORDER BY revenue DESC
            """, (start_date, end_date))

            categories = cursor.fetchall()
            self.category_table.setRowCount(len(categories))

            for i, category in enumerate(categories):
                name, order_count, revenue = category
                percentage = (revenue / total_revenue *
                              100) if total_revenue > 0 else 0

                self.category_table.setItem(i, 0, QTableWidgetItem(name))
                self.category_table.setItem(
                    i, 1, QTableWidgetItem(str(order_count)))
                self.category_table.setItem(
                    i, 2, QTableWidgetItem(f"{revenue:,.0f} VNĐ"))
                self.category_table.setItem(
                    i, 3, QTableWidgetItem(f"{percentage:.1f}%"))

            # Thống kê theo món
            cursor.execute("""
                SELECT m.name,
                       SUM(oi.quantity) as total_quantity,
                       SUM(oi.quantity * oi.price) as revenue
                FROM menu_items m
                JOIN order_items oi ON oi.menu_item_id = m.id
                JOIN orders o ON oi.order_id = o.id
                WHERE o.created_at BETWEEN ? AND ?
                AND o.status = 'completed'
                GROUP BY m.id, m.name
                ORDER BY revenue DESC
            """, (start_date, end_date))

            items = cursor.fetchall()
            self.item_table.setRowCount(len(items))

            for i, item in enumerate(items):
                name, quantity, revenue = item
                percentage = (revenue / total_revenue *
                              100) if total_revenue > 0 else 0

                self.item_table.setItem(i, 0, QTableWidgetItem(name))
                self.item_table.setItem(i, 1, QTableWidgetItem(str(quantity)))
                self.item_table.setItem(
                    i, 2, QTableWidgetItem(f"{revenue:,.0f} VNĐ"))
                self.item_table.setItem(
                    i, 3, QTableWidgetItem(f"{percentage:.1f}%"))

            conn.close()
