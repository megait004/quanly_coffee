from PyQt6.QtCore import QEasingCurve, QPropertyAnimation
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QWidget

# Color Palette
COLORS = {
    'primary': '#2ecc71',
    'primary_dark': '#27ae60',
    'secondary': '#3498db',
    'secondary_dark': '#2980b9',
    'accent': '#e74c3c',
    'accent_dark': '#c0392b',
    'background': '#f5f6fa',
    'surface': '#ffffff',
    'text': '#2c3e50',
    'text_light': '#7f8c8d',
    'border': '#bdc3c7'
}

# Common Styles
BUTTON_STYLE = """
QPushButton {{
    background-color: {color};
    color: white;
    border: none;
    border-radius: 5px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {dark_color};
}}
QPushButton:pressed {{
    background-color: {color};
    padding: 11px 19px;
}}
"""

INPUT_STYLE = """
QLineEdit {{
    background-color: {surface};
    border: 2px solid {border};
    border-radius: 5px;
    padding: 8px;
    font-size: 14px;
    color: {text};
}}
QLineEdit:focus {{
    border-color: {primary};
}}
QLineEdit:hover {{
    border-color: {primary_dark};
}}
"""

COMBOBOX_STYLE = """
QComboBox {{
    background-color: {surface};
    border: 2px solid {border};
    border-radius: 5px;
    padding: 8px;
    font-size: 14px;
    color: {text};
}}
QComboBox:hover {{
    border-color: {primary};
}}
QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
}}
QComboBox::down-arrow {{
    image: url(resources/icons/down-arrow.png);
    width: 12px;
    height: 12px;
}}
"""

TABLE_STYLE = """
QTableWidget {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 5px;
    gridline-color: {border};
}}
QTableWidget::item {{
    padding: 8px;
    color: {text};
}}
QTableWidget::item:selected {{
    background-color: {primary};
    color: white;
}}
QHeaderView::section {{
    background-color: {background};
    color: {text};
    padding: 8px;
    border: none;
    border-right: 1px solid {border};
    border-bottom: 1px solid {border};
    font-weight: bold;
}}
"""

TAB_STYLE = """
QTabWidget::pane {{
    border: 1px solid {border};
    border-radius: 5px;
    background: {surface};
}}
QTabBar::tab {{
    background: {background};
    color: {text};
    padding: 10px 15px;
    border: 1px solid {border};
    border-bottom: none;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background: {surface};
    border-bottom: none;
    padding-bottom: 11px;
}}
"""

CALENDAR_STYLE = """
QCalendarWidget {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 5px;
}}
QCalendarWidget QToolButton {{
    color: {text};
    background-color: transparent;
    border: none;
    border-radius: 5px;
    padding: 5px;
}}
QCalendarWidget QToolButton:hover {{
    background-color: {primary};
    color: white;
}}
QCalendarWidget QMenu {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 5px;
}}
"""


def apply_shadow(widget: QWidget, radius=10, offset=1):
    """Thêm hiệu ứng đổ bóng cho widget"""
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(radius)
    shadow.setOffset(offset)
    shadow.setColor(QColor(0, 0, 0, 50))
    widget.setGraphicsEffect(shadow)


def fade_in(widget: QWidget, duration=300):
    """Hiệu ứng fade in cho widget"""
    widget.setWindowOpacity(0)
    animation = QPropertyAnimation(widget, b"windowOpacity")
    animation.setDuration(duration)
    animation.setStartValue(0)
    animation.setEndValue(1)
    animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    animation.start()


def slide_in(widget: QWidget, direction="right", duration=300):
    """Hiệu ứng slide in cho widget"""
    pos = widget.pos()
    if direction == "right":
        start_pos = pos.x() - 100
        widget.move(start_pos, pos.y())
    elif direction == "left":
        start_pos = pos.x() + 100
        widget.move(start_pos, pos.y())
    elif direction == "up":
        start_pos = pos.y() + 100
        widget.move(pos.x(), start_pos)
    else:  # down
        start_pos = pos.y() - 100
        widget.move(pos.x(), start_pos)

    anim = QPropertyAnimation(widget, b"pos")
    anim.setDuration(duration)
    anim.setEndValue(pos)
    anim.setEasingCurve(QEasingCurve.Type.OutQuad)
    anim.start()


def setup_theme(app):
    """Thiết lập theme chung cho toàn bộ ứng dụng"""
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(COLORS['background']))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(COLORS['text']))
    palette.setColor(QPalette.ColorRole.Base, QColor(COLORS['surface']))
    palette.setColor(QPalette.ColorRole.AlternateBase,
                     QColor(COLORS['background']))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(COLORS['surface']))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(COLORS['text']))
    palette.setColor(QPalette.ColorRole.Text, QColor(COLORS['text']))
    palette.setColor(QPalette.ColorRole.Button, QColor(COLORS['primary']))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor('white'))
    palette.setColor(QPalette.ColorRole.Link, QColor(COLORS['secondary']))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(COLORS['primary']))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor('white'))

    app.setPalette(palette)
    app.setStyle('Fusion')  # Sử dụng Fusion style cho giao diện hiện đại


def get_style(style_name: str, **kwargs) -> str:
    """Lấy style với các tham số tùy chỉnh"""
    style_dict = {
        'button': BUTTON_STYLE,
        'input': INPUT_STYLE,
        'combobox': COMBOBOX_STYLE,
        'table': TABLE_STYLE,
        'tab': TAB_STYLE,
        'calendar': CALENDAR_STYLE
    }

    # Merge COLORS với kwargs để cho phép ghi đè màu sắc
    params = COLORS.copy()
    params.update(kwargs)

    return style_dict.get(style_name, "").format(**params)
