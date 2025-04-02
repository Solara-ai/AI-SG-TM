import os
from datetime import datetime
from typing import Dict, List
import json

from dotenv import load_dotenv
from openai import OpenAI
from fastapi import APIRouter, HTTPException

from routes.Performance_Evaluation_router import ScheduleResponse, router, get_weekly_schedules, logger
from routes.chat_router import openai_client
from schemas.schemas import TimeAnalysisResponse, TimePercentageResponse

load_dotenv()
openai_clients = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter()


def calculate_percentage(time_stats: dict) -> dict:
    """Tính phần trăm và đảm bảo tổng 100%"""
    total_hours = sum(time_stats.values())
    if total_hours == 0:
        return {"working": 0, "sleeping": 0, "entertainment": 0, "free": 0}  # Trả về 0% cho tất cả nếu không có dữ liệu

    # Tính phần trăm và phần dư
    categories = ["working", "sleeping", "entertainment", "free"]
    percentages = {
        cat: (time_stats[cat] / total_hours) * 100
        for cat in categories
    }

    # Làm tròn xuống và tính phần dư
    rounded = {cat: int(percentages[cat]) for cat in categories}
    remainder = 100 - sum(rounded.values())

    # Phân bổ phần dư vào category có phần thập phân lớn nhất
    if remainder > 0:
        max_decimal_cat = max(categories, key=lambda cat: percentages[cat] % 1)
        rounded[max_decimal_cat] += remainder

    return rounded


def calculate_duration(start: str, end: str) -> float:
    """Tính số giờ giữa 2 mốc thời gian"""
    fmt = "%H:%M:%S"
    start_time = datetime.strptime(start, fmt)
    end_time = datetime.strptime(end, fmt)
    return (end_time - start_time).total_seconds() / 3600


@router.post("/schedules/time-percentage/{user_id}")
async def get_time_percentage(user_id: str):
    try:
        logger.info(f"Fetching schedules for user {user_id}")
        weekly_schedules = await get_weekly_schedules(user_id)
        logger.info(f"Raw schedule data: {weekly_schedules}")

        if not weekly_schedules or sum(weekly_schedules.values()) == 0:
            logger.warning("Empty or zero-time schedule detected")
            return {
                "time_percentages": [
                    {"category": "working", "percentage": "0%"},
                    {"category": "sleeping", "percentage": "0%"},
                    {"category": "entertainment", "percentage": "0%"},
                    {"category": "free", "percentage": "0%"}
                ],
                "total_hours": 168
            }

        percentages = calculate_percentage(weekly_schedules)
        logger.info(f"Calculated percentages: {percentages}")

        return {
            "time_percentages": [
                {"category": "working", "percentage": f"{percentages['working']}%"},
                {"category": "sleeping", "percentage": f"{percentages['sleeping']}%"},
                {"category": "entertainment", "percentage": f"{percentages['entertainment']}%"},
                {"category": "free", "percentage": f"{percentages['free']}%"}
            ],
            "total_hours": 168
        }

    except Exception as e:
        logger.error(f"Calculation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Time distribution calculation failed: {str(e)}"
        )
@router.post("/schedules/analyze-week/{user_id}", response_model=TimeAnalysisResponse)
async def analyze_weekly_schedule(user_id: str):
    try:
        # Lấy dữ liệu từ API trước
        weekly_schedules = await get_weekly_schedules(user_id)

        # Tính phần trăm thời gian
        time_stats = calculate_percentage(weekly_schedules)

        # Chuẩn bị prompt cho GPT
        prompt = f"""Hãy phân tích lịch trình sau và trả về JSON đúng format:
{{
    "priority_events": {{
        "1st": "[sự kiện được dùng nhiều nhất]",
        "2nd": "[sự kiện được dùng nhiều nhì]",
        "3rd": "[sự kiện được dùng nhiều ba]"
    }},
    "health_evaluation": "[excellent/good/fair/poor]",
    "total_score": [0.0-10.0] ,
    "advice": "[lời khuyên chi tiết bằng tiếng anh về việc cân bằng thời gian đi làm việc vui chơi và ăn uống ngủ nghỉ]"
}}

Thống kê thời gian:
- Làm việc: {time_stats['working']}%
- Ngủ: {time_stats['sleeping']}%
- Giải trí: {time_stats['entertainment']}%
- Thời gian trống: {time_stats['free']}%
Total_score thì chấm điểm dựa trên giờ giấc khoa học, ăn ngủ nghỉ, làm việc, chơi bời điểm được chấm với số thập phân"""

        # Gọi OpenAI API
        response = openai_clients.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Bạn là chuyên gia phân tích thời gian biểu."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        gpt_response = json.loads(response.choices[0].message.content)

        return {
            "priority_events": gpt_response["priority_events"],
            "health_evaluation": gpt_response["health_evaluation"],
            "total_score": gpt_response["total_score"],
            "advice": gpt_response["advice"]
        }

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed")