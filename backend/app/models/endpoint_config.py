"""
EndpointConfig model — user-configured webhook URLs per organization.

Agents use the EndpointTool to call these endpoints dynamically,
allowing non-technical users to wire up external systems via the admin UI.
"""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class EndpointConfig(Base, UUIDMixin, TimestampMixin):
    """A custom webhook endpoint configured for an organization."""

    __tablename__ = "endpoint_configs"

    # ── Tenant ───────────────────────────────────────────────
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── Endpoint Definition ──────────────────────────────────
    name: Mapped[str] = mapped_column(
        String(100), nullable=False,
    )  # e.g. "order_status", "crm_update"
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    method: Mapped[str] = mapped_column(
        String(10), nullable=False, default="POST",
    )  # GET | POST | PUT | PATCH

    # ── Auth / Headers ───────────────────────────────────────
    headers: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict,
    )  # e.g. {"Authorization": "Bearer xxx"}

    # ── Status ───────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True,
    )

    # ── Indexes ───────────────────────────────────────────────
    __table_args__ = (
        Index("ix_endpoint_configs_org_name", "organization_id", "name", unique=True),
        Index("ix_endpoint_configs_org_active", "organization_id", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<EndpointConfig id={self.id} name={self.name!r} url={self.url!r}>"
