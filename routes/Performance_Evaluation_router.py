import os
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from openai import OpenAI
from pydantic import BaseModel

from database.mongo_services import schedules_collection

load_dotenv()
router = APIRouter()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class ScheduleResponse(BaseModel):
    name: str
    startTime: str
    endTime: str
    date: str
    repeat: str


class ScheduleAnalysisResponse(BaseModel):
    httpStatus: int
    resultCode: str
    resultMsg: str
    resourceId: str
    responseTimestamp: str
    data: Dict[str, Any]


@router.get("/schedules/evaluate/{user_id}")
async def evaluate_schedule(user_id: str):
    try:
        # Lấy lịch trình trong tuần
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        query = {
            "userId": user_id,
            "date": {
                "$gte": start_of_week.strftime('%Y-%m-%d'),
                "$lte": end_of_week.strftime('%Y-%m-%d')
            }
        }

        projection = {"name": 1, "startTime": 1, "endTime": 1, "_id": 0}
        schedules = list(schedules_collection.find(query, projection))

        if not schedules:
            raise HTTPException(status_code=404, detail="Không tìm thấy lịch trình")

        # Gửi dữ liệu lịch trình cho GPT để phân tích và đánh giá
        gpt_prompt = f"""
        Dưới đây là dữ liệu lịch trình của người dùng trong tuần:

        {json.dumps(schedules, ensure_ascii=False)}

        Phân tích và đánh giá lịch trình này cho tôi:

        1. Phân bổ thời gian cho các hoạt động mà bạn tự nhận diện được.
        2. Ba sự kiện phổ biến nhất trong lịch trình.
        3. Đánh giá sức khỏe của lịch trình theo các mức: "Poor", "Average", "Good", "Excellent".
        4. Chấm điểm tổng thể từ 0 đến 10 và cung cấp lời khuyên để cải thiện lịch trình.

        LƯU Ý QUAN TRỌNG:
        - Tổng 4 giá trị trong event_time PHẢI CHÍNH XÁC BẰNG 100
        - Phải trả về đúng định dạng JSON hợp lệ
        - Không được chứa bất kỳ ký tự nào ngoài JSON
        - Không được có newlines (\\n) hoặc thụt lề trong JSON
        - Tất cả strings phải được đặt trong dấu ngoặc kép
        - Chỉ trả về duy nhất JSON, không có bất kỳ text nào khác

        Cấu trúc JSON mà bạn cần trả về phải giống như sau:
        {{
            "event_time": {{
                "Work_Study": 45.2,
                "Entertainment_Relaxation": 25.5,
                "Physical_Health": 20.3,
                "Others": 9.0
            }},
            "Priority_events": [
                "1st : event_name",
                "2nd : event_name",
                "3rd : event_name"
            ],
            "calendar_health": "Poor/Average/Good/Excellent",
            "Overall_score": 7.5,
            "Advice": "string"
        }}
      
        """

        # Gửi yêu cầu GPT để phân tích lịch trình
        gpt_response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Changed from "gpt-4o-mini" as it might not exist
            messages=[{"role": "user", "content": gpt_prompt}],
            response_format={"type": "json_object"},  # Force JSON output
            max_tokens=550
        )

        gpt_analysis = gpt_response.choices[0].message.content

        # Xử lý phản hồi từ GPT
        try:
            # Tìm vị trí bắt đầu và kết thúc của JSON
            json_start = gpt_analysis.find('{')
            json_end = gpt_analysis.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                raise ValueError("Không tìm thấy JSON hợp lệ trong phản hồi GPT")

            # Cắt chuỗi để chỉ lấy phần JSON
            json_str = gpt_analysis[json_start:json_end]

            # Parse JSON
            gpt_result = json.loads(json_str)

            # Validate cấu trúc JSON
            required_keys = ["event_time", "Priority_events", "calendar_health", "Overall_score", "Advice"]
            if not all(key in gpt_result for key in required_keys):
                raise ValueError("Thiếu các trường bắt buộc trong phản hồi GPT")

        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Lỗi phân tích JSON từ GPT: {str(e)}. Nguyên bản response: {gpt_analysis}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Lỗi xử lý phản hồi GPT: {str(e)}. Nguyên bản response: {gpt_analysis}"
            )

        # Trả về kết quả JSON đã được phân tích
        return ScheduleAnalysisResponse(
            httpStatus=200,
            resultCode="100 CONTINUE",
            resultMsg="User schedule analysis retrieved successfully",
            resourceId=str(uuid.uuid4()),  # hoặc có thể dùng user_id nếu muốn
            responseTimestamp=datetime.utcnow().isoformat(),
            data=gpt_result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

