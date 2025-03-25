from pydantic import BaseModel
from typing import List, Optional


class MessageRequest(BaseModel):
    user_id: str
    text: str


class MessageResponse(BaseModel):
    reply: str


class CategoryStats(BaseModel):
    _id: str
    count: int


class StatisticsResponse(BaseModel):
    date: str
    total_schedules: int
    total_users: int
    top_categories: List[CategoryStats]
