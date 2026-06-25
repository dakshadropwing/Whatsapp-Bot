"""
Messages routes — standalone message queries.
"""
from __future__ import annotations

import uuid
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required
from sqlalchemy import select, func

from app.extensions import db
from app.models.message import Message

messages_bp = Blueprint("messages", __name__)


@messages_bp.get("/")
@jwt_required()
def list_messages():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))

    query = select(Message).where(Message.organization_id == uuid.UUID(org_id))
    
    total = db.session.execute(
        select(func.count()).select_from(query.subquery())
    ).scalar() or 0

    messages = (
        db.session.execute(
            query.order_by(Message.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        .scalars()
        .all()
    )

    return jsonify({
        "data": [
            {
                "id": str(m.id),
                "organization_id": str(m.organization_id),
                "conversation_id": str(m.conversation_id),
                "wa_message_id": m.wa_message_id,
                "direction": m.direction.value,
                "message_type": m.message_type.value,
                "status": m.status.value,
                "body": m.body,
                "media_url": m.media_url,
                "ai_generated": m.ai_generated,
                "tokens_used": m.tokens_used,
                "processing_time_ms": m.processing_time_ms,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }), 200


@messages_bp.get("/<message_id>")
@jwt_required()
def get_message(message_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    msg = db.session.get(Message, uuid.UUID(message_id))
    if not msg or str(msg.organization_id) != org_id:
        return jsonify({"error": "Message not found"}), 404

    return jsonify({
        "message": {
            "id": str(msg.id),
            "organization_id": str(msg.organization_id),
            "conversation_id": str(msg.conversation_id),
            "wa_message_id": msg.wa_message_id,
            "direction": msg.direction.value,
            "message_type": msg.message_type.value,
            "status": msg.status.value,
            "body": msg.body,
            "media_url": msg.media_url,
            "ai_generated": msg.ai_generated,
            "tokens_used": msg.tokens_used,
            "processing_time_ms": msg.processing_time_ms,
            "created_at": msg.created_at.isoformat() if msg.created_at else None,
        }
    }), 200
