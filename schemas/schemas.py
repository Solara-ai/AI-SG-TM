from pydantic import BaseModel


class MessageRequest(BaseModel):
    user_id: str
    text: str


class MessageResponse(BaseModel):
    reply: str
