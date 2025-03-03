import os
import subprocess
import sys


def build():
    # Thêm thư mục hiện tại vào PYTHONPATH
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)

    # Xóa thư mục build và dist cũ
    os.system('rmdir /s /q build dist')

    # Build ứng dụng
    subprocess.call(['pyinstaller', 'quanly_coffee.spec'])


if __name__ == '__main__':
    build()
