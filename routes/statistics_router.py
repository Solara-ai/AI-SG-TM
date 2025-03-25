from fastapi import APIRouter, Query
from services.ai_service import get_ai_suggestions
from services.statistics_service import get_statistics
from database.mongo_services import db
from datetime import datetime
from bson import ObjectId, errors

router = APIRouter(prefix="/api")


@router.get("/statistics")
def statistics():
    return get_statistics()
