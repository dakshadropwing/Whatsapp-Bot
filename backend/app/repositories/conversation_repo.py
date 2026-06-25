"""
Conversation Repository — WhatsApp thread lookups & state queries.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from app.extensions import db
from app.models.conversation import Conversation, ConversationStatus
from app.repositories.base_repository import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    """Specialised repository for Conversation entity queries."""

    def __init__(self) -> None:
        super().__init__(Conversation)

    def find_by_phone(self, phone: str) -> Optional[Conversation]:
        """Return the most recent conversation for a given phone number."""
        return db.session.execute(
            select(Conversation)
            .where(Conversation.contact_phone == phone)
            .order_by(Conversation.created_at.desc())
            .limit(1)
        ).scalar_one_or_none()

    def find_active_by_phone(self, phone: str) -> Optional[Conversation]:
        """Return the latest *active* conversation for a phone number."""
        return db.session.execute(
            select(Conversation)
            .where(
                Conversation.contact_phone == phone,
                Conversation.status.in_([
                    ConversationStatus.ACTIVE,
                    ConversationStatus.WAITING,
                    ConversationStatus.BOT_HANDLING,
                    ConversationStatus.HUMAN_HANDLING,
                ]),
            )
            .order_by(Conversation.created_at.desc())
            .limit(1)
        ).scalar_one_or_none()

    def find_by_organization(
        self, org_id: str, status: Optional[ConversationStatus] = None
    ) -> list[Conversation]:
        """List conversations for an organization, optionally filtered by status."""
        query = select(Conversation).where(
            Conversation.organization_id == org_id
        )
        if status:
            query = query.where(Conversation.status == status)
        query = query.order_by(Conversation.created_at.desc())
        return db.session.execute(query).scalars().all()
