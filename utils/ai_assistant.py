import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline


class AIAssistant:
    def __init__(self):
        # Khởi tạo các mô hình
        print("Đang tải mô hình AI...")

        # Mô hình cho chat
        self.chat_model = pipeline(
            "text2text-generation",
            model="VietAI/vit5-base",
            device=-1  # Sử dụng CPU
        )

        # Dữ liệu menu
        self.menu_context = self.load_menu_context()

        # Vectorizer cho tìm kiếm tương đồng
        self.vectorizer = TfidfVectorizer()
        self.menu_vectors = None
        self.prepare_menu_vectors()

        # Các câu trả lời mẫu cho trường hợp phổ biến
        self.common_responses = {
            'greeting': [
                "Xin chào quý khách! Tôi có thể giúp gì cho bạn?",
                "Chào mừng quý khách đến với quán cà phê của chúng tôi!",
                "Xin chào! Rất vui được phục vụ quý khách."
            ],
            'goodbye': [
                "Cảm ơn quý khách! Hẹn gặp lại!",
                "Chúc quý khách một ngày tốt lành!",
                "Tạm biệt quý khách! Rất vui được phục vụ!"
            ],
            'thanks': [
                "Không có gì ạ! Rất vui được phục vụ quý khách!",
                "Cảm ơn quý khách đã ủng hộ!",
                "Rất hân hạnh được phục vụ quý khách!"
            ]
        }

    def load_menu_context(self):
        """Load thông tin menu"""
        menu_items = {
            "Cà phê": [
                {"name": "Cà phê đen", "description": "Cà phê đen truyền thống"},
                {"name": "Cà phê sữa", "description": "Cà phê pha với sữa đặc"},
                {"name": "Cappuccino", "description": "Cà phê Ý với sữa tươi đánh bông"},
                {"name": "Latte", "description": "Cà phê với sữa tươi và ít bọt sữa"},
                {"name": "Espresso", "description": "Cà phê đậm đặc kiểu Ý"},
                {"name": "Mocha", "description": "Cà phê pha với sữa và socola"},
                {"name": "Americano", "description": "Espresso pha với nước nóng"},
                {"name": "Cold Brew", "description": "Cà phê ủ lạnh 24 giờ"}
            ],
            "Trà": [
                {"name": "Trà xanh", "description": "Trà xanh truyền thống"},
                {"name": "Trà đen", "description": "Trà đen đậm đà"},
                {"name": "Trà sữa", "description": "Trà pha với sữa tươi"},
                {"name": "Trà đào", "description": "Trà đen với đào tươi và syrup đào"},
                {"name": "Trà vải", "description": "Trà pha với vải và syrup vải"},
                {"name": "Trà chanh", "description": "Trà tươi với chanh và mật ong"},
                {"name": "Trà gừng", "description": "Trà nóng với gừng tươi"},
                {"name": "Trà hoa cúc", "description": "Trà hoa cúc thư giãn"}
            ],
            "Nước ép & Sinh tố": [
                {"name": "Nước cam", "description": "Nước cam tươi"},
                {"name": "Nước táo", "description": "Nước ép táo"},
                {"name": "Sinh tố xoài", "description": "Sinh tố xoài với sữa tươi"},
                {"name": "Sinh tố dâu", "description": "Sinh tố dâu tây với sữa chua"},
                {"name": "Nước ép dứa", "description": "Nước ép dứa tươi"},
                {"name": "Nước ép cà rốt", "description": "Nước ép cà rốt tươi"},
                {"name": "Sinh tố bơ", "description": "Sinh tố bơ béo ngậy"},
                {"name": "Sinh tố việt quất",
                    "description": "Sinh tố việt quất với sữa chua"}
            ],
            "Đồ ăn nhẹ": [
                {"name": "Bánh mì", "description": "Bánh mì truyền thống"},
                {"name": "Bánh ngọt", "description": "Bánh ngọt đặc biệt"},
                {"name": "Sandwich", "description": "Sandwich với nhiều loại nhân"},
                {"name": "Croissant", "description": "Bánh sừng bò truyền thống Pháp"},
                {"name": "Muffin", "description": "Bánh muffin nhiều hương vị"},
                {"name": "Cookies", "description": "Bánh quy giòn tan"},
                {"name": "Tiramisu", "description": "Bánh tiramisu Ý"},
                {"name": "Cheesecake", "description": "Bánh phô mai New York"}
            ],
            "Đồ uống đặc biệt": [
                {"name": "Sữa chua đá", "description": "Sữa chua với đá bào"},
                {"name": "Matcha đá xay", "description": "Matcha Nhật Bản xay với đá"},
                {"name": "Socola nóng", "description": "Socola nóng với kem tươi"},
                {"name": "Smoothie trái cây",
                    "description": "Smoothie hỗn hợp trái cây"},
                {"name": "Trà sữa trân châu",
                    "description": "Trà sữa với trân châu đường đen"},
                {"name": "Yakult đào", "description": "Yakult với syrup đào"},
                {"name": "Nước chanh sả", "description": "Nước chanh với sả tươi"},
                {"name": "Soda Italian", "description": "Soda với syrup hoa quả"}
            ]
        }
        return menu_items

    def prepare_menu_vectors(self):
        """Chuẩn bị vectors cho menu items"""
        menu_texts = []
        for category, items in self.menu_context.items():
            for item in items:
                menu_texts.append(f"{item['name']} - {item['description']}")
        self.menu_vectors = self.vectorizer.fit_transform(menu_texts)
        self.menu_items_flat = menu_texts

    def clean_text(self, text):
        """Làm sạch văn bản"""
        # Loại bỏ các ký tự đặc biệt không cần thiết
        text = re.sub(r'[^\w\s,.!?:;()-]', '', text)
        # Chuẩn hóa khoảng trắng
        text = ' '.join(text.split())
        return text

    def is_greeting(self, text):
        """Kiểm tra xem có phải là câu chào không"""
        greetings = ['chào', 'xin chào', 'hello', 'hi', 'hey']
        text = text.lower()
        return any(greeting in text for greeting in greetings)

    def is_goodbye(self, text):
        """Kiểm tra xem có phải là câu tạm biệt không"""
        goodbyes = ['tạm biệt', 'goodbye', 'bye', 'hẹn gặp lại']
        text = text.lower()
        return any(goodbye in text for goodbye in goodbyes)

    def is_thanks(self, text):
        """Kiểm tra xem có phải là câu cảm ơn không"""
        thanks = ['cảm ơn', 'thank', 'thanks', 'cám ơn']
        text = text.lower()
        return any(thank in text for thank in thanks)

    def get_simple_response(self, text):
        """Lấy câu trả lời đơn giản cho các trường hợp phổ biến"""
        import random
        if self.is_greeting(text):
            return random.choice(self.common_responses['greeting'])
        elif self.is_goodbye(text):
            return random.choice(self.common_responses['goodbye'])
        elif self.is_thanks(text):
            return random.choice(self.common_responses['thanks'])
        return None

    def chat_with_customer(self, user_message):
        """Xử lý chat với khách hàng"""
        try:
            # Làm sạch tin nhắn của người dùng
            clean_message = self.clean_text(user_message)

            # Kiểm tra các trường hợp đơn giản trước
            simple_response = self.get_simple_response(clean_message)
            if simple_response:
                return simple_response

            # Kiểm tra nếu khách hàng hỏi về menu
            if "menu" in clean_message.lower():
                return self._format_menu()

            # Xử lý các câu hỏi phức tạp hơn
            prompt = f"Hãy trả lời ngắn gọn và lịch sự: {clean_message}"

            # Tạo câu trả lời
            response = self.chat_model(
                prompt,
                max_length=100,  # Giảm độ dài tối đa
                num_beams=2,     # Giảm số beam để tập trung vào câu trả lời chính
                length_penalty=1.0,
                do_sample=True,
                temperature=0.5,  # Giảm temperature để có câu trả lời ổn định hơn
                no_repeat_ngram_size=2
            )[0]['generated_text']

            # Làm sạch và định dạng phản hồi
            response = self.clean_text(response)

            # Nếu response trống hoặc không hợp lệ
            if not response or len(response.strip()) < 5:
                return "Xin lỗi, tôi không hiểu câu hỏi. Bạn có thể nói rõ hơn được không?"

            return response

        except Exception as e:
            return f"Xin lỗi, tôi đang gặp vấn đề kỹ thuật: {str(e)}"

    def recommend_drinks(self, preferences):
        """Gợi ý đồ uống dựa trên sở thích"""
        try:
            # Vector hóa preferences
            pref_vector = self.vectorizer.transform([preferences])

            # Tính similarity
            similarities = cosine_similarity(pref_vector, self.menu_vectors)

            # Lấy top 3 đồ uống phù hợp nhất
            top_indices = similarities[0].argsort()[-3:][::-1]

            recommendations = []
            for idx in top_indices:
                recommendations.append(self.menu_items_flat[idx])

            return "Dựa trên sở thích của bạn, tôi gợi ý:\n" + "\n".join(
                f"- {rec}" for rec in recommendations
            )
        except Exception as e:
            return f"Xin lỗi, không thể tạo gợi ý: {str(e)}"

    def _format_menu(self):
        """Format menu để hiển thị"""
        menu_text = "🍵 MENU CỦA CHÚNG TÔI 🍵\n\n"
        for category, items in self.menu_context.items():
            menu_text += f"=== {category} ===\n"
            for item in items:
                menu_text += f"• {item['name']}: {item['description']}\n"
            menu_text += "\n"
        return menu_text
