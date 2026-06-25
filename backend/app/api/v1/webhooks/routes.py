"""
Webhooks routes — receiver for Meta/WhatsApp inbound webhooks.

Handles both:
  • GET  /api/v1/webhooks/whatsapp — Meta verify-token challenge
  • POST /api/v1/webhooks/whatsapp — Inbound message / status updates
"""
from __future__ import annotations

import logging

from flask import Blueprint, jsonify, request

from app.services.whatsapp_service import WhatsAppService
from app.tasks.queue_tasks import process_inbound_message_task

logger = logging.getLogger(__name__)

webhooks_bp = Blueprint("webhooks", __name__)


# ── GET: Meta Webhook Verification ─────────────────────────────
@webhooks_bp.get("/whatsapp")
def verify_webhook():
    """
    Meta sends a GET request during webhook registration with:
      - hub.mode      → "subscribe"
      - hub.verify_token → the token we configured
      - hub.challenge → a random string we must echo back
    """
    mode = request.args.get("hub.mode", "")
    token = request.args.get("hub.verify_token", "")
    challenge = request.args.get("hub.challenge", "")

    if mode == "subscribe" and WhatsAppService.verify_token(token):
        logger.info("WhatsApp webhook verified successfully")
        return challenge, 200

    logger.warning("Webhook verification failed: mode=%s token=%s", mode, token)
    return jsonify({"error": "Verification failed"}), 403


# ── POST: Inbound Messages & Status Updates ────────────────────
@webhooks_bp.post("/whatsapp")
def receive_webhook():
    """
    Receive an inbound webhook from Meta.

    1. Validates the HMAC-SHA256 signature.
    2. Normalises the message payload.
    3. Enqueues each message for async processing by the AgentRouter.
    4. Returns 200 immediately so Meta does not retry.
    """
    # Step 1: Verify signature
    signature = request.headers.get("X-Hub-Signature-256")
    WhatsAppService.validate_or_abort(request.get_data(), signature)

    # Step 2: Parse payload
    payload = request.get_json(silent=True) or {}

    # Step 3: Normalize and enqueue
    messages = WhatsAppService.normalize_inbound(payload)
    for msg in messages:
        try:
            process_inbound_message_task.delay(msg)
            logger.info(
                "Enqueued message from %s (id=%s)",
                msg.get("from"),
                msg.get("message_id"),
            )
        except Exception:
            logger.exception("Failed to enqueue message %s", msg.get("message_id"))

    # Step 4: Always return 200 to Meta
    return jsonify({"status": "ok", "processed": len(messages)}), 200


# ── Health Check ────────────────────────────────────────────────
@webhooks_bp.get("/")
def health():
    return jsonify({"status": "active"}), 200
