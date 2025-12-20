import time

from fastapi import Depends, FastAPI, Request

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
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Apply global prefix for all auth routes
app.include_router(auth_router, prefix="/api/v1")


@app.get("/")
def hello():
    return {"message": "Hello, World!"}


@app.get("/redis/check")
async def redis_check(redis=Depends(get_redis)):
    await redis.set("ping", "pong", ex=5)
    return await redis.get("ping")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Capture simple per-request telemetry to the kalamna logger
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "HTTP %s %s -> %s (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response
