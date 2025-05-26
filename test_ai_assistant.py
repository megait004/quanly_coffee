import pandas as pd

from utils.ai_assistant import AIAssistant


def test_ai_features():
    print("Khởi tạo AI Assistant...")
    ai = AIAssistant()

    # Test chức năng chat
    print("\nKiểm tra chức năng chat:")
    chat_response = ai.chat_with_customer("Cho tôi xem menu")
    print(f"Phản hồi chat: {chat_response}")

    # Test gợi ý đồ uống
    print("\nKiểm tra chức năng gợi ý đồ uống:")
    recommendations = ai.recommend_drinks("Tôi thích đồ uống ngọt và có sữa")
    print(f"Gợi ý: {recommendations}")

    # Test phân tích phản hồi
    print("\nKiểm tra phân tích phản hồi:")
    sample_feedback = pd.DataFrame({
        'feedback': [
            "Cà phê rất ngon và nhân viên phục vụ tốt!",
            "Phải đợi quá lâu để có đồ uống",
            "Không gian đẹp nhưng giá hơi cao"
        ]
    })
    feedback_analysis = ai.analyze_feedback(sample_feedback)
    print("Kết quả phân tích phản hồi:")
    print(feedback_analysis)

    # Test dự đoán xu hướng
    print("\nKiểm tra dự đoán xu hướng:")
    sample_sales = pd.DataFrame({
        'date': pd.date_range(start='2024-01-01', periods=10, freq='D'),
        'sales': [100, 120, 115, 125, 130, 140, 135, 145, 150, 160]
    })
    trend_analysis = ai.predict_sales_trend(sample_sales)
    print("Kết quả phân tích xu hướng:")
    print(trend_analysis)


if __name__ == "__main__":
    test_ai_features()
