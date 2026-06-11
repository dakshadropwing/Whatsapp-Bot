"""
Step Executors — functions that execute specific workflow actions.
"""
from __future__ import annotations

import logging
from typing import Any, Callable
import uuid

logger = logging.getLogger(__name__)


def send_message_executor(payload: dict, conversation_id: str | None, context: dict) -> dict:
    body = payload.get("body", "")
    logger.info("Executing send_message: %s to %s", body, conversation_id)
    if conversation_id:
        try:
            from app.extensions import db
            from app.integrations.whatsapp.client import WhatsAppClient
            from app.models.conversation import Conversation

            conv = db.session.get(Conversation, uuid.UUID(conversation_id))
            if conv:
                client = WhatsAppClient()
                res = client.send_text(conv.contact_phone, body)
                return {
                    "status": "success",
                    "message_id": res.get("messages", [{}])[0].get("id") if res else None,
                }
        except Exception as exc:
            logger.exception("Failed to send whatsapp message in workflow")
            return {"status": "failed", "error": str(exc)}
    return {"status": "skipped", "reason": "no_conversation_id"}


def create_ticket_executor(payload: dict, conversation_id: str | None, context: dict) -> dict:
    title = payload.get("title", "Workflow Ticket")
    description = payload.get("description", "")
    logger.info("Executing create_ticket: %s", title)
    if conversation_id:
        try:
            from app.extensions import db
            from app.models.conversation import Conversation
            from app.services.ticket_service import TicketService

            conv = db.session.get(Conversation, uuid.UUID(conversation_id))
            if conv:
                ticket = TicketService.create_support_ticket(
                    org_id=str(conv.organization_id),
                    title=title,
                    description=description,
                    priority="MEDIUM",
                    phone=conv.contact_phone,
                    name=conv.contact_name,
                    conversation_id=conversation_id,
                )
                return {"status": "success", "ticket_id": str(ticket.id)}
        except Exception as exc:
            logger.exception("Failed to create ticket in workflow")
            return {"status": "failed", "error": str(exc)}
    return {"status": "skipped", "reason": "no_conversation_id"}


def update_context_executor(payload: dict, conversation_id: str | None, context: dict) -> dict:
    logger.info("Executing update_context: %s", payload)
    context.update(payload)
    if conversation_id:
        try:
            from app.extensions import db
            from app.models.conversation import Conversation

            conv = db.session.get(Conversation, uuid.UUID(conversation_id))
            if conv:
                conv.context.update(payload)
                db.session.commit()
        except Exception as exc:
            logger.exception("Failed to persist conversation context in workflow")
    return {"status": "success"}


def wait_executor(payload: dict, conversation_id: str | None, context: dict) -> dict:
    duration = payload.get("duration_seconds", 0)
    logger.info("Executing wait: %d seconds", duration)
    return {"status": "paused", "duration_seconds": duration}


EXECUTORS: dict[str, Callable] = {
    "send_message": send_message_executor,
    "create_ticket": create_ticket_executor,
    "update_context": update_context_executor,
    "wait": wait_executor,
}


def get_executor(action: str) -> Callable[[dict, str | None, dict], Any] | None:
    return EXECUTORS.get(action)
