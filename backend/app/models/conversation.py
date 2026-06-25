"""
Conversation model — tracks a WhatsApp thread with a contact.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
import enum

if TYPE_CHECKING:
    from app.models.message import Message
    from app.models.ai_session import AISession


class ConversationStatus(str, enum.Enum):
    ACTIVE = "active"
    WAITING = "waiting"           # Waiting for customer reply
    BOT_HANDLING = "bot_handling"
    HUMAN_HANDLING = "human_handling"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"


class ConversationChannel(str, enum.Enum):
    WHATSAPP = "whatsapp"
    WHATSAPP_BUSINESS = "whatsapp_business"


class Conversation(Base, UUIDMixin, TimestampMixin):
    """A conversation thread between the platform and a WhatsApp contact."""

    __tablename__ = "conversations"

    # ── Tenant ───────────────────────────────────────────────
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── WhatsApp Identity ────────────────────────────────────
    whatsapp_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("whatsapp_accounts.id", ondelete="CASCADE"),
        nullable=False,
    )
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_wa_id: Mapped[str] = mapped_column(String(50), nullable=False)

    # ── Status ───────────────────────────────────────────────
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus), nullable=False, default=ConversationStatus.ACTIVE
    )
    channel: Mapped[ConversationChannel] = mapped_column(
        Enum(ConversationChannel),
        nullable=False,
        default=ConversationChannel.WHATSAPP,
    )

    # ── Agent Assignment ─────────────────────────────────────
    assigned_agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_agents.id", ondelete="SET NULL"),
        nullable=True,
    )
    assigned_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Context & Metadata ───────────────────────────────────
    context: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    tags: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="normal")
    message_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_message_at: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # ── Relationships ────────────────────────────────────────
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", lazy="dynamic", order_by="Message.created_at"
    )
    ai_sessions: Mapped[list["AISession"]] = relationship(
        "AISession", back_populates="conversation", lazy="dynamic"
    )

    # ── Indexes & Partitioning ───────────────────────────────
    __table_args__ = (
        Index("ix_conversations_org_contact", "organization_id", "contact_phone"),
        Index("ix_conversations_status", "status"),
        Index("ix_conversations_org_status", "organization_id", "status"),
        Index("ix_conversations_wa_account", "whatsapp_account_id"),
        Index("ix_conversations_created_at", "created_at"),
        Index("ix_conversations_last_msg", "last_message_at"),
    )

    def __repr__(self) -> str:
        return f"<Conversation id={self.id} contact={self.contact_phone} status={self.status}>"
