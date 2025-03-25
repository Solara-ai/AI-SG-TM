from fastapi import APIRouter, Query
from services.statistics_service import get_daily_statistics

router = APIRouter(prefix="/api/statistics")

@router.get("")
def get_statistics(date: str = Query(..., description="Ngày cần thống kê (YYYY-MM-DD)")):
    return get_daily_statistics(date)
