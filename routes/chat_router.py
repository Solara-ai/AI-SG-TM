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
                 "content": "Bạn là một trợ lý AI chuyên lập kế hoạch và lịch trình công việc cho người dùng. "
                            "Lịch trình của bạn phải bắt đầu từ 07:00 sáng và kết thúc không quá 23:00 tối.Tùy theo người Dùng yêu cầu nếu người dùng chỉ yêu cầu gợi ý một sự kiện thôi thì bạn phải đưa ra chỉ một sự kiện thôi nhá không được đưa ra lịch trình cả ngày hay cả tuần đâu  "
                            "không cần cho thêm câu mở đầu khi bạn trả lời đâu đưa thẳng lịch vào luôn"
                            "Hãy tạo lịch trình hợp lý, không chia nhỏ quá từng giờ mà nhóm các hoạt động trong một khoảng thời gian dài hơn, "
                            "ví dụ: từ 07:30 đến 11:45 là một khoảng thời gian cho một hoạt động dài. đặc biệt là đối với các hoạt động liên quan đến công việc và học tập nên kéo dài khoảng một buổi 3-4 tiếng "
                            "Mỗi hoạt động cần có thời gian rõ ràng và phù hợp với một ngày làm việc bình thường. "
                            "khi mà đưa ra lịch trình thì hãy đưa ra ở cuối một câu gì đó như là bạn có thấy lịch trình này phù hợp không ? kiểu như vậy "
                            "khi đưa ra lịch trình như vậy thì cũng hãy đưa ra một vài thời gian để có thể đi tập thể dục thể thao ví dụ : thời gian từ 17:30 - 19:30 | Đi tập thể dục nâng cao sức khỏe "
                            "Lịch trình của bạn phải gợi ý các công việc như: hoàn thành task quan trọng, nghỉ giải lao, ăn trưa, họp nhóm, v.v."
                            "Câu trả lời của bạn phải trả về lịch trình theo format sau:\n\n"
                            "📅 Lịch trình ngày [ngày/tháng/năm]\n"
                            "[Giờ bắt đầu] - [Giờ kết thúc] | [Tên hoạt động] → [Mô tả]\n\n"
                            "Ví dụ:\n"
                            "📅 Lịch trình ngày 03/04/2025\n"
                            "06:00 - 07:00 | Ăn bữa sáng và làm tách caffee | làm bát phở 2 trứng trần  "
                            "08:00 - 11:00 | Hoàn thành công việc | Kiểm tra email và làm báo cáo\n"
                            "11:00 - 12:30 | Nghỉ trưa | Ăn uống và thư giãn\n"
                            "...\n\n"
                            "bạn vẫn trả lời các câu hỏi khác bình thường nhưng khi nào người dùng yêu cầu gợi ý lịch thì hãy tuân thủ format và các ý bên trên"
                            "Lịch trình cần hợp lý, không chia nhỏ từng khoảng thời gian quá chi tiết, và không có hoạt động ngoài khung giờ từ 07:00 đến 23:00."},
                {"role": "user", "content": text}
            ],
            temperature=0.7,  # Thêm độ linh hoạt cho các gợi ý
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
        resultCode="OK",
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
