from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả FE gọi API (hoặc thay bằng domain cụ thể)
    allow_credentials=True,
    allow_methods=["*"],  # Cho phép tất cả phương thức (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # Cho phép tất cả header
)