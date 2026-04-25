"""Reusable column groups for ORM models."""

from __future__ import annotations

from datetime import UTC, datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


def _utc_now() -> datetime:
    return datetime.now(tz=UTC)


class TimestampMixin:
    """created_at from DB default; updated_at refreshed on ORM UPDATE events."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=_utc_now,
        nullable=False,
    )
