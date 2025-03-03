from datetime import datetime, timedelta

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (QCalendarWidget, QComboBox, QHBoxLayout,
                             QHeaderView, QLabel, QLineEdit, QTableWidget,
                             QTableWidgetItem, QTabWidget, QVBoxLayout,
                             QWidget)

from config.database import create_connection


class ReportManager(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.category_data = []  # Lưu dữ liệu gốc của bảng danh mục
        self.item_data = []  # Lưu dữ liệu gốc của bảng món

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Tạo tab widget
        tab_widget = QTabWidget()

        # Tab Tổng quan
        overview_tab = QWidget()
        overview_layout = QVBoxLayout()
        overview_tab.setLayout(overview_layout)

        # Bộ lọc thời gian
        filter_layout = QHBoxLayout()
        self.period_combo = QComboBox()
        self.period_combo.addItems(
            ["Hôm nay", "7 ngày qua", "30 ngày qua", "Tùy chọn"])
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        filter_layout.addWidget(QLabel("Thời gian:"))
        filter_layout.addWidget(self.period_combo)
        overview_layout.addLayout(filter_layout)

        # Calendar cho tùy chọn thời gian
        calendar_layout = QHBoxLayout()
        self.start_calendar = QCalendarWidget()
        self.start_calendar.setVisible(False)
        self.start_calendar.clicked.connect(self.on_date_selected)
        calendar_layout.addWidget(self.start_calendar)

        self.end_calendar = QCalendarWidget()
        self.end_calendar.setVisible(False)
        self.end_calendar.clicked.connect(self.on_date_selected)
        calendar_layout.addWidget(self.end_calendar)
        overview_layout.addLayout(calendar_layout)

        # Thống kê tổng quan
        summary_layout = QHBoxLayout()
        self.total_orders = QLabel("Tổng số đơn: 0")
        self.total_revenue = QLabel("Doanh thu: 0 VNĐ")
        self.avg_order_value = QLabel("Giá trị trung bình: 0 VNĐ")
        summary_layout.addWidget(self.total_orders)
        summary_layout.addWidget(self.total_revenue)
        summary_layout.addWidget(self.avg_order_value)
        overview_layout.addLayout(summary_layout)

        # Biểu đồ doanh thu theo thời gian
        self.revenue_figure = plt.figure(figsize=(10, 4))
        self.revenue_canvas = FigureCanvas(self.revenue_figure)
        overview_layout.addWidget(self.revenue_canvas)

        # Tab Thống kê theo danh mục
        category_tab = QWidget()
        category_layout = QVBoxLayout()
        category_tab.setLayout(category_layout)

        # Thêm ô tìm kiếm cho danh mục
        category_search_layout = QHBoxLayout()
        category_search_layout.addWidget(QLabel("Tìm kiếm danh mục:"))
        self.category_search = QLineEdit()
        self.category_search.setPlaceholderText("Nhập tên danh mục...")
        self.category_search.textChanged.connect(self.search_category)
        category_search_layout.addWidget(self.category_search)
        category_layout.addLayout(category_search_layout)

        # Bảng thống kê theo danh mục
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(4)
        self.category_table.setHorizontalHeaderLabels(
            ["Danh mục", "Số lượng đơn", "Doanh thu", "Tỷ lệ"])
        self.category_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        category_layout.addWidget(self.category_table)

        # Biểu đồ tròn theo danh mục
        self.category_figure = plt.figure(figsize=(8, 8))
        self.category_canvas = FigureCanvas(self.category_figure)
        category_layout.addWidget(self.category_canvas)

        # Tab Thống kê theo món
        item_tab = QWidget()
        item_layout = QVBoxLayout()
        item_tab.setLayout(item_layout)

        # Thêm ô tìm kiếm cho món
        item_search_layout = QHBoxLayout()
        item_search_layout.addWidget(QLabel("Tìm kiếm món:"))
        self.item_search = QLineEdit()
        self.item_search.setPlaceholderText("Nhập tên món...")
        self.item_search.textChanged.connect(self.search_item)
        item_search_layout.addWidget(self.item_search)
        item_layout.addLayout(item_search_layout)

        # Bảng thống kê theo món
        self.item_table = QTableWidget()
        self.item_table.setColumnCount(4)
        self.item_table.setHorizontalHeaderLabels(
            ["Món", "Số lượng đã bán", "Doanh thu", "Tỷ lệ"])
        self.item_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        item_layout.addWidget(self.item_table)

        # Biểu đồ top 10 món bán chạy
        self.item_figure = plt.figure(figsize=(10, 4))
        self.item_canvas = FigureCanvas(self.item_figure)
        item_layout.addWidget(self.item_canvas)

        # Thêm các tab
        tab_widget.addTab(overview_tab, "Tổng quan")
        tab_widget.addTab(category_tab, "Theo danh mục")
        tab_widget.addTab(item_tab, "Theo món")
        layout.addWidget(tab_widget)

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

    def search_category(self, text):
        """Tìm kiếm trong bảng danh mục"""
        text = text.lower()
        self.category_table.setRowCount(0)
        filtered_data = []

        for row in self.category_data:
            if text in row[0].lower():  # Tìm trong tên danh mục
                filtered_data.append(row)

        self.category_table.setRowCount(len(filtered_data))
        for i, row in enumerate(filtered_data):
            name, order_count, revenue, percentage = row
            self.category_table.setItem(i, 0, QTableWidgetItem(name))
            self.category_table.setItem(
                i, 1, QTableWidgetItem(str(order_count)))
            self.category_table.setItem(i, 2, QTableWidgetItem(revenue))
            self.category_table.setItem(i, 3, QTableWidgetItem(percentage))

        # Cập nhật biểu đồ tròn với dữ liệu đã lọc
        if filtered_data:
            self.update_category_chart(filtered_data)

    def search_item(self, text):
        """Tìm kiếm trong bảng món"""
        text = text.lower()
        self.item_table.setRowCount(0)
        filtered_data = []

        for row in self.item_data:
            if text in row[0].lower():  # Tìm trong tên món
                filtered_data.append(row)

        self.item_table.setRowCount(len(filtered_data))
        for i, row in enumerate(filtered_data):
            name, quantity, revenue, percentage = row
            self.item_table.setItem(i, 0, QTableWidgetItem(name))
            self.item_table.setItem(i, 1, QTableWidgetItem(str(quantity)))
            self.item_table.setItem(i, 2, QTableWidgetItem(revenue))
            self.item_table.setItem(i, 3, QTableWidgetItem(percentage))

        # Cập nhật biểu đồ cột với top 10 của dữ liệu đã lọc
        if filtered_data:
            self.update_item_chart(filtered_data[:10])

    def update_category_chart(self, data):
        """Cập nhật biểu đồ tròn danh mục"""
        self.category_figure.clear()
        ax = self.category_figure.add_subplot(111)

        names = [row[0] for row in data]
        revenues = [float(row[2].replace(',', '').replace(' VNĐ', ''))
                    for row in data]

        ax.pie(revenues, labels=names, autopct='%1.1f%%')
        ax.set_title("Tỷ lệ doanh thu theo danh mục")
        self.category_figure.tight_layout()
        self.category_canvas.draw()

    def update_item_chart(self, data):
        """Cập nhật biểu đồ cột món"""
        self.item_figure.clear()
        ax = self.item_figure.add_subplot(111)

        names = [row[0] for row in data]
        quantities = [int(row[1]) for row in data]

        ax.bar(names, quantities)
        ax.set_title("Top món bán chạy nhất")
        ax.set_xlabel("Tên món")
        ax.set_ylabel("Số lượng đã bán")
        plt.xticks(rotation=45, ha='right')
        self.item_figure.tight_layout()
        self.item_canvas.draw()

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

            # Biểu đồ doanh thu theo thời gian
            cursor.execute("""
                SELECT DATE(created_at) as date,
                       COUNT(*) as order_count,
                       SUM(total_amount) as daily_revenue
                FROM orders
                WHERE created_at BETWEEN ? AND ?
                AND status = 'completed'
                GROUP BY DATE(created_at)
                ORDER BY date
            """, (start_date, end_date))

            dates = []
            revenues = []
            for row in cursor.fetchall():
                dates.append(datetime.strptime(
                    row[0], "%Y-%m-%d").strftime("%d/%m"))
                revenues.append(row[2])

            self.revenue_figure.clear()
            ax = self.revenue_figure.add_subplot(111)
            ax.bar(dates, revenues)
            ax.set_title("Doanh thu theo ngày")
            ax.set_xlabel("Ngày")
            ax.set_ylabel("Doanh thu (VNĐ)")
            plt.xticks(rotation=45)
            self.revenue_figure.tight_layout()
            self.revenue_canvas.draw()

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

            # Lưu dữ liệu gốc của bảng danh mục
            self.category_data = []
            category_names = []
            category_revenues = []

            for i, category in enumerate(categories):
                name, order_count, revenue = category
                percentage = (revenue / total_revenue *
                              100) if total_revenue > 0 else 0

                row_data = (
                    name,
                    order_count,
                    f"{revenue:,.0f} VNĐ",
                    f"{percentage:.1f}%"
                )
                self.category_data.append(row_data)

                self.category_table.setItem(
                    i, 0, QTableWidgetItem(row_data[0]))
                self.category_table.setItem(
                    i, 1, QTableWidgetItem(str(row_data[1])))
                self.category_table.setItem(
                    i, 2, QTableWidgetItem(row_data[2]))
                self.category_table.setItem(
                    i, 3, QTableWidgetItem(row_data[3]))

                # Thêm dữ liệu cho biểu đồ tròn
                category_names.append(name)
                category_revenues.append(revenue if revenue else 0)

            # Vẽ biểu đồ tròn danh mục
            self.category_figure.clear()
            ax = self.category_figure.add_subplot(111)

            # Chỉ vẽ biểu đồ nếu có dữ liệu
            if category_revenues:
                ax.pie(category_revenues,
                       labels=category_names, autopct='%1.1f%%')
                ax.set_title("Tỷ lệ doanh thu theo danh mục")
            else:
                ax.text(0.5, 0.5, "Không có dữ liệu", ha='center', va='center')

            self.category_figure.tight_layout()
            self.category_canvas.draw()

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

            # Lưu dữ liệu gốc của bảng món
            self.item_data = []
            item_names = []
            item_quantities = []

            for i, item in enumerate(items):
                name, quantity, revenue = item
                percentage = (revenue / total_revenue *
                              100) if total_revenue > 0 else 0

                row_data = (
                    name,
                    quantity if quantity else 0,
                    f"{revenue:,.0f} VNĐ" if revenue else "0 VNĐ",
                    f"{percentage:.1f}%"
                )
                self.item_data.append(row_data)

                self.item_table.setItem(i, 0, QTableWidgetItem(row_data[0]))
                self.item_table.setItem(
                    i, 1, QTableWidgetItem(str(row_data[1])))
                self.item_table.setItem(i, 2, QTableWidgetItem(row_data[2]))
                self.item_table.setItem(i, 3, QTableWidgetItem(row_data[3]))

                # Thêm dữ liệu cho biểu đồ cột (chỉ lấy top 10)
                if i < 10:
                    item_names.append(name)
                    item_quantities.append(quantity if quantity else 0)

            # Vẽ biểu đồ top 10 món bán chạy
            self.item_figure.clear()
            ax = self.item_figure.add_subplot(111)

            # Chỉ vẽ biểu đồ nếu có dữ liệu
            if item_quantities:
                ax.bar(item_names, item_quantities)
                ax.set_title("Top 10 món bán chạy nhất")
                ax.set_xlabel("Tên món")
                ax.set_ylabel("Số lượng đã bán")
                plt.xticks(rotation=45, ha='right')
            else:
                ax.text(0.5, 0.5, "Không có dữ liệu", ha='center', va='center')

            self.item_figure.tight_layout()
            self.item_canvas.draw()

            conn.close()
