from fastapi import APIRouter

from routes import Performance_Evaluation_router
from routes.chat_router import router as chat_router
from routes.suggestion_router import router as suggestion_router
from routes.statistics_router import router as statistics_router
from routes.Performance_Evaluation_router import router as Performance_Evaluation_router
from routes.AI_Performance_router import router as AI_Performance_router
# Tạo main router tổng
api_router = APIRouter()

api_router.include_router(chat_router, prefix="/chat", tags=["Chat"])
api_router.include_router(suggestion_router, prefix="/suggestions", tags=["Suggestions"])
api_router.include_router(statistics_router, prefix="/stats", tags=["Statistics"])
api_router.include_router(Performance_Evaluation_router, prefix="/performance", tags=["Performance Evaluation"])
api_router.include_router(AI_Performance_router, prefix="/AI_Performance", tags=["AI_Performance"])

__all__ = ["api_router"]