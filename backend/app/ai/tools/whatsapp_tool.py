"""
WhatsAppTool — send WhatsApp messages as a tool action.

Wraps the existing ``WhatsAppClient``.  Agents use this when they need
to send a *specific* message as a deliberate tool action (confirmations,
follow-ups, notifications), separate from the primary conversational
response that ``BaseAgent.handle()`` sends.
"""
from __future__ import annotations

import logging
from typing import Any

from app.ai.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class SendWhatsAppMessageTool(BaseTool):
    """Send a WhatsApp text message to a phone number."""

    name = "send_whatsapp_message"
    description = (
        "Send a WhatsApp message to a specific phone number.  "
        "Use for appointment confirmations, follow-up messages, "
        "or proactive notifications — NOT for the main reply "
        "(the agent sends that automatically)."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "to": {
                "type": "string",
                "description": (
                    "Recipient phone number in E.164 format "
                    "(e.g. +919876543210)."
                ),
            },
            "message": {
                "type": "string",
                "description": "Text content of the message to send.",
            },
        },
        "required": ["to", "message"],
    }

    async def execute(self, to: str, message: str, **_: Any) -> dict:
        from app.integrations.whatsapp.client import WhatsAppClient

        async with WhatsAppClient() as wa:
            await wa.send_text(to=to, body=message)

        logger.info("WhatsAppTool: sent message to %s (%d chars)", to, len(message))
        return {
            "sent": True,
            "to": to,
            "message_preview": message[:100],
        }
