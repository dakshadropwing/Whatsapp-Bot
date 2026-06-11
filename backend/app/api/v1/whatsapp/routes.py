"""
WhatsApp routes — webhook handling + management (accounts, send).
"""
from __future__ import annotations

import asyncio
import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.integrations.whatsapp.webhook_handler import WebhookHandler

logger = logging.getLogger(__name__)
whatsapp_bp = Blueprint("whatsapp", __name__)
_handler = WebhookHandler()


# ── Webhook (public, no auth) ────────────────────────────────────

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


# ── Management (auth required) ───────────────────────────────────

@whatsapp_bp.get("/accounts")
@jwt_required()
def list_accounts():
    """List connected WhatsApp Business accounts."""
    # TODO: WhatsAppAccountService.list(org_id)
    return jsonify({"accounts": []}), 200


@whatsapp_bp.post("/send")
@jwt_required()
def send_message():
    """Send a text message via WhatsApp."""
    data = request.get_json(silent=True) or {}
    phone = data.get("phone")
    message = data.get("message")
    if not phone or not message:
        return jsonify({"error": "phone and message are required"}), 400
    # TODO: WhatsAppSendService.send_text(org_id, phone, message)
    return jsonify({"sent": True, "message_id": "wamid.stub"}), 200


@whatsapp_bp.post("/send-template")
@jwt_required()
def send_template():
    """Send a template message via WhatsApp."""
    data = request.get_json(silent=True) or {}
    phone = data.get("phone")
    template_name = data.get("template_name")
    if not phone or not template_name:
        return jsonify({"error": "phone and template_name are required"}), 400
    # TODO: WhatsAppSendService.send_template(org_id, phone, template_name, language, parameters)
    return jsonify({"sent": True, "message_id": "wamid.stub"}), 200
