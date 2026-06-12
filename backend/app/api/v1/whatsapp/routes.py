"""
WhatsApp routes — webhook handling + management (accounts, send).
"""
from __future__ import annotations

import asyncio
import logging
import uuid

from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.whatsapp_account import WhatsAppAccount
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

    from flask import current_app
    if current_app.config.get("TESTING"):
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(_handler.dispatch(payload))
        except Exception as exc:
            logger.exception("Webhook dispatch failed", exc_info=exc)
        finally:
            loop.close()
    else:
        from app.tasks.queue_tasks import process_inbound_webhook_task
        try:
            process_inbound_webhook_task.delay(payload)
        except Exception as exc:
            logger.exception("Failed to enqueue webhook processing Celery task", exc_info=exc)

    return jsonify({"status": "ok"}), 200


# ── Management (auth required) ───────────────────────────────────

@whatsapp_bp.get("/accounts")
@jwt_required()
def list_accounts():
    """List connected WhatsApp Business accounts."""
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    accounts = db.session.execute(
        db.select(WhatsAppAccount).where(WhatsAppAccount.organization_id == uuid.UUID(org_id))
    ).scalars().all()

    return jsonify({
        "accounts": [
            {
                "id": str(acc.id),
                "phone_number_id": acc.phone_number_id,
                "waba_id": acc.waba_id,
                "is_active": acc.is_active,
            }
            for acc in accounts
        ]
    }), 200


@whatsapp_bp.post("/send")
@jwt_required()
def send_message():
    """Send a text message via WhatsApp."""
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    data = request.get_json(silent=True) or {}
    phone = data.get("phone")
    message = data.get("message")
    if not phone or not message:
        return jsonify({"error": "phone and message are required"}), 400

    from app.integrations.whatsapp.client import WhatsAppClient

    async def _send():
        async with WhatsAppClient() as client:
            return await client.send_text(phone, message)

    try:
        res = asyncio.run(_send())
        wa_msg_id = "wamid.stub"
        if res and "messages" in res and res["messages"]:
            wa_msg_id = res["messages"][0].get("id", "wamid.stub")
        return jsonify({"sent": True, "message_id": wa_msg_id}), 200
    except Exception as exc:
        logger.exception("Failed to send text message")
        return jsonify({"error": str(exc)}), 500


@whatsapp_bp.post("/send-template")
@jwt_required()
def send_template():
    """Send a template message via WhatsApp."""
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    data = request.get_json(silent=True) or {}
    phone = data.get("phone")
    template_name = data.get("template_name")
    language = data.get("language", "en_US")
    parameters = data.get("parameters", [])

    if not phone or not template_name:
        return jsonify({"error": "phone and template_name are required"}), 400

    from app.integrations.whatsapp.client import WhatsAppClient

    async def _send():
        components = None
        if parameters:
            components = [{"type": "body", "parameters": parameters}]
        async with WhatsAppClient() as client:
            return await client.send_template(
                to=phone,
                template_name=template_name,
                language_code=language,
                components=components,
            )

    try:
        res = asyncio.run(_send())
        wa_msg_id = "wamid.stub"
        if res and "messages" in res and res["messages"]:
            wa_msg_id = res["messages"][0].get("id", "wamid.stub")
        return jsonify({"sent": True, "message_id": wa_msg_id}), 200
    except Exception as exc:
        logger.exception("Failed to send template message")
        return jsonify({"error": str(exc)}), 500
