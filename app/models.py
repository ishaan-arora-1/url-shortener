from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base

# Postgres uses BIGINT; SQLite (used in tests) only autoincrements its INTEGER rowid.
BigIntPK = BigInteger().with_variant(Integer, "sqlite")


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    # Filled in right after insert once we know the row id (see crud.create_short_url).
    short_code: Mapped[str | None] = mapped_column(String(16), unique=True, index=True)
    original_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    clicks: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    last_accessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
