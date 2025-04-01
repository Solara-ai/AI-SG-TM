import uuid
from datetime import datetime
from http.client import HTTPException
from config import settings
from bson import ObjectId
from pymongo import MongoClient
import os

mongo_client = MongoClient(settings.MONGO_URI)
db = mongo_client["sgtm"]
chat_collection = db["conversations"]
users_collection = db["users"]
schedules_collection = db["schedules"]
feedbacks_collection = db["feedbacks"]

# def create_conversation(user_id: str):
#     conversation_id = str(uuid.uuid4())  # Tạo ID dạng chuỗi
#     chat_collection.insert_one({
#         "_id": conversation_id,
#         "user_id": user_id.strip(),
#         "messages": [],
#         "created_at": datetime.now()
#     })
#     return conversation_id  # Trả về để FE hoặc API lưu lại

def add_message(conversation_id, user_text, bot_reply):
    chat_collection.update_one(
        {"_id": conversation_id.strip()},
        {"$push": {
            "messages": {
                "user": user_text,
                "bot": bot_reply
            }}
        }
    )

def get_history(user_id: str):
    return chat_collection.find_one({
        "_id": user_id.strip(),
    })

