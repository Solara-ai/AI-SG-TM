from datetime import datetime
from fastapi import APIRouter
from database.mongo_services import db
from services.statistics_service import get_statistics

router = APIRouter()


@router.get("/statistics")
def statistics():
    return get_statistics()

#có cần thiết đâu
@router.get("/recent-activities")
def get_recent_activities():
    activities = []

    # 🟢 Lấy người dùng mới đăng ký gần nhất
    new_user = db["users"].find_one({}, {"fullName": 1, "phone": 1})
    if new_user:
        user_name = new_user.get("fullName", "Người dùng ẩn danh")  # Tránh lỗi KeyError
        phone = new_user.get("phone", "Không có số điện thoại")  # Tránh lỗi KeyError
        activities.append({
            "text": f"Người dùng mới đăng ký: {user_name}.",
            "phonenumber": phone,
            "time": None  # Không có thời gian, tránh lỗi sắp xếp
        })

    # 🔵 Lấy cuộc trò chuyện mới nhất
    recent_chat = db["conversations"].find_one({}, {"user_id": 1, "timestamp": 1}, sort=[("timestamp", -1)])
    if recent_chat and "timestamp" in recent_chat:
        user = db["users"].find_one({"_id": recent_chat["user_id"]}, {"userName": 1})
        user_name = user.get("userName", "Người dùng ẩn danh") if user else "Người dùng ẩn danh"
        activities.append({
            "text": f"{user_name} vừa chat với bot.",
            "time": recent_chat["timestamp"]
        })

    # 🟠 Lấy feedback mới nhất
    recent_feedback = db["feedbacks"].find_one({}, {"userId": 1, "messages": 1, "createdAt": 1}, sort=[("createdAt", -1)])
    if recent_feedback and "createdAt" in recent_feedback:
        user = db["users"].find_one({"_id": recent_feedback["userId"]}, {"userName": 1})
        user_name = user.get("userName", "Người dùng ẩn danh") if user else "Người dùng ẩn danh"
        activities.append({
            "text": f"{user_name} vừa gửi feedback mới.",
            "time": recent_feedback["createdAt"]
        })

    # 📌 Lọc và sắp xếp chỉ những activity có `time`
    activities = [a for a in activities if a.get("time") is not None]

    activities.sort(key=lambda x: x["time"], reverse=True)

    # Format lại thời gian
    for activity in activities:
        if isinstance(activity["time"], datetime):
            activity["time"] = activity["time"].strftime("%H:%M ngày %d/%m/%Y")

    return activities