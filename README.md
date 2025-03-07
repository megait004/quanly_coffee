# Quản lý Quán Cà Phê

Ứng dụng quản lý quán cà phê được xây dựng bằng Python và PyQt6.

## Cài đặt

### Cách 1: Cài đặt từ source code

1. Clone repository:
```bash
git clone https://github.com/megait004/quanly_coffee.git
cd quanly_coffee
```

2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

3. Chạy ứng dụng:
```bash
python main.py
```

### Cách 2: Cài đặt từ file exe

1. Tải file exe từ trang Releases
2. Giải nén file zip
3. Chạy file QuanLyCoffee.exe

## Build từ source code

Để build ứng dụng thành file exe:

1. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

2. Build ứng dụng:
```bash
pyinstaller quanly_coffee.spec
```

File exe sẽ được tạo trong thư mục `dist/QuanLyCoffee`.

## Cấu trúc thư mục

```
quanly_coffee/
│
├── config/               # Cấu hình và kết nối database
├── models/              # Các model xử lý dữ liệu
├── views/               # Giao diện người dùng
│   ├── windows/        # Các cửa sổ chính
│   ├── dialogs/        # Các dialog
│   └── managers/       # Các module quản lý
├── controllers/         # Xử lý logic
├── utils/              # Tiện ích
└── static/             # Tài nguyên tĩnh khác
```

## Cấu trúc Database

### Bảng Users (Người dùng)
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `username`: TEXT UNIQUE NOT NULL - Tên đăng nhập
- `password`: TEXT NOT NULL - Mật khẩu (đã mã hóa)
- `role`: TEXT NOT NULL - Vai trò (admin/staff/customer)
- `email`: TEXT UNIQUE - Email
- `phone`: TEXT - Số điện thoại
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP - Thời gian tạo

### Bảng Categories (Danh mục)
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `name`: TEXT NOT NULL - Tên danh mục
- `description`: TEXT - Mô tả danh mục

### Bảng Tables (Bàn)
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `number`: INTEGER UNIQUE NOT NULL - Số bàn
- `capacity`: INTEGER NOT NULL - Sức chứa
- `status`: TEXT NOT NULL - Trạng thái (available/occupied/reserved)

### Bảng Menu Items (Món)
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `category_id`: INTEGER - ID danh mục (FK)
- `name`: TEXT NOT NULL - Tên món
- `description`: TEXT - Mô tả món
- `price`: REAL NOT NULL - Giá
- `status`: TEXT NOT NULL - Trạng thái (available/out_of_stock/discontinued)

### Bảng Orders (Đơn hàng)
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `user_id`: INTEGER - ID người dùng (FK)
- `table_id`: INTEGER - ID bàn (FK)
- `status`: TEXT NOT NULL - Trạng thái (pending/preparing/served/completed/cancelled)
- `total_amount`: REAL - Tổng tiền
- `created_at`: TIMESTAMP DEFAULT CURRENT_TIMESTAMP - Thời gian tạo

### Bảng Order Items (Chi tiết đơn hàng)
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `order_id`: INTEGER - ID đơn hàng (FK)
- `menu_item_id`: INTEGER - ID món (FK)
- `quantity`: INTEGER NOT NULL - Số lượng
- `price`: REAL NOT NULL - Giá tại thời điểm đặt

### Bảng Employees (Nhân viên)
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `user_id`: INTEGER UNIQUE - ID người dùng (FK)
- `name`: TEXT NOT NULL - Tên nhân viên
- `position`: TEXT NOT NULL - Chức vụ
- `salary`: REAL - Lương
- `shift_start`: TIME - Giờ bắt đầu ca
- `shift_end`: TIME - Giờ kết thúc ca

### Bảng Customers (Khách hàng)
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `user_id`: INTEGER UNIQUE - ID người dùng (FK)
- `name`: TEXT NOT NULL - Tên khách hàng
- `loyalty_points`: INTEGER DEFAULT 0 - Điểm tích lũy
- `member_since`: DATE DEFAULT CURRENT_DATE - Ngày đăng ký

### Bảng Inventory (Kho)
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `name`: TEXT NOT NULL UNIQUE - Tên nguyên liệu
- `quantity`: INTEGER DEFAULT 0 - Số lượng
- `unit`: TEXT NOT NULL - Đơn vị tính
- `threshold`: INTEGER DEFAULT 0 - Ngưỡng cảnh báo

### Bảng Inventory History (Lịch sử kho)
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT
- `inventory_id`: INTEGER NOT NULL - ID nguyên liệu (FK)
- `type`: TEXT NOT NULL - Loại (import/export)
- `quantity`: INTEGER NOT NULL - Số lượng
- `price`: REAL - Giá
- `supplier`: TEXT - Nhà cung cấp
- `note`: TEXT - Ghi chú
- `timestamp`: DATETIME DEFAULT CURRENT_TIMESTAMP - Thời gian

### Quan hệ giữa các bảng:
1. Menu Items -> Categories (n-1)
2. Orders -> Users (n-1)
3. Orders -> Tables (n-1)
4. Order Items -> Orders (n-1)
5. Order Items -> Menu Items (n-1)
6. Employees -> Users (1-1)
7. Customers -> Users (1-1)
8. Inventory History -> Inventory (n-1)

### Dữ liệu mặc định:
1. Tài khoản Admin:
   - Username: admin
   - Password: admin123
2. Danh mục đồ uống:
   - Cà phê
   - Trà
   - Nước ép
   - Sinh tố
3. Bàn:
   - 10 bàn với sức chứa 4 người/bàn

## Tài khoản mặc định

- Admin:
  - Username: admin
  - Password: admin123

## Chức năng chính

1. Quản lý người dùng:
   - Đăng nhập/Đăng ký
   - Phân quyền (Admin/Staff/Customer)

2. Quản lý menu:
   - Thêm/sửa/xóa món
   - Quản lý danh mục
   - Cập nhật trạng thái món

3. Quản lý bàn:
   - Thêm/xóa bàn
   - Cập nhật trạng thái bàn
   - Quản lý đặt bàn

4. Quản lý đơn hàng:
   - Tạo đơn hàng mới
   - Theo dõi trạng thái đơn hàng
   - Xem lịch sử đơn hàng

5. Quản lý kho:
   - Thêm/xóa sản phẩm
   - Cập nhật số lượng
   - Cảnh báo hết hàng

6. Báo cáo thống kê:
   - Doanh thu theo thời gian
   - Thống kê theo danh mục/món
   - Phân tích xu hướng

## Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo issue hoặc pull request.