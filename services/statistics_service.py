from datetime import datetime
from database.mongo_services import db

def get_daily_statistics(date: str):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d")

        schedules = db["schedules"]

        # In ra ngày cần lọc để kiểm tra
        print(f"Fetching statistics for date: {date_obj}")

        pipeline = [
            {"$match": {"date": date_obj}},  # Lọc theo ngày cụ thể
            {"$group": {
                "_id": "$categoryId",
                "total_schedules": {"$sum": 1},
                "users_involved": {"$addToSet": "$userId"}
            }},
            {"$lookup": {
                "from": "categories",
                "localField": "_id",
                "foreignField": "_id",
                "as": "category"
            }},
            {"$unwind": {"path": "$category", "preserveNullAndEmptyArrays": True}},
            {"$project": {
                "_id": 0,
                "category_name": "$category.name",
                "total_schedules": 1,
                "users_count": {"$size": "$users_involved"}
            }}
        ]

        # In ra pipeline để kiểm tra
        print(f"Aggregation pipeline: {pipeline}")

        data = list(schedules.aggregate(pipeline))
        print(f"Query result: {data}")  # In kết quả query để debug
        return {"date": date_obj, "statistics": data}

    except Exception as e:
        print(f"Error: {e}")  # Log lỗi nếu có
        return {"error": str(e)}
