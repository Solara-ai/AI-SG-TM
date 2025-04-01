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

        Hãy phân tích lịch trình hiện tại của người dùng và tạo các gợi ý hoạt động cho khoảng thời gian trống theo hướng dẫn sau:

        1. Xác định chính xác các khoảng thời gian trống giữa các hoạt động trong ngày (từ 00:00 đến 23:59)

        2. Cho mỗi khoảng trống, đề xuất một hoạt động phù hợp với:
         - Thời lượng thực tế của khoảng trống (đề xuất phải khả thi trong khung giờ đó)
         - Ưu tiên sở thích của người dùng: {user_info['hobbies']}
         - Cân nhắc yếu tố sức khỏe và thời điểm trong ngày
 
        3. Định dạng mỗi gợi ý:
         - [Giờ bắt đầu] - [Giờ kết thúc]: [Gợi ý hoạt động]
         - lưu ý là lịch trống có thời gian quá nhiều ví dụ là 5 tiếng thì hãy chia nhỏ ra để có thêm nhiều gợi ý 
         - chú ý một điều quan trọng nữa là nên tránh gợi ý vào những giừo 00:00 đến 5:00 sáng  
         - Sử dụng 1-2 emoji phù hợp với hoạt động
         - Dùng ngôn ngữ thân thiện, trực tiếp (ví dụ: "Bạn nên...")
         - Không sử dụng ký tự đặc biệt trong phần nội dung gợi ý

        4. Đối với khoảng trống cuối ngày, thêm nội dung: "Bạn đã làm việc cả một ngày mệt mỏi rồi, hãy tận hưởng thời gian nghỉ ngơi đi nhé."

        5. TUYỆT ĐỐI CHỈ trả về danh sách gợi ý hoạt động, không thêm lời chào, giới thiệu hay kết thúc, không nhắc lại lịch trình hiện tại của người dùng.

        """

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "Bạn là trợ lý lập lịch trình chuyên nghiệp. Hãy trả lời bằng Tiếng Việt. "},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Lỗi khi gọi AI: {str(e)}"
