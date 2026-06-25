"""
WebhookLog model — recording incoming/outgoing webhook payloads and statuses.
"""
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class WebhookLog(Base, UUIDMixin, TimestampMixin):
    """Execution/audit log for webhooks sent or received."""

    __tablename__ = "webhook_logs"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    endpoint_config_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("endpoint_configs.id", ondelete="SET NULL"),
        nullable=True,
    )
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    request_payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    response_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_webhook_logs_org_event", "organization_id", "event_type"),
        Index("ix_webhook_logs_endpoint", "endpoint_config_id"),
    )

    def __repr__(self) -> str:
        return f"<WebhookLog id={self.id} event={self.event_type!r} status={self.status_code}>"
