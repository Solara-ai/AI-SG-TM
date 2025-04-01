import json
import logging

from fastapi import APIRouter, Query
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


        # Kiểm tra nếu ai_suggestions là chuỗi JSON hợp lệ
        if isinstance(ai_suggestions, str):
            try:
                # Chuyển chuỗi JSON thành dict
                ai_suggestions = json.loads(ai_suggestions)
            except json.JSONDecodeError as e:
                print(f"JSONDecodeError: {str(e)}")
                ai_suggestions = []

        # Trả về chuỗi JSON dạng chuẩn
        return AiScheduleResponse(
            httpStatus=200,
            resultCode="100 CONTINUE",
            resultMsg="Lấy gợi ý thành công",
            resourceId=user_id,
            responseTimestamp=datetime.utcnow().isoformat(),
            data=ai_suggestions  # Trả về dữ liệu ở dạng list[dict] đã chuyển từ JSON string
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
