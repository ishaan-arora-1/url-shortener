import redis.asyncio as redis
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from . import crud
from .cache import cache_key, get_redis
from .config import get_settings
from .database import get_db, get_sessionmaker
from .rate_limit import rate_limiter
from .schemas import ShortenRequest, ShortenResponse, StatsResponse

settings = get_settings()

app = FastAPI(
    title="URL Shortener",
    description="Shorten long URLs and redirect through short codes.",
    version="0.1.0",
)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/shorten",
    response_model=ShortenResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limiter)],
    tags=["links"],
)
async def shorten(payload: ShortenRequest, db: AsyncSession = Depends(get_db)) -> ShortenResponse:
    url = await crud.create_short_url(db, str(payload.url))
    return ShortenResponse(
        short_code=url.short_code,
        short_url=f"{settings.base_url}/{url.short_code}",
        original_url=url.original_url,
    )


@app.get("/{short_code}/stats", response_model=StatsResponse, tags=["links"])
async def stats(short_code: str, db: AsyncSession = Depends(get_db)) -> StatsResponse:
    url = await crud.get_by_code(db, short_code)
    if url is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="short code not found")
    return StatsResponse.model_validate(url)


@app.get("/{short_code}", tags=["links"])
async def redirect(
    short_code: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    cache: redis.Redis = Depends(get_redis),
    sessionmaker: async_sessionmaker[AsyncSession] = Depends(get_sessionmaker),
) -> RedirectResponse:
    # Fast path: serve straight from Redis without touching Postgres.
    target = await cache.get(cache_key(short_code))
    if target is None:
        url = await crud.get_by_code(db, short_code)
        if url is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="short code not found"
            )
        target = url.original_url
        await cache.set(cache_key(short_code), target, ex=settings.cache_ttl)

    # Count the click after the response goes out, so it never adds latency.
    background_tasks.add_task(crud.register_click, sessionmaker, short_code)
    return RedirectResponse(url=target, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
