from fastapi import FastAPI

from routes.chat_router import router as chat_router
from routes.suggestion_route import router as suggestion_router

app = FastAPI()

app.include_router(suggestion_router)
app.include_router(chat_router)
