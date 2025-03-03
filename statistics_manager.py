from datetime import datetime, timedelta

from PyQt6.QtWidgets import (QCalendarWidget, QComboBox, QHBoxLayout,
                             QHeaderView, QLabel, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from config.database import create_connection


class StatisticsManager(QWidget):
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

        # Bảng thống kê chi tiết theo sản phẩm
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(4)
        self.product_table.setHorizontalHeaderLabels(
            ["Sản phẩm", "Số lượng đã bán", "Doanh thu", "Tỷ lệ"])
        self.product_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.product_table)

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
                WHERE order_date BETWEEN ? AND ?
            """, (start_date, end_date))

            result = cursor.fetchone()
            total_orders = result[0] or 0
            total_revenue = result[1] or 0
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

            self.total_orders.setText(f"Tổng số đơn: {total_orders}")
            self.total_revenue.setText(f"Doanh thu: {total_revenue:,.0f} VNĐ")
            self.avg_order_value.setText(
                f"Giá trị trung bình: {avg_order_value:,.0f} VNĐ")

            # Thống kê theo sản phẩm
            cursor.execute("""
                SELECT p.name,
                       SUM(od.quantity) as total_quantity,
                       SUM(od.quantity * od.price) as revenue
                FROM order_details od
                JOIN products p ON od.product_id = p.id
                JOIN orders o ON od.order_id = o.id
                WHERE o.order_date BETWEEN ? AND ?
                GROUP BY p.id, p.name
                ORDER BY revenue DESC
            """, (start_date, end_date))

            products = cursor.fetchall()
            self.product_table.setRowCount(len(products))

            for i, product in enumerate(products):
                name, quantity, revenue = product
                percentage = (revenue / total_revenue *
                              100) if total_revenue > 0 else 0

                self.product_table.setItem(i, 0, QTableWidgetItem(name))
                self.product_table.setItem(
                    i, 1, QTableWidgetItem(str(quantity)))
                self.product_table.setItem(
                    i, 2, QTableWidgetItem(f"{revenue:,.0f} VNĐ"))
                self.product_table.setItem(
                    i, 3, QTableWidgetItem(f"{percentage:.1f}%"))

            conn.close()
