📅 Lịch trình Gợi ý + Chatbot API — FastAPI Project
👋 Giới thiệu
Dự án này xây dựng một hệ thống gợi ý lịch trình cho người dùng kết hợp cùng chatbot. Toàn bộ API được phát triển bằng FastAPI, hỗ trợ các chức năng:

Gợi ý lịch trình cá nhân hóa.

API để thêm/sửa/xoá nội dung liên quan đến chatbot.

🚀 Công nghệ sử dụng
Python 3.10+

FastAPI

Uvicorn

Pydantic (Xử lý dữ liệu đầu vào/ra)

SQLAlchemy / SQLite hoặc PostgreSQL (tuỳ config)

📂 Cấu trúc thư mục
css
Sao chép
Chỉnh sửa
project/
│
├── app/
│   ├── main.py               # Điểm bắt đầu API
│   ├── routers/
│   │   ├── schedule.py       # API gợi ý lịch trình
│   │   └── chatbot.py        # API thêm/sửa/xoá cho chatbot
│   ├── models/
│   ├── schemas/
│   └── services/
│
├── requirements.txt
└── README.md
📌 Các chức năng chính
1. Gợi ý lịch trình
GET /schedule/suggest: Trả về danh sách lịch trình phù hợp với người dùng.

Params: sở thích, thời gian rảnh, mục tiêu cá nhân,...

Lỗi có thể gặp: Dữ liệu đầu vào thiếu → cần kiểm tra kỹ schema Pydantic.

2. Quản lý chatbot
POST /chatbot/create: Thêm nội dung gợi ý mới cho chatbot.

PUT /chatbot/update/{id}: Sửa nội dung theo ID.

DELETE /chatbot/delete/{id}: Xoá nội dung theo ID.

Lỗi có thể gặp: ID không tồn tại → cần xử lý exception rõ ràng.

⚙️ Cài đặt nhanh
bash
Sao chép
Chỉnh sửa
git clone https://github.com/yourusername/schedule-chatbot-api.git
cd schedule-chatbot-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload