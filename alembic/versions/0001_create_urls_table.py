"""create urls table

Revision ID: 0001
Revises:
Create Date: 2024-11-13 21:38:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "urls",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("short_code", sa.String(length=16), nullable=True),
        sa.Column("original_url", sa.String(length=2048), nullable=False),
        sa.Column("clicks", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("last_accessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_urls_short_code", "urls", ["short_code"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_urls_short_code", table_name="urls")
    op.drop_table("urls")
