"""
Ticket model — support tickets created by AI agents or humans.
"""
from __future__ import annotations

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, SoftDeleteMixin, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    pass


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_ON_CUSTOMER = "waiting_on_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Ticket(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """A support ticket linked to a conversation."""

    __tablename__ = "tickets"

    # ── Tenant ───────────────────────────────────────────────
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── Link to conversation (optional — tickets can be standalone) ──
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Ticket Content ───────────────────────────────────────
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Status & Priority ────────────────────────────────────
    priority: Mapped[TicketPriority] = mapped_column(
        Enum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM
    )
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus), nullable=False, default=TicketStatus.OPEN
    )

    # ── Assignment ───────────────────────────────────────────
    assigned_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Contact info (denormalised for quick display) ─────────
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── Indexes ───────────────────────────────────────────────
    __table_args__ = (
        Index("ix_tickets_org_status", "organization_id", "status"),
        Index("ix_tickets_org_priority", "organization_id", "priority"),
        Index("ix_tickets_conversation", "conversation_id"),
        Index("ix_tickets_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Ticket id={self.id} title={self.title!r} status={self.status}>"
