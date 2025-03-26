import logging

from fastapi import APIRouter, Query
import logging

from schemas.schemas import AiScheduleResponse, AiSuggestion
from services.ai_service import get_ai_suggestions
from database.mongo_services import db
from datetime import datetime
from bson import ObjectId, errors

router = APIRouter()


@router.get("/noti-suggestion", response_model=AiScheduleResponse)
def get_ai_schedule_suggestion(userId: str = Query(..., description="ID của người dùng")):
    try:
        # Kiểm tra userId có hợp lệ không
        user_id = userId

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
            return AiScheduleResponse(
                httpStatus=200,
                resultCode="204 NO CONTENT",
                resultMsg="Không có lịch trình cho hôm nay",
                resourceId=user_id,
                responseTimestamp=datetime.utcnow().isoformat(),
                data=[]
            )

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
        suggestions_list = [AiSuggestion(**s) for s in ai_suggestions]

        return AiScheduleResponse(
            httpStatus=200,
            resultCode="100 CONTINUE",
            resultMsg="Lấy gợi ý thành công",
            resourceId=user_id,
            responseTimestamp=datetime.utcnow().isoformat(),
            data=suggestions_list
        )

    except Exception as e:
        return AiScheduleResponse(
            httpStatus=500,
            resultCode="500 INTERNAL SERVER ERROR",
            resultMsg="Đã xảy ra lỗi trong quá trình xử lý",
            resourceId=userId,
            responseTimestamp=datetime.utcnow().isoformat(),
            data=[],
            error=str(e)
        )
