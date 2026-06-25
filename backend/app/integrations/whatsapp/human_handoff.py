"""
Human Handoff Integration — manages Bot to Human Agent handoff logic.
"""
from __future__ import annotations

import logging
import uuid

from app.extensions import db
from app.models.conversation import Conversation, ConversationStatus
from app.models.message import Message, MessageDirection, MessageType
from app.services.ticket_service import TicketService
from app.tasks.notification_tasks import send_critical_alert

logger = logging.getLogger(__name__)


def escalate_to_human(conversation_id: str, reason: str | None = None) -> bool:
    """
    Escalate a conversation from Bot Handling to Human Handling.
    Creates a support ticket and alerts organization users.
    """
    try:
        conv_uuid = uuid.UUID(conversation_id)
        conv = db.session.get(Conversation, conv_uuid)
        if not conv:
            logger.error("Handoff: Conversation %s not found", conversation_id)
            return False

        if conv.status == ConversationStatus.HUMAN_HANDLING:
            logger.info("Conversation %s is already in human handling status", conversation_id)
            return True

        logger.info("Escalating conversation %s to human; reason: %s", conversation_id, reason)

        # Update conversation status
        conv.status = ConversationStatus.HUMAN_HANDLING
        conv.priority = "high"

        # Create system message logging escalation event
        sys_msg = Message(
            organization_id=conv.organization_id,
            conversation_id=conv_uuid,
            direction=MessageDirection.OUTBOUND,
            message_type=MessageType.SYSTEM,
            body=f"System: Escalated to human handling. Reason: {reason or 'Bot handoff requested'}",
            raw_payload={"reason": reason},
        )
        db.session.add(sys_msg)

        # Create support ticket in the background
        TicketService.create_support_ticket(
            org_id=str(conv.organization_id),
            title=f"Chat Escalation: {conv.contact_phone}",
            description=f"Automated bot escalation for contact {conv.contact_name or conv.contact_phone}.\nReason: {reason or 'Not specified'}",
            priority="HIGH",
            phone=conv.contact_phone,
            name=conv.contact_name,
            conversation_id=conversation_id,
        )

        db.session.commit()

        # Trigger critical alert asynchronously to notify agents
        send_critical_alert.delay(
            org_id=str(conv.organization_id),
            title="Conversation Escalated",
            body=f"Conversation with {conv.contact_phone} has been escalated to human handling. Reason: {reason or 'None'}",
        )

        return True
    except Exception as exc:
        logger.exception("Failed to escalate conversation %s to human agent", conversation_id)
        db.session.rollback()
        return False
