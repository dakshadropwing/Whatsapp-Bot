"""
WhatsApp Ingestion Service — webhook signature checks & gateway normalisation.

Validates that inbound webhooks genuinely originate from Meta, then
normalises the raw payload into a flat dict consumed by the AgentRouter.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any, Optional

from flask import abort

from app.core.config.settings import get_settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Handles Meta webhook verification and message normalisation."""

    # ── Signature Verification ────────────────────────────────

    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str) -> bool:
        """
        Ensure the webhook request genuinely comes from Meta.

        Meta signs the raw request body with the app secret using HMAC-SHA256
        and sends it in the ``X-Hub-Signature-256`` header as ``sha256=<hex>``.

        Args:
            payload: Raw request body bytes.
            signature: Value of the ``X-Hub-Signature-256`` header.

        Returns:
            True if the computed digest matches the provided signature.
        """
        settings = get_settings()
        app_secret = settings.APP_SECRET_KEY

        expected = hmac.new(
            app_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(f"sha256={expected}", signature)

    @classmethod
    def validate_or_abort(cls, payload: bytes, signature: Optional[str]) -> None:
        """Validate the signature or abort with 403."""
        if not signature or not cls.verify_webhook_signature(payload, signature):
            logger.warning("Invalid or missing webhook signature")
            abort(403, description="Invalid webhook signature")

    # ── Webhook Verify Token (GET challenge) ──────────────────

    @staticmethod
    def verify_token(token: str) -> bool:
        """
        Check the verify token sent during Meta webhook registration.

        Meta sends a GET request with ``hub.verify_token`` during setup.
        """
        settings = get_settings()
        return hmac.compare_digest(token, settings.WHATSAPP_WEBHOOK_VERIFY_TOKEN)

    # ── Message Normalisation ─────────────────────────────────

    @staticmethod
    def normalize_inbound(payload: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract and normalise inbound messages from Meta's webhook payload.

        Meta's payload structure:
            { "entry": [{ "changes": [{ "value": { "messages": [...] } }] }] }

        Returns:
            A list of normalised message dicts, each containing:
            ``from``, ``body``, ``message_id``, ``timestamp``, ``type``, ``raw``.
        """
        messages: list[dict[str, Any]] = []

        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                metadata = value.get("metadata", {})

                for msg in value.get("messages", []):
                    msg_type = msg.get("type", "text")
                    body = ""

                    if msg_type == "text":
                        body = msg.get("text", {}).get("body", "")
                    elif msg_type == "image":
                        body = msg.get("image", {}).get("caption", "")
                    elif msg_type == "audio":
                        body = "[audio message]"
                    elif msg_type == "video":
                        body = msg.get("video", {}).get("caption", "")
                    elif msg_type == "location":
                        loc = msg.get("location", {})
                        body = f"[location: {loc.get('latitude')},{loc.get('longitude')}]"
                    elif msg_type == "interactive":
                        interactive = msg.get("interactive", {})
                        body = interactive.get("button_reply", {}).get("title", "")
                    elif msg_type == "button":
                        body = msg.get("button", {}).get("text", "")

                    # Extract contact name from the "contacts" array if present
                    contacts = value.get("contacts", [])
                    contact_name = ""
                    if contacts:
                        profile = contacts[0].get("profile", {})
                        contact_name = profile.get("name", "")

                    normalized = {
                        "from": msg.get("from", ""),
                        "body": body,
                        "message_id": msg.get("id", ""),
                        "timestamp": msg.get("timestamp", ""),
                        "type": msg_type,
                        "contact_name": contact_name,
                        "phone_number_id": metadata.get("phone_number_id", ""),
                        "raw": msg,
                    }
                    messages.append(normalized)

        return messages
