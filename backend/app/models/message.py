"""
Message model — individual WhatsApp messages within a conversation.
"""
from __future__ import annotations

import uuid
import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.conversation import Conversation


class MessageDirection(str, enum.Enum):
    INBOUND = "inbound"    # From customer → platform
    OUTBOUND = "outbound"  # From platform → customer


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    LOCATION = "location"
    CONTACTS = "contacts"
    INTERACTIVE = "interactive"
    TEMPLATE = "template"
    REACTION = "reaction"
    STICKER = "sticker"
    SYSTEM = "system"


class MessageStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class Message(Base, UUIDMixin, TimestampMixin):
    """
    Individual WhatsApp message.
    Partitioned by created_at for performance at scale.
    """

    __tablename__ = "messages"

    # ── Tenant ───────────────────────────────────────────────
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )

    # ── Conversation ─────────────────────────────────────────
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── WhatsApp Wire Fields ──────────────────────────────────
    wa_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Meta's ID
    direction: Mapped[MessageDirection] = mapped_column(
        Enum(MessageDirection), nullable=False
    )
    message_type: Mapped[MessageType] = mapped_column(
        Enum(MessageType), nullable=False, default=MessageType.TEXT
    )
    status: Mapped[MessageStatus] = mapped_column(
        Enum(MessageStatus), nullable=False, default=MessageStatus.PENDING
    )

    # ── Content ───────────────────────────────────────────────
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    media_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    media_size: Mapped[int | None] = mapped_column(nullable=True)
    raw_payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # ── AI Metadata ───────────────────────────────────────────
    ai_generated: Mapped[bool] = mapped_column(nullable=False, default=False)
    ai_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    tokens_used: Mapped[int | None] = mapped_column(nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(nullable=True)

    # ── Relationships ────────────────────────────────────────
    conversation: Mapped["Conversation"] = relationship(
        "Conversation", back_populates="messages"
    )

    # ── Indexes ───────────────────────────────────────────────
    __table_args__ = (
        Index("ix_messages_conversation_id", "conversation_id"),
        Index("ix_messages_wa_message_id", "wa_message_id"),
        Index("ix_messages_org_created", "organization_id", "created_at"),
        Index("ix_messages_direction", "direction"),
        Index("ix_messages_status", "status"),
        Index("ix_messages_ai_generated", "ai_generated"),
    )

    def __repr__(self) -> str:
        return f"<Message id={self.id} type={self.message_type} dir={self.direction}>"
