from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from config import settings
from core.request_logger import RequestLoggerMiddleware


from routes import api_router
from utils.logger import configure_logging

app = FastAPI(
    port=8001,
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    root_path=settings.ROOT_PATH,
    docs_url="/swagger-ui.html",
    openapi_url="/openapi.json",
    redoc_url=None,
)


# Setup các thành phần
configure_logging()

app.include_router(api_router)