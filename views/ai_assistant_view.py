from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QTextEdit,
                             QVBoxLayout, QWidget)

from utils.ai_assistant import AIAssistant


class AIAssistantView(QWidget):
    def __init__(self):
        super().__init__()
        self.ai = AIAssistant()
        self.init_ui()

    def init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout()

        # Chat area
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        layout.addWidget(QLabel("Lịch sử chat:"))
        layout.addWidget(self.chat_history)

        # Input area
        input_layout = QHBoxLayout()
        self.chat_input = QTextEdit()
        self.chat_input.setMaximumHeight(50)
        send_button = QPushButton("Gửi")
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(send_button)
        layout.addLayout(input_layout)

        # Recommendation area
        layout.addWidget(QLabel("Gợi ý đồ uống:"))
        pref_layout = QHBoxLayout()
        self.pref_input = QTextEdit()
        self.pref_input.setMaximumHeight(50)
        self.pref_input.setPlaceholderText(
            "Nhập sở thích của bạn (vd: đồ uống ngọt, có sữa)")
        recommend_button = QPushButton("Gợi ý")
        recommend_button.clicked.connect(self.get_recommendations)
        pref_layout.addWidget(self.pref_input)
        pref_layout.addWidget(recommend_button)
        layout.addLayout(pref_layout)

        self.setLayout(layout)

    def send_message(self):
        """Xử lý gửi tin nhắn"""
        message = self.chat_input.toPlainText().strip()
        if message:
            self.chat_history.append(f"Bạn: {message}")
            response = self.ai.chat_with_customer(message)
            self.chat_history.append(f"AI: {response}\n")
            self.chat_input.clear()

    def get_recommendations(self):
        """Lấy gợi ý đồ uống"""
        preferences = self.pref_input.toPlainText().strip()
        if preferences:
            recommendations = self.ai.recommend_drinks(preferences)
            self.chat_history.append(
                f"\nGợi ý dựa trên sở thích '{preferences}':\n{recommendations}\n")
            self.pref_input.clear()
