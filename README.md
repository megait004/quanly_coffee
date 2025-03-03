# Quản lý Quán Cà Phê

Ứng dụng quản lý quán cà phê được xây dựng bằng Python và PyQt6.

## Cài đặt

### Cách 1: Cài đặt từ source code

1. Clone repository:
```bash
git clone https://github.com/yourusername/quanly_coffee.git
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