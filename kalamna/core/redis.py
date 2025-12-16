import os

from redis.asyncio import Redis
from redis.exceptions import ConnectionError

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_redis: Redis | None = None


async def get_redis() -> Redis:
    """
    Lazily initialize Redis connection on first use.
    No FastAPI events needed.
    """
    global _redis

    if _redis is None:
        _redis = Redis.from_url(
            REDIS_URL,
            decode_responses=True,
        )

        # 🔥 Force connection check
        try:
            await _redis.ping()
        except ConnectionError as e:
            _redis = None
            raise RuntimeError("Redis is not reachable") from e

    return _redis


# OPTIONAL: keep these for future use (but unused now)
async def init_redis():
    await get_redis()


async def close_redis():
    global _redis
    if _redis:
        await _redis.close()
        _redis = None
