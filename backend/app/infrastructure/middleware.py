"""
Infrastructure — Middleware (request logging, error handling).
"""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger("crm")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs every request: method, path, status, duration."""

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        try:
            response = await call_next(request)
        except Exception as exc:
            logger.exception(f"Unhandled error on {request.method} {request.url.path}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )
        duration = round((time.time() - start) * 1000, 1)
        logger.info(
            f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)"
        )
        response.headers["X-Process-Time-Ms"] = str(duration)
        return response
