"""
Webhook handler — entry point for all incoming WhatsApp events.
Validates signature, parses payload, and dispatches to the message processor.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any

from flask import Request

from app.core.config.settings import get_settings
from app.integrations.whatsapp.message_processor import MessageProcessor

logger = logging.getLogger(__name__)


class WebhookHandler:
    """
    Handles WhatsApp Cloud API webhook events.

    Flow:
        POST /webhooks/whatsapp
            → verify_signature()
            → parse_event()
            → dispatch()
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.processor = MessageProcessor()

    # ── Signature Verification ────────────────────────────────

    def verify_signature(self, request: Request) -> bool:
        """
        Validate the X-Hub-Signature-256 header using HMAC-SHA256.
        Returns False if the signature is missing or invalid.
        """
        signature_header = request.headers.get("X-Hub-Signature-256", "")
        if not signature_header.startswith("sha256="):
            logger.warning("Webhook: missing or malformed signature header")
            return False

        expected_sig = signature_header[len("sha256="):]
        body = request.get_data()
        computed = hmac.new(
            self.settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN.encode("utf-8"),
            body,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(expected_sig, computed)

    # ── Challenge Verification (GET) ──────────────────────────

    def handle_verification(self, args: dict) -> tuple[str, int]:
        """
        Respond to Meta's webhook verification challenge.
        """
        mode = args.get("hub.mode")
        token = args.get("hub.verify_token")
        challenge = args.get("hub.challenge")

        if mode == "subscribe" and token == self.settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN:
            logger.info("Webhook verification successful")
            return challenge, 200

        logger.warning("Webhook verification failed")
        return "Forbidden", 403

    # ── Event Dispatch ────────────────────────────────────────

    async def dispatch(self, payload: dict) -> None:
        """
        Parse the webhook payload and route to the appropriate handler.
        """
        try:
            entry_list = payload.get("entry", [])
            for entry in entry_list:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    field = change.get("field", "")

                    if field == "messages":
                        await self._handle_messages(value)
                    elif field == "statuses":
                        await self._handle_statuses(value)
        except Exception as exc:
            logger.exception("Webhook dispatch error", exc_info=exc)

    async def _handle_messages(self, value: dict) -> None:
        """Dispatch inbound messages to the processor."""
        for message in value.get("messages", []):
            contacts = value.get("contacts", [{}])
            contact = contacts[0] if contacts else {}
            metadata = value.get("metadata", {})

            await self.processor.process(
                message=message,
                contact=contact,
                metadata=metadata,
            )

    async def _handle_statuses(self, value: dict) -> None:
        """Handle delivery/read status updates for outbound messages."""
        from app.extensions import db
        from app.models.message import Message, MessageStatus
        from sqlalchemy import select

        for status in value.get("statuses", []):
            wa_message_id = status.get("id")
            new_status = status.get("status")  # sent | delivered | read | failed
            logger.info(
                "Message status update",
                extra={"wa_message_id": wa_message_id, "status": new_status},
            )
            if not wa_message_id:
                continue

            try:
                status_map = {
                    "sent": MessageStatus.SENT,
                    "delivered": MessageStatus.DELIVERED,
                    "read": MessageStatus.READ,
                    "failed": MessageStatus.FAILED,
                }
                status_enum = status_map.get(new_status)
                if status_enum:
                    msg = db.session.execute(
                        select(Message).where(Message.wa_message_id == wa_message_id)
                    ).scalar_one_or_none()
                    if msg:
                        msg.status = status_enum
                        db.session.commit()
                        logger.info("Updated message %s status to %s", msg.id, status_enum)
            except Exception as exc:
                logger.exception("Failed to update message status for wa_message_id %s", wa_message_id)
                db.session.rollback()
