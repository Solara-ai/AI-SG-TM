from datetime import datetime

from fastapi import APIRouter, Query

from database.mongo_services import db
from services.statistics_service import get_statistics, get_recent_activities

router = APIRouter(prefix="/api")


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
            "phonenumber": new_user["phone"]
        })

    # 🔵 Lấy cuộc trò chuyện mới nhất
    recent_chat = db["conversations"].find_one({}, {"user_id": 1, "created_at": 1}, sort=[("created_at", -1)])
    if recent_chat:
        user = db["users"].find_one({"_id": recent_chat["user_id"]}, {"userName": 1})
        user_name = user["userName"] if user else "Người dùng ẩn danh"
        activities.append({
            "text": f"{user_name} vừa chat với bot.",
            "time": recent_chat["created_at"]
        })

    # 🟠 Lấy feedback mới nhất
    recent_feedback = db["feedbacks"].find_one({}, {"userId": 1, "message": 1})
    if recent_feedback:
        user = db["users"].find_one({"_id": recent_feedback["userId"]}, {"userName": 1})
        user_name = user["userName"] if user else "Người dùng ẩn danh"
        activities.append({
            "text": f"{user_name} vừa gửi feedback mới.",
            "time": recent_feedback["created_at"]
        })

    # 📌 Sắp xếp tất cả activities theo thời gian giảm dần
    activities = sorted(activities, key=lambda x: x["time"], reverse=True)

    # Format lại thời gian
    for activity in activities:
        activity["time"] = datetime.strftime(activity["time"], "%H:%M ngày %d/%m/%Y")

    return activities
