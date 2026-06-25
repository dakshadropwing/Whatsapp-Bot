"""
ActivityLog model — user/agent activity logs.
"""
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class ActivityLog(Base, UUIDMixin, TimestampMixin):
    """Log of minor activities/events triggered by users or automated scripts."""

    __tablename__ = "activity_logs"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    activity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)

    __table_args__ = (
        Index("ix_activity_logs_org_type", "organization_id", "activity_type"),
        Index("ix_activity_logs_user", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<ActivityLog id={self.id} type={self.activity_type!r}>"
