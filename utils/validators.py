import re


def validate_email(email: str) -> bool:
    """
    Kiểm tra định dạng email hợp lệ.

    Args:
        email (str): Email cần kiểm tra

    Returns:
        bool: True nếu email hợp lệ, False nếu không hợp lệ
    """
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Kiểm tra định dạng số điện thoại hợp lệ.
    Số điện thoại phải có 10 chữ số và bắt đầu bằng số 0.

    Args:
        phone (str): Số điện thoại cần kiểm tra

    Returns:
        bool: True nếu số điện thoại hợp lệ, False nếu không hợp lệ
    """
    phone_pattern = r'^0\d{9}$'
    return bool(re.match(phone_pattern, phone))
