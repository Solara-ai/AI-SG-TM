import os
from datetime import datetime
import uuid
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from openai import OpenAI

from schemas.schemas import MessageRequest, MessageResponse, UserChatHistoryResponse, ChatMessage
from database.mongo_services import add_message, get_history, chat_collection, users_collection

load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
router = APIRouter()


def get_bot_reply(text: str) -> str:
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "Bạn là một người hỗ trợ người dùng trong việc tạo lịch trình dựa trên sở thích lịch trình công việc bạn  "},
                {"role": "user", "content": text}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Lỗi khi kết nối với OpenAI: " + str(e)

@router.post("", response_model=UserChatHistoryResponse)
async def chat(msg: MessageRequest):
    # Kiểm tra user_id có tồn tại trong users collection không
    user_exists = users_collection.find_one({"_id": msg.user_id})
    if not user_exists:
        raise HTTPException(status_code=400, detail="User ID không tồn tại")

    reply = get_bot_reply(msg.text)

    # Tạo tin nhắn mới
    new_message = {
        "text": msg.text,
        "reply": reply,
    }

    # Kiểm tra user_id đã có trong chat_collection chưa
    user_chat = chat_collection.find_one({"user_id": msg.user_id})

    if user_chat:
        # Nếu đã có, cập nhật danh sách messages
        chat_collection.update_one(
            {"user_id": msg.user_id},
            {"$push": {"messages": new_message}}
        )
    else:
        # Nếu chưa có, tạo mới
        chat_collection.insert_one({
            "_id": str(uuid.uuid4()),
            "user_id": msg.user_id,
            "messages": [new_message],
            "created_at": datetime.utcnow().isoformat()
        })

    return UserChatHistoryResponse(
        httpStatus=200,
        resultCode="100 CONTINUE",
        resultMsg="Chat response generated successfully",
        resourceId=msg.user_id,
        responseTimestamp=datetime.utcnow().isoformat(),
        data={"messages": [new_message]}
    )



@router.get("/history/{user_id}", response_model=UserChatHistoryResponse)
async def get_user_history(user_id: str):
    user_chat = chat_collection.find_one({"user_id": user_id})

    if not user_chat:
        return UserChatHistoryResponse(
            httpStatus=404,
            resultCode="404 NOT FOUND",
            resultMsg="No chat history found for this user",
            resourceId=user_id,
            responseTimestamp=datetime.utcnow().isoformat(),
            data={
                "user_id": user_id,
                "messages": []
            }
        )

    # Lấy toàn bộ messages nhưng loại bỏ timestamp
    history = [
        {
            "text": msg["text"],
            "reply": msg["reply"]
        }
        for msg in user_chat.get("messages", [])
    ]

    return UserChatHistoryResponse(
        httpStatus=200,
        resultCode="100 CONTINUE",
        resultMsg="User chat history retrieved successfully",
        resourceId=user_id,
        responseTimestamp=datetime.utcnow().isoformat(),
        data={
            "user_id": user_id,
            "messages": history  # Danh sách messages không có timestamp
        }
    )
#
# @router.delete("/conversation/{conversation_id}")
# async def delete_conversation(conversation_id: str):
#     if not conversation_id:
#         raise HTTPException(status_code=400, detail="Thiếu conversation_id")
#     print(f"conversation_id nhận được: {conversation_id}")
#     result = chat_collection.delete_one({"_id": conversation_id.strip()})  # đảm bảo việc xóa khoảng trắng
#     if result.deleted_count == 1:
#         return {"message": "Xóa cuộc hội thoại thành công"}
#     return {"message": "Không tìm thấy cuộc hội thoại"}

#
# @router.post("/new_conversation/{user_id}")
# async def new_conversation(user_id: str):
#     new_conversation_id = str(uuid4())
#     conversation = {
#         "_id": new_conversation_id,
#         "user_id": user_id,
#         "messages": [],
#         "created_at": datetime.now()
#     }
#     chat_collection.insert_one(conversation)
#     return {
#         "message": "Đã tạo cuộc hội thoại mới",
#         "conversation_id": new_conversation_id
#     }
