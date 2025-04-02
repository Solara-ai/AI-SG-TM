from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import logging
from database.mongo_services import schedules_collection

router = APIRouter()
logger = logging.getLogger(__name__)


class ScheduleResponse(BaseModel):
    name: str
    startTime: str
    endTime: str
    date: str
    repeat: str


def validate_schedule(schedule: dict) -> bool:
    """Kiểm tra schedule có đủ các trường bắt buộc và hợp lệ"""
    required_fields = ['name', 'startTime', 'endTime', 'date']
    for field in required_fields:
        if field not in schedule or not schedule[field]:
            logger.warning(f"Missing or empty field '{field}' in schedule: {schedule}")
            return False

    try:
        datetime.strptime(schedule['date'], '%Y-%m-%d')
        datetime.strptime(schedule['startTime'], '%H:%M:%S')  # Thêm validate thời gian
    except ValueError:
        logger.warning(f"Invalid date/time format in schedule: {schedule}")
        return False

    return True


@router.get("/schedules/current-week/{user_id}", response_model=List[ScheduleResponse])
async def get_weekly_schedules(user_id: str):
    try:
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        query = {
            "userId": user_id,
            "$or": [
                {
                    "date": {
                        "$gte": start_of_week.strftime('%Y-%m-%d'),
                        "$lte": end_of_week.strftime('%Y-%m-%d')
                    }
                },
                {
                    "repeat": {"$in": ["DAILY", "WEEKLY"]},
                    "date": {"$exists": True, "$ne": None}
                }
            ]
        }

        projection = {
            "name": 1,
            "startTime": 1,
            "endTime": 1,
            "date": 1,
            "repeat": 1,
            "_id": 0
        }

        schedules = list(schedules_collection.find(query, projection).sort("date", 1))

        filtered_schedules = []

        for schedule in schedules:
            if not validate_schedule(schedule):
                continue

            repeat = schedule.get("repeat", "NONE")
            schedule_date = datetime.strptime(schedule['date'], '%Y-%m-%d').date()

            if repeat == "DAILY":
                for day in range(7):
                    current_date = start_of_week + timedelta(days=day)
                    filtered_schedules.append({
                        "name": schedule['name'],
                        "startTime": schedule['startTime'],
                        "endTime": schedule['endTime'],
                        "date": current_date.strftime('%Y-%m-%d'),
                        "repeat": repeat
                    })
            elif repeat == "WEEKLY":
                if schedule_date.weekday() < 7:
                    current_date = start_of_week + timedelta(days=schedule_date.weekday())
                    filtered_schedules.append({
                        "name": schedule['name'],
                        "startTime": schedule['startTime'],
                        "endTime": schedule['endTime'],
                        "date": current_date.strftime('%Y-%m-%d'),
                        "repeat": repeat
                    })
            else:
                if start_of_week <= schedule_date <= end_of_week:
                    filtered_schedules.append({
                        "name": schedule['name'],
                        "startTime": schedule['startTime'],
                        "endTime": schedule['endTime'],
                        "date": schedule['date'],
                        "repeat": repeat
                    })

        # SẮP XẾP THEO DATE RỒI ĐẾN STARTTIME
        filtered_schedules.sort(key=lambda x: (x['date'], x['startTime']))

        return filtered_schedules

    except Exception as e:
        logger.error(f"Error fetching schedules: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing schedules"
        )