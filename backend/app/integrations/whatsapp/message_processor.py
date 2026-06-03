"""
Message Processor — orchestrates the full inbound message pipeline.

Pipeline:
    raw WA message
        → normalize
        → get/create conversation
        → retrieve context (memory)
        → select agent
        → execute tools (if needed)
        → generate AI response
        → send reply
        → persist logs
"""
from __future__ import annotations

import logging
from typing import Any

from app.ai.orchestrator.router import AgentRouter

logger = logging.getLogger(__name__)


class MessageProcessor:
    """
    Central pipeline for processing inbound WhatsApp messages.
    """

    def __init__(self) -> None:
        self.router = AgentRouter()

    async def process(
        self,
        message: dict,
        contact: dict,
        metadata: dict,
    ) -> None:
        """
        Full processing pipeline for a single inbound message.
        """
        try:
            normalized = self._normalize(message, contact, metadata)
            logger.info(
                "Processing inbound message",
                extra={
                    "from": normalized["from"],
                    "type": normalized["type"],
                    "wa_id": normalized["wa_id"],
                },
            )

            # Delegate to the supervisor agent router
            await self.router.route(normalized)

        except Exception as exc:
            logger.exception("MessageProcessor pipeline error", exc_info=exc)

    def _normalize(
        self,
        message: dict,
        contact: dict,
        metadata: dict,
    ) -> dict[str, Any]:
        """
        Normalize the raw WhatsApp payload into a standard internal format.
        """
        msg_type = message.get("type", "text")
        body = ""

        if msg_type == "text":
            body = message.get("text", {}).get("body", "")
        elif msg_type == "interactive":
            interactive = message.get("interactive", {})
            if interactive.get("type") == "button_reply":
                body = interactive["button_reply"]["title"]
            elif interactive.get("type") == "list_reply":
                body = interactive["list_reply"]["title"]
        elif msg_type in ("image", "video", "audio", "document", "sticker"):
            body = f"[{msg_type.upper()}]"

        return {
            "wa_message_id": message.get("id"),
            "from": message.get("from"),
            "wa_id": contact.get("wa_id", message.get("from")),
            "contact_name": contact.get("profile", {}).get("name"),
            "type": msg_type,
            "body": body,
            "timestamp": message.get("timestamp"),
            "phone_number_id": metadata.get("phone_number_id"),
            "raw": message,
        }
