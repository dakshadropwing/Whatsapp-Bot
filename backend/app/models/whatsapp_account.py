"""
WhatsAppAccount model — credentials and configuration for WhatsApp Business API.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.organization import Organization


class WhatsAppAccount(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """WhatsApp Business API Account settings for an organization."""

    __tablename__ = "whatsapp_accounts"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    phone_number_id: Mapped[str] = mapped_column(String(50), nullable=False)
    waba_id: Mapped[str] = mapped_column(String(50), nullable=False)
    access_token: Mapped[str] = mapped_column(Text, nullable=False)
    verify_token: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="whatsapp_accounts"
    )

    def __repr__(self) -> str:
        return f"<WhatsAppAccount id={self.id} phone_number_id={self.phone_number_id}>"
