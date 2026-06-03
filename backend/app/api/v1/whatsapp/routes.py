"""
WhatsApp webhook routes — handles verification and inbound events.
"""
from __future__ import annotations

import asyncio
import logging

from flask import Blueprint, jsonify, request

from app.integrations.whatsapp.webhook_handler import WebhookHandler

logger = logging.getLogger(__name__)
whatsapp_bp = Blueprint("whatsapp", __name__)
_handler = WebhookHandler()


@whatsapp_bp.get("/webhook")
def verify_webhook():
    """Meta webhook challenge verification (GET)."""
    challenge, status = _handler.handle_verification(request.args)
    return challenge, status


@whatsapp_bp.post("/webhook")
def receive_webhook():
    """
    Receive inbound WhatsApp events (POST).

    1. Validate HMAC signature.
    2. Immediately return 200 OK (Meta requires < 5s response).
    3. Dispatch to async processor.
    """
    if not _handler.verify_signature(request):
        logger.warning("Invalid webhook signature — rejecting request")
        return jsonify({"error": "Invalid signature"}), 401

    payload = request.get_json(force=True, silent=True) or {}

    # Fire and forget — process asynchronously
    # In production this would push to Celery; here we run in event loop
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(_handler.dispatch(payload))
    except Exception as exc:
        logger.exception("Webhook dispatch failed", exc_info=exc)
    finally:
        loop.close()

    return jsonify({"status": "ok"}), 200
