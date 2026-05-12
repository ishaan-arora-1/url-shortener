from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .config import get_settings
from .models import URL
from .shortcode import encode

settings = get_settings()


async def get_by_code(db: AsyncSession, code: str) -> URL | None:
    result = await db.execute(select(URL).where(URL.short_code == code))
    return result.scalar_one_or_none()


async def get_by_original(db: AsyncSession, original_url: str) -> URL | None:
    result = await db.execute(select(URL).where(URL.original_url == original_url))
    return result.scalars().first()


async def create_short_url(db: AsyncSession, original_url: str) -> URL:
    """Create a mapping for original_url, or return the existing one if we've seen it."""
    existing = await get_by_original(db, original_url)
    if existing is not None:
        return existing

    url = URL(original_url=original_url)
    db.add(url)
    # Flush to get the auto-incremented id, then derive the code from it.
    await db.flush()
    url.short_code = encode(url.id + settings.id_offset)
    await db.commit()
    await db.refresh(url)
    return url


async def register_click(sessionmaker: async_sessionmaker[AsyncSession], code: str) -> None:
    """Bump the click counter and last-accessed time for a code.

    Runs in its own session as a background task so it never slows the redirect.
    """
    async with sessionmaker() as session:
        await session.execute(
            update(URL)
            .where(URL.short_code == code)
            .values(clicks=URL.clicks + 1, last_accessed_at=func.now())
        )
        await session.commit()
