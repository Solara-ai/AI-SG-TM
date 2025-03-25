# 📅 Lịch trình Gợi ý + Chatbot API — FastAPI Project

## 👋 Giới thiệu
Dự án này xây dựng một hệ thống gợi ý lịch trình cho người dùng kết hợp cùng chatbot. Toàn bộ API được phát triển bằng FastAPI, hỗ trợ các chức năng:
- Gợi ý lịch trình cá nhân hóa.
- API để thêm/sửa/xoá nội dung liên quan đến chatbot.

## 🚀 Công nghệ sử dụng
Dự án được phát triển bằng Python 3.10+ và sử dụng các thư viện chính sau:
- **FastAPI**: Framework để xây dựng API nhanh chóng và hiệu quả.
- **Uvicorn**: ASGI server để chạy ứng dụng FastAPI.
- **Pydantic**: Hỗ trợ xử lý dữ liệu đầu vào/ra cho API.
- **SQLAlchemy**: ORM để làm việc với cơ sở dữ liệu.
- **SQLite hoặc PostgreSQL**: Cơ sở dữ liệu, tùy theo cấu hình.

## 📂 Cấu trúc thư mục
```
project/
│
├── app/
│   ├── main.py        # Điểm bắt đầu API
│   ├── routers/
│   │   ├── schedule.py  # API gợi ý lịch trình
│   │   └── chatbot.py   # API thêm/sửa/xoá cho chatbot
│   ├── models/          # Định nghĩa các bảng CSDL
│   ├── schemas/         # Định nghĩa các schema dùng Pydantic
│   ├── services/        # Xử lý logic ứng dụng
│
├── requirements.txt  # Danh sách thư viện cần cài đặt
├── README.md         # Hướng dẫn sử dụng dự án
```

## 📌 Các chức năng chính

### 1. Gợi ý lịch trình
- **Endpoint**: `GET /schedule/suggest`
- **Chức năng**: Trả về danh sách lịch trình phù hợp với người dùng dựa trên các tham số như sở thích, thời gian rảnh, mục tiêu cá nhân,...
- **Lỗi có thể gặp**: Nếu dữ liệu đầu vào thiếu, API sẽ báo lỗi, cần kiểm tra kỹ schema của Pydantic trước khi gửi request.

### 2. Quản lý chatbot
- **Thêm nội dung**: `POST /chatbot/create`
- **Sửa nội dung**: `PUT /chatbot/update/{id}`
- **Xoá nội dung**: `DELETE /chatbot/delete/{id}`
- **Lỗi có thể gặp**: Nếu ID không tồn tại, API sẽ báo lỗi, cần xử lý exception rõ ràng trong code.

## ⚙️ Hướng dẫn cài đặt và chạy dự án

### 1. Clone dự án về máy
```bash
git clone https://github.com/yourusername/schedule-chatbot-api.git
cd schedule-chatbot-api
```

### 2. Tạo và kích hoạt môi trường ảo
```bash
python -m venv venv
source venv/bin/activate  # Trên macOS/Linux
venv\Scripts\activate    # Trên Windows
```

### 3. Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

### 4. Chạy ứng dụng
```bash
uvicorn app.main:app --reload
```
- Sau khi chạy, API sẽ có thể truy cập tại: `http://127.0.0.1:8000`
- Để xem tài liệu API tự động: `http://127.0.0.1:8000/docs`

## 🛠 Một số lỗi có thể gặp khi cài đặt và cách xử lý
1. **Lỗi "ModuleNotFoundError: No module named 'fastapi'"**:
   - Nguyên nhân: FastAPI chưa được cài đặt.
   - Cách khắc phục: Chạy `pip install -r requirements.txt`.

2. **Lỗi "venv: command not found"**:
   - Nguyên nhân: Python chưa cài đặt hoặc chưa được thêm vào PATH.
   - Cách khắc phục: Kiểm tra bằng `python --version`, nếu chưa có thì cần cài đặt Python.

3. **Lỗi cổng 8000 đã bị chiếm dụng**:
   - Nguyên nhân: Có một ứng dụng khác đang chạy trên cổng 8000.
   - Cách khắc phục: Chạy với cổng khác, ví dụ: `uvicorn app.main:app --reload --port 8080`.

Chúc bạn cài đặt thành công! 🚀
