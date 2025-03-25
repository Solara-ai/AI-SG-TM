from database.mongo_services import db
from datetime import datetime


def get_statistics():
    now = datetime.now()
    first_day = datetime(now.year, now.month, 1)

    user_count = db["users"].count_documents({})
    new_users_this_month = db["users"].count_documents({"created_at": {"$gte": first_day}})
    schedule_count = db["schedules"].count_documents({})
    feedback_count = db["feedbacks"].count_documents({})

    return {
        "user_count": user_count,
        "new_users_this_month": new_users_this_month,
        "schedule_count": schedule_count,
        "feedback_count": feedback_count
    }

