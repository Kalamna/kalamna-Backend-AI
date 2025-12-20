import logging

from fastapi import Depends, FastAPI

from kalamna.apps.authentication.routers import router as auth_router
from kalamna.core.config import setup_logging
from kalamna.core.redis import get_redis

setup_logging()

logger = logging.getLogger("kalamna")

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
