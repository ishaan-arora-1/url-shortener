from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, pool_pre_ping=True, future=True)

SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a request-scoped database session."""
    async with SessionLocal() as session:
        yield session


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Expose the session factory for code that needs its own session.

    Used by the background click-counter, which runs after the request session
    is already closed. Overridable in tests.
    """
    return SessionLocal
