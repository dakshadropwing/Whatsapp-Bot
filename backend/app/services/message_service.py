"""
Message Service — persist and query WhatsApp messages.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func, select

from app.extensions import db
from app.models.conversation import Conversation
from app.models.message import Message, MessageDirection, MessageStatus, MessageType

logger = logging.getLogger(__name__)


class MessageService:
    """Handles message persistence, history retrieval, and status updates."""

    @staticmethod
    def list_messages(
        conversation_id: str,
        page: int = 1,
        per_page: int = 50,
        direction: Optional[str] = None,
    ) -> dict:
        """Return paginated message history for a conversation."""
        query = select(Message).where(
            Message.conversation_id == uuid.UUID(conversation_id)
        )
        if direction:
            try:
                query = query.where(Message.direction == MessageDirection(direction))
            except ValueError:
                pass

        total = db.session.execute(
            select(func.count()).select_from(query.subquery())
        ).scalar() or 0

        messages = (
            db.session.execute(
                query.order_by(Message.created_at.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            .scalars()
            .all()
        )

        return {
            "data": [
                {
                    "id": str(m.id),
                    "organization_id": str(m.organization_id),
                    "conversation_id": str(m.conversation_id),
                    "wa_message_id": m.wa_message_id,
                    "direction": m.direction.value,
                    "message_type": m.message_type.value,
                    "status": m.status.value,
                    "body": m.body,
                    "media_url": m.media_url,
                    "ai_generated": m.ai_generated,
                    "tokens_used": m.tokens_used,
                    "processing_time_ms": m.processing_time_ms,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in messages
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    @classmethod
    def create_message(
        cls,
        org_id: str,
        conversation_id: str,
        direction: str,
        body: Optional[str] = None,
        message_type: str = "text",
        wa_message_id: Optional[str] = None,
        media_url: Optional[str] = None,
        ai_generated: bool = False,
        tokens_used: Optional[int] = None,
        processing_time_ms: Optional[int] = None,
    ) -> Message:
        """Create and persist a new message, updating the parent conversation."""
        msg = Message(
            organization_id=uuid.UUID(org_id),
            conversation_id=uuid.UUID(conversation_id),
            direction=MessageDirection(direction),
            message_type=MessageType(message_type),
            status=MessageStatus.PENDING if direction == "outbound" else MessageStatus.DELIVERED,
            body=body,
            wa_message_id=wa_message_id,
            media_url=media_url,
            ai_generated=ai_generated,
            tokens_used=tokens_used,
            processing_time_ms=processing_time_ms,
        )
        db.session.add(msg)

        # Update conversation metadata
        conv = db.session.get(Conversation, uuid.UUID(conversation_id))
        if conv:
            conv.message_count = (conv.message_count or 0) + 1
            conv.last_message_at = datetime.now(timezone.utc).isoformat()

        db.session.commit()
        logger.info("Created message %s in conversation %s", msg.id, conversation_id)
        return msg

    @staticmethod
    def update_status(message_id: str, status: str) -> Optional[Message]:
        """Update message delivery status (e.g. from Meta webhook callbacks)."""
        msg = db.session.get(Message, uuid.UUID(message_id))
        if not msg:
            return None
        try:
            msg.status = MessageStatus(status)
        except ValueError:
            return None
        db.session.commit()
        return msg

    @staticmethod
    def update_status_by_wa_id(wa_message_id: str, status: str) -> Optional[Message]:
        """Update status using Meta's WhatsApp message ID."""
        msg = db.session.execute(
            select(Message).where(Message.wa_message_id == wa_message_id)
        ).scalar_one_or_none()
        if not msg:
            return None
        try:
            msg.status = MessageStatus(status)
        except ValueError:
            return None
        db.session.commit()
        return msg

    @staticmethod
    def get_failed_messages(org_id: str, limit: int = 100) -> list[Message]:
        """Return recently failed outbound messages for retry."""
        return (
            db.session.execute(
                select(Message)
                .where(
                    Message.organization_id == uuid.UUID(org_id),
                    Message.status == MessageStatus.FAILED,
                )
                .order_by(Message.created_at.desc())
                .limit(limit)
            )
            .scalars()
            .all()
        )
