from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
import time
import logging
from typing import Awaitable, Callable

logger = logging.getLogger(__name__)


class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(
            self,
            request: Request,
            call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start_time = time.time()
        logger.info(f"Request started: {request.method} {request.url}")

        try:
            response = await call_next(request)

            # Thêm Header CORS vào Response
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"

            process_time = (time.time() - start_time) * 1000
            logger.info(
                f"Request completed | "
                f"Status: {response.status_code} | "
                f"Duration: {process_time:.2f}ms"
            )

            return response

        except Exception as exc:
            logger.error(f"Request failed: {exc}", exc_info=True)
            raise