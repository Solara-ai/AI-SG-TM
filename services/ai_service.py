from openai import OpenAI
import os
from dotenv import load_dotenv
from utils.schedule_utils import format_schedule
from datetime import datetime

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_ai_suggestions(schedule_data, user_info):
    try:
        prompt = f"""Hãy phân tích lịch trình và đưa ra gợi ý:

        Lịch trình ngày {datetime.now().strftime('%d/%m/%Y')}:
        {format_schedule(schedule_data)}

        Thông tin người dùng:
        - Nghề nghiệp: {user_info['occupation']}
        - Giới tính: {user_info['gender']}
        - Sở thích: {user_info['hobbies']}

        Yêu cầu:
        1. Phân tích các khoảng thời gian trống giữa các công việc đến 24 giờ
        2. Gợi ý hoạt động phù hợp (ưu tiên {user_info['hobbies']}) , mặc dù là ưu tiên sở thích nhng cũng cần chú trọng đến sức khỏe nữa
        3. Định dạng rõ ràng với thời gian cụ thể và nghiêm cấm cho các ký tự đặc biệt vào câu gợi ý  và gợi ý cũng phải phù hợp với thời gian nữa nhé ví dụ : thời gian trống có 30 phút mà lại gợi ý đi vẽ tranh là không được đâu nhé .
        4. Giữ giọng điệu như một đoạn gợi ý chính hiệu cho người dùng ấy nên cho icon bày tỏ cảm xúc
        5. Các đoạn mà gợi ý thì bạn hãy nói như là đưa ra lời khuyên cho người dùng vậy : ví dụ như là bạn nên giải lao một chút với game...
        6. lưu ý tối ưu đầu ra đoạn chat là chỉ cần đưa ra lịch gợi ý thôi nhất định không được thêm các đoạn chat khác vào và bỏ cái đoạn cuối đi như là chúc bạn một ngày vui vẻ
        7. Bắt buộc chỉ đưa ra lịch gợi ý thôi không cần đầu câu và cuối câu và cái đoạn gợi ý cuối ngày thì nên nói là bạn đã làm việc cả một ngày mệt mỏi rồi hãy tận hưởng thời gian nghỉ ngơi đi nhé . đó thân thiện với người dùng là như vậy 
        8. Chỉ đưa ra câu gợi ý thôi tuyệt đối không được viết lại lịch của người dùng """

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "Bạn là trợ lý lập lịch trình chuyên nghiệp. Hãy trả lời bằng Tiếng Việt."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Lỗi khi gọi AI: {str(e)}"
