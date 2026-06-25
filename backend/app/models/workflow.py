"""
Workflow model — automated multi-step sequences triggered by events.
"""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin


class Workflow(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """An automated workflow definition with triggers and steps."""

    __tablename__ = "workflows"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    trigger: Mapped[str] = mapped_column(String(100), nullable=False, default="manual")
    trigger_config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    steps: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_run_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    run_count: Mapped[int] = mapped_column(nullable=False, default=0)

    __table_args__ = (
        Index("ix_workflows_org_active", "organization_id", "is_active"),
        Index("ix_workflows_org_trigger", "organization_id", "trigger"),
    )

    def __repr__(self) -> str:
        return f"<Workflow id={self.id} name={self.name!r}>"
