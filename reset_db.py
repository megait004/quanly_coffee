from config.database import reset_database

if __name__ == "__main__":
    try:
        print("Đang reset database...")
        reset_database()
        print("Đã reset database thành công!")
        print("\nTài khoản admin mặc định:")
        print("Username: admin")
        print("Password: admin123")
        print("\nĐã tạo sẵn:")
        print("- 4 danh mục đồ uống")
        print("- 10 bàn với sức chứa 4 người/bàn")
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        input("\nNhấn Enter để thoát...")
