from fastapi import FastAPI

from routes.statistics_router import router as statistics_router
from routes.chat_router import router as chat_router
from routes.suggestion_route import router as suggestion_router

app = FastAPI(
    docs_url="/swagger-ui.html",  # Thay đổi đường dẫn Swagger UI
    redoc_url=None,  # (Tùy chọn) Tắt Redoc nếu không cần
    openapi_url="/openapi.json"  # (Tùy chọn) Thay đổi OpenAPI JSON
)

app.include_router(suggestion_router)
app.include_router(chat_router)
app.include_router(statistics_router)
