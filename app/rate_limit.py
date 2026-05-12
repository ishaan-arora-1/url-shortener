import redis.asyncio as redis
from fastapi import Depends, HTTPException, Request, status

from .cache import get_redis
from .config import get_settings

settings = get_settings()


async def rate_limiter(
    request: Request,
    cache: redis.Redis = Depends(get_redis),
) -> None:
    """Fixed-window IP rate limit backed by Redis.

    Counts requests per client IP in a WINDOW-second bucket and rejects with 429
    once RATE_LIMIT_MAX is exceeded.
    """
    client_ip = request.client.host if request.client else "unknown"
    key = f"ratelimit:{client_ip}"

    count = await cache.incr(key)
    if count == 1:
        await cache.expire(key, settings.rate_limit_window)

    if count > settings.rate_limit_max:
        retry_after = await cache.ttl(key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="rate limit exceeded, slow down",
            headers={"Retry-After": str(max(retry_after, 1))},
        )
