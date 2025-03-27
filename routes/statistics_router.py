from datetime import datetime, timedelta
from fastapi import APIRouter
from database.mongo_services import db, users_collection, chat_collection, schedules_collection
from services.statistics_service import get_statistics

router = APIRouter()

#lấy tổng số người dùng
@router.get("/users/count")
async def get_total_users():
    total_users = users_collection.count_documents({})
    return {"total_users": total_users}

#lấy số người dùng đã sử dụng lịch
@router.get("/users/with_schedule")
async def get_users_with_schedules():
    total_users = users_collection.count_documents({})  # Tổng số người dùng
    users_with_schedules = schedules_collection.distinct("userId")  # Lấy danh sách userId có trong schedules
    unique_users_with_schedules = len(set(users_with_schedules))  # Số lượng user duy nhất

    percentage = (unique_users_with_schedules / total_users * 100) if total_users > 0 else 0

    return {
        "users_with_schedules": unique_users_with_schedules,
        "total_users": total_users,
        "percentage": f"{percentage:.2f}%"
    }


#lấy số người dùng đã chat với ai
@router.get("/users/conversation-percentage")
async def get_users_with_conversation_percentage():
    all_user_ids = users_collection.count_documents({})  # Tổng số người dùng
    user_ids_with_conversation = chat_collection.distinct("user_id")
    unique_users_with_conversation = len(set(user_ids_with_conversation))  # Số lượng user duy nhất

    percentages = (unique_users_with_conversation / all_user_ids * 100) if all_user_ids > 0 else 0

    return {
        "users_with_conversation": unique_users_with_conversation,
        "total_users": all_user_ids,
        "percentage": f"{percentages:.2f}%"
    }



# #có cần thiết đâu
# @router.get("/recent-activities")
# def get_recent_activities():
#     activities = []
#
#     # 🟢 Lấy người dùng mới đăng ký gần nhất
#     new_user = db["users"].find_one({}, {"fullName": 1, "phone": 1})
#     if new_user:
#         user_name = new_user.get("fullName", "Người dùng ẩn danh")  # Tránh lỗi KeyError
#         phone = new_user.get("phone", "Không có số điện thoại")  # Tránh lỗi KeyError
#         activities.append({
#             "text": f"Người dùng mới đăng ký: {user_name}.",
#             "phonenumber": phone,
#             "time": None  # Không có thời gian, tránh lỗi sắp xếp
#         })
#
#     # 🔵 Lấy cuộc trò chuyện mới nhất
#     recent_chat = db["conversations"].find_one({}, {"user_id": 1, "timestamp": 1}, sort=[("timestamp", -1)])
#     if recent_chat and "timestamp" in recent_chat:
#         user = db["users"].find_one({"_id": recent_chat["user_id"]}, {"userName": 1})
#         user_name = user.get("userName", "Người dùng ẩn danh") if user else "Người dùng ẩn danh"
#         activities.append({
#             "text": f"{user_name} vừa chat với bot.",
#             "time": recent_chat["timestamp"]
#         })
#
#     # 🟠 Lấy feedback mới nhất
#     recent_feedback = db["feedbacks"].find_one({}, {"userId": 1, "messages": 1, "createdAt": 1}, sort=[("createdAt", -1)])
#     if recent_feedback and "createdAt" in recent_feedback:
#         user = db["users"].find_one({"_id": recent_feedback["userId"]}, {"userName": 1})
#         user_name = user.get("userName", "Người dùng ẩn danh") if user else "Người dùng ẩn danh"
#         activities.append({
#             "text": f"{user_name} vừa gửi feedback mới.",
#             "time": recent_feedback["createdAt"]
#         })
#
#     # 📌 Lọc và sắp xếp chỉ những activity có `time`
#     activities = [a for a in activities if a.get("time") is not None]
#
#     activities.sort(key=lambda x: x["time"], reverse=True)
#
#     # Format lại thời gian
#     for activity in activities:
#         if isinstance(activity["time"], datetime):
#             activity["time"] = activity["time"].strftime("%H:%M ngày %d/%m/%Y")
#
#     return activities