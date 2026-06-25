"""
Conversation Service — thread lifecycle, assignment, status transitions.
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from sqlalchemy import func, select

from app.extensions import db
from app.models.conversation import Conversation, ConversationStatus

logger = logging.getLogger(__name__)


class ConversationService:
    """Manages WhatsApp conversation threads — listing, assignment, status changes."""

    @staticmethod
    def list_conversations(
        org_id: str,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
    ) -> dict:
        """Return a paginated list of conversations for an organization."""
        query = select(Conversation).where(
            Conversation.organization_id == uuid.UUID(org_id)
        )
        if status:
            try:
                query = query.where(Conversation.status == ConversationStatus(status))
            except ValueError:
                pass
        if search:
            term = f"%{search.lower()}%"
            query = query.where(
                db.or_(
                    Conversation.contact_phone.like(term),
                    func.lower(Conversation.contact_name).like(term),
                )
            )

        total = db.session.execute(
            select(func.count()).select_from(query.subquery())
        ).scalar() or 0

        conversations = (
            db.session.execute(
                query.order_by(Conversation.last_message_at.desc().nulls_last(), Conversation.created_at.desc())
                .offset((page - 1) * per_page)
                .limit(per_page)
            )
            .scalars()
            .all()
        )

        return {
            "data": [
                {
                    "id": str(c.id),
                    "organization_id": str(c.organization_id),
                    "contact_phone": c.contact_phone,
                    "contact_name": c.contact_name,
                    "contact_wa_id": c.contact_wa_id,
                    "status": c.status.value if c.status else None,
                    "channel": c.channel.value if c.channel else None,
                    "assigned_agent_id": str(c.assigned_agent_id) if c.assigned_agent_id else None,
                    "assigned_user_id": str(c.assigned_user_id) if c.assigned_user_id else None,
                    "priority": c.priority,
                    "message_count": c.message_count,
                    "last_message_at": c.last_message_at,
                    "tags": c.tags or [],
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "updated_at": c.updated_at.isoformat() if c.updated_at else None,
                }
                for c in conversations
            ],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    @staticmethod
    def get_conversation(conversation_id: str) -> Optional[Conversation]:
        """Fetch a single conversation by ID."""
        return db.session.get(Conversation, uuid.UUID(conversation_id))

    @staticmethod
    def assign_conversation(
        conversation_id: str,
        assigned_user_id: Optional[str] = None,
        assigned_agent_id: Optional[str] = None,
    ) -> Optional[Conversation]:
        """Assign a conversation to a human user or AI agent."""
        conv = db.session.get(Conversation, uuid.UUID(conversation_id))
        if not conv:
            return None
        if assigned_user_id:
            conv.assigned_user_id = uuid.UUID(assigned_user_id)
            conv.status = ConversationStatus.HUMAN_HANDLING
        if assigned_agent_id:
            conv.assigned_agent_id = uuid.UUID(assigned_agent_id)
            conv.status = ConversationStatus.BOT_HANDLING
        db.session.commit()
        logger.info("Assigned conversation %s", conv.id)
        return conv

    @staticmethod
    def update_conversation(conversation_id: str, **kwargs) -> Optional[Conversation]:
        """Update conversation fields."""
        conv = db.session.get(Conversation, uuid.UUID(conversation_id))
        if not conv:
            return None
        for key, value in kwargs.items():
            if hasattr(conv, key) and key not in ("id", "organization_id"):
                if key == "status" and isinstance(value, str):
                    try:
                        value = ConversationStatus(value)
                    except ValueError:
                        continue
                elif key in ("assigned_user_id", "assigned_agent_id", "whatsapp_account_id"):
                    if not value:
                        value = None
                    elif isinstance(value, str):
                        try:
                            value = uuid.UUID(value)
                        except ValueError:
                            continue
                setattr(conv, key, value)
        db.session.commit()
        return conv

    @staticmethod
    def resolve_conversation(conversation_id: str) -> Optional[Conversation]:
        """Mark a conversation as resolved."""
        conv = db.session.get(Conversation, uuid.UUID(conversation_id))
        if not conv:
            return None
        conv.status = ConversationStatus.RESOLVED
        db.session.commit()
        logger.info("Resolved conversation %s", conv.id)
        return conv

    @staticmethod
    def escalate_conversation(conversation_id: str) -> Optional[Conversation]:
        """Escalate a conversation to human handling."""
        conv = db.session.get(Conversation, uuid.UUID(conversation_id))
        if not conv:
            return None
        conv.status = ConversationStatus.ESCALATED
        db.session.commit()
        logger.info("Escalated conversation %s", conv.id)
        return conv

    @staticmethod
    def get_or_create(
        org_id: str,
        phone: str,
        wa_id: str,
        wa_account_id: str,
        contact_name: Optional[str] = None,
    ) -> tuple[Conversation, bool]:
        """Get existing active conversation or create a new one. Returns (conversation, created)."""
        existing = db.session.execute(
            select(Conversation).where(
                Conversation.organization_id == uuid.UUID(org_id),
                Conversation.contact_phone == phone,
                Conversation.status.in_([
                    ConversationStatus.ACTIVE,
                    ConversationStatus.WAITING,
                    ConversationStatus.BOT_HANDLING,
                ]),
            ).order_by(Conversation.created_at.desc()).limit(1)
        ).scalar_one_or_none()

        if existing:
            return existing, False

        conv = Conversation(
            organization_id=uuid.UUID(org_id),
            whatsapp_account_id=uuid.UUID(wa_account_id),
            contact_phone=phone,
            contact_wa_id=wa_id,
            contact_name=contact_name,
            status=ConversationStatus.ACTIVE,
        )
        db.session.add(conv)
        db.session.commit()
        logger.info("Created conversation %s for %s", conv.id, phone)
        return conv, True
