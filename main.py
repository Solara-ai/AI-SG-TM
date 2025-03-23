from fastapi import FastAPI

from routes.chat_router import router as chat_router
from routes.suggestion_route import router as suggestion_router

app = FastAPI(
    title="My API",
    description="This is a sample API",
    version="1.0",
    docs_url="api/ai/swagger-ui.html",
    redoc_url="/redocs"
)

app.include_router(suggestion_router)
app.include_router(chat_router)
