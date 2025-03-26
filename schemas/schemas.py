from typing import Optional, List

from pydantic import BaseModel


class MessageRequest(BaseModel):
    user_id: str
    text: str


class MessageResponse(BaseModel):
    httpStatus: int
    resultCode: str
    resultMsg: str
    resourceId: str
    responseTimestamp: str


class ChatMessage(BaseModel):
    reply: str

class UserChatHistoryData(BaseModel):
    user_id: str
    messages: List[ChatMessage]


class UserChatHistoryResponse(BaseModel):
    httpStatus: int
    resultCode: str
    resultMsg: str
    resourceId: str
    responseTimestamp: str
    data: UserChatHistoryData

class AiSuggestion(BaseModel):
    activity: str
    recommendation: str
    startTime: str
    endTime: str

class AiScheduleResponse(BaseModel):
    httpStatus: int
    resultCode: str
    resultMsg: str
    resourceId: str
    responseTimestamp: str
    data: List[AiSuggestion]
    error: Optional[str] = None  # Chỉ có khi có lỗi