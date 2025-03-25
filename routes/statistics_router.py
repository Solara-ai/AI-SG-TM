from datetime import datetime
from fastapi import APIRouter
from database.mongo_services import db
from services.statistics_service import get_statistics

router = APIRouter()


@router.get("/statistics")
def statistics():
    return get_statistics()


@router.get("/recent-activities")
def get_recent_activities():
    activities = []

    # 🟢 Lấy người dùng mới đăng ký gần nhất
    new_user = db["users"].find_one({}, {"userName": 1, "phone": 1})
    if new_user:
        activities.append({
            "text": f"Người dùng mới đăng ký: {new_user['userName']}.",
            "phonenumber": new_user["phone"],
            "time": None  # Không có thời gian, để tránh lỗi
        })

    # 🔵 Lấy cuộc trò chuyện mới nhất
    recent_chat = db["conversations"].find_one({}, {"user_id": 1, "created_at": 1}, sort=[("created_at", -1)])
    if recent_chat and "created_at" in recent_chat:
        user = db["users"].find_one({"_id": recent_chat["user_id"]}, {"userName": 1})
        user_name = user["userName"] if user else "Người dùng ẩn danh"
        activities.append({
            "text": f"{user_name} vừa chat với bot.",
            "time": recent_chat["created_at"]
        })

    # 🟠 Lấy feedback mới nhất
    recent_feedback = db["feedbacks"].find_one({}, {"userId": 1, "createdAt": 1}, sort=[("createdAt", -1)])
    if recent_feedback and "createdAt" in recent_feedback:
        user = db["users"].find_one({"_id": recent_feedback["userId"]}, {"userName": 1})
        user_name = user["userName"] if user else "Người dùng ẩn danh"
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
