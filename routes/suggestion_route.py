from fastapi import APIRouter, Query
from services.ai_service import get_ai_suggestions
from database.mongo_services import db
from datetime import datetime
from bson import ObjectId, errors

router = APIRouter()


@router.get("/ai-suggestion")
def get_ai_schedule_suggestion(userId: str = Query(..., description="ID của người dùng")):
    try:
        # Kiểm tra userId có phải ObjectId hợp lệ không
        try:
            user_id = userId
        except errors.InvalidId:
            return {"error": "userId không hợp lệ. Định dạng ObjectId không đúng."}

        schedules = db["schedules"]
        today = datetime.now().strftime("%Y-%m-%d")

        pipeline = [
            {"$match": {"date": today, "userId": user_id}},

            {"$lookup": {
                "from": "categories", "localField": "categoryId", "foreignField": "_id", "as": "category"}},
            {"$unwind": {"path": "$category", "preserveNullAndEmptyArrays": True}},
            {"$lookup": {
                "from": "users", "localField": "userId", "foreignField": "_id", "as": "user"}},
            {"$unwind": {"path": "$user", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "_id": 1, "startTime": 1, "endTime": 1, "name": 1, "description": 1,
                "categoryName": "$category.name",
                "occupation": "$user.Occupation", "gender": "$user.gender", "hobbies": "$user.hobbies"
            }}
        ]

        data = list(schedules.aggregate(pipeline))
        if not data:
            return {"message": "Không có lịch trình cho hôm nay."}

        user_data = data[0]
        hobbies = user_data.get("hobbies", [])
        if isinstance(hobbies, str):
            hobbies = [h.strip() for h in hobbies.split(",") if h.strip()]

        user_info = {
            "occupation": user_data.get("occupation", "Không rõ"),
            "gender": user_data.get("gender", "Không rõ"),
            "hobbies": ", ".join(hobbies) if hobbies else "Không có"
        }

        ai_suggestions = get_ai_suggestions(data, user_info)
        return {"suggestions": ai_suggestions}

    except Exception as e:
        return {"error": str(e)}
