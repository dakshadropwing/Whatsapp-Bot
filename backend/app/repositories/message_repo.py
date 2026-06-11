"""
Message Repository — persisting and querying chat history logs.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from app.extensions import db
from app.models.message import Message, MessageDirection, MessageStatus
from app.repositories.base_repository import BaseRepository


class MessageRepository(BaseRepository[Message]):
    """Specialised repository for Message entity queries."""

    def __init__(self) -> None:
        super().__init__(Message)

    def find_by_conversation(
        self, conversation_id: str, limit: int = 50
    ) -> list[Message]:
        """Return the most recent messages for a conversation, oldest first."""
        return (
            db.session.execute(
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
            )
            .scalars()
            .all()
        )

    def find_by_wa_message_id(self, wa_message_id: str) -> Optional[Message]:
        """Look up a message by Meta's WhatsApp message ID."""
        return db.session.execute(
            select(Message).where(Message.wa_message_id == wa_message_id)
        ).scalar_one_or_none()

    def count_by_conversation(self, conversation_id: str) -> int:
        """Return the total message count for a conversation."""
        from sqlalchemy import func
        result = db.session.execute(
            select(func.count())
            .select_from(Message)
            .where(Message.conversation_id == conversation_id)
        ).scalar()
        return result or 0

    def find_failed_by_organization(self, org_id: str, limit: int = 100) -> list[Message]:
        """Return recently failed outbound messages for an organization."""
        return (
            db.session.execute(
                select(Message)
                .where(
                    Message.organization_id == org_id,
                    Message.status == MessageStatus.FAILED,
                )
                .order_by(Message.created_at.desc())
                .limit(limit)
            )
            .scalars()
            .all()
        )
