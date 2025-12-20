import time
import uuid

from fastapi import Depends, FastAPI, Request
from structlog.contextvars import bind_contextvars, clear_contextvars

from kalamna.apps.authentication.routers import router as auth_router
from kalamna.core.config import setup_logging
from kalamna.core.redis import get_redis
from kalamna.utils.logger import get_logger

setup_logging()
logger = get_logger()

app = FastAPI(
    title="Kalamna Backend API",
    description="Backend API for Kalamna - Customer Service Egyptian AI-powered platform",
    version="1.0.0",
)

app.include_router(auth_router, prefix="/api/v1")


@app.get("/")
def hello():
    logger.info("health_check")
    return {"message": "Hello, World!"}


@app.get("/redis/check")
async def redis_check(redis=Depends(get_redis)):
    await redis.set("ping", "pong", ex=5)
    return await redis.get("ping")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    bind_contextvars(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )

    start = time.perf_counter()
    try:
        response = await call_next(request)
        return response
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "http_request_completed",
            status_code=getattr(response, "status_code", None),
            duration_ms=round(duration_ms, 2),
        )
        clear_contextvars()
