import redis.asyncio as redis

from .config import get_settings

settings = get_settings()

_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    """Return a lazily-created, process-wide async Redis client.

    Exposed as a dependency so it can be swapped out in tests.
    """
    global _client
    if _client is None:
        _client = redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    return _client


def cache_key(short_code: str) -> str:
    return f"url:{short_code}"
