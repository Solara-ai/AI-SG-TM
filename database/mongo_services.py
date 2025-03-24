import uuid
from datetime import datetime
from http.client import HTTPException

from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client["sgtm"]
chat_collection = db["conversations"]


#
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


#
# def delete_conversation(conversation_id):
#     result = chat_collection.delete_one({"_id": conversation_id.strip()})
#     if result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="Conversation not found")
#     return {"message": "Conversation deleted successfully"}
#

def get_history(user_id: str):
    return chat_collection.find_one({
        "_id": user_id.strip(),
    })
