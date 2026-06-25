"""
User model — platform users (admins, agents, staff).
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.organization import Organization


class User(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Platform user — can belong to one organization with one role."""

    __tablename__ = "users"

    # ── Identity ─────────────────────────────────────────────
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    username: Mapped[str] = mapped_column(String(150), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # ── Auth ─────────────────────────────────────────────────
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    is_superadmin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── Tenant & Role ────────────────────────────────────────
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    role_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Metadata ─────────────────────────────────────────────
    last_login_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_login_ip: Mapped[str | None] = mapped_column(String(45), nullable=True)
    preferences: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # ── Relationships ────────────────────────────────────────
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="users"
    )

    # ── Indexes ───────────────────────────────────────────────
    __table_args__ = (
        Index("ix_users_email_org", "email", "organization_id", unique=True),
        Index("ix_users_organization_id", "organization_id"),
        Index("ix_users_role_id", "role_id"),
        Index("ix_users_is_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
