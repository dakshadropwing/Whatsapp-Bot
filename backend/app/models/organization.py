"""
Organization model — top-level multi-tenant unit.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db
from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.whatsapp_account import WhatsAppAccount


class Organization(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Represents a tenant (company / client organization).
    All resources belong to an organization — enforcing multi-tenancy.
    """

    __tablename__ = "organizations"

    # ── Core Fields ──────────────────────────────────────────
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # ── Plan & Billing ───────────────────────────────────────
    plan: Mapped[str] = mapped_column(
        String(50), nullable=False, default="starter"
    )  # starter | professional | enterprise
    max_users: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    max_agents: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    max_conversations_per_month: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1000
    )

    # ── Status ───────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # ── Settings (flexible JSON) ──────────────────────────────
    settings: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # ── Relationships ────────────────────────────────────────
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="organization", lazy="dynamic"
    )
    whatsapp_accounts: Mapped[list["WhatsAppAccount"]] = relationship(
        "WhatsAppAccount", back_populates="organization", lazy="dynamic"
    )

    # ── Indexes ───────────────────────────────────────────────
    __table_args__ = (
        Index("ix_organizations_slug", "slug"),
        Index("ix_organizations_is_active", "is_active"),
        Index("ix_organizations_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Organization id={self.id} slug={self.slug}>"
