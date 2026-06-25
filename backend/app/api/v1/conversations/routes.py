"""
Conversations routes — CRUD + real-time conversation management.
"""
from __future__ import annotations

import uuid
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required

from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService

conversations_bp = Blueprint("conversations", __name__)


@conversations_bp.get("/")
@jwt_required()
def list_conversations():
    """
    GET /api/v1/conversations
    Query params: status, page, per_page, search
    """
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    status = request.args.get("status")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    search = request.args.get("search")

    result = ConversationService.list_conversations(
        org_id=org_id,
        status=status,
        page=page,
        per_page=per_page,
        search=search
    )
    return jsonify(result), 200


@conversations_bp.get("/<conversation_id>")
@jwt_required()
def get_conversation(conversation_id: str):
    """GET /api/v1/conversations/{id} — fetch a single conversation with messages."""
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    conv = ConversationService.get_conversation(conversation_id)
    if not conv or str(conv.organization_id) != org_id:
        return jsonify({"error": "Conversation not found"}), 404

    return jsonify({
        "conversation": {
            "id": str(conv.id),
            "organization_id": str(conv.organization_id),
            "contact_phone": conv.contact_phone,
            "contact_name": conv.contact_name,
            "contact_wa_id": conv.contact_wa_id,
            "status": conv.status.value if conv.status else None,
            "channel": conv.channel.value if conv.channel else None,
            "assigned_agent_id": str(conv.assigned_agent_id) if conv.assigned_agent_id else None,
            "assigned_user_id": str(conv.assigned_user_id) if conv.assigned_user_id else None,
            "priority": conv.priority,
            "message_count": conv.message_count,
            "last_message_at": conv.last_message_at,
            "tags": conv.tags or [],
            "created_at": conv.created_at.isoformat() if conv.created_at else None,
            "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
        }
    }), 200


@conversations_bp.patch("/<conversation_id>")
@jwt_required()
def update_conversation(conversation_id: str):
    """PATCH /api/v1/conversations/{id} — update assignment or fields."""
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    conv = ConversationService.get_conversation(conversation_id)
    if not conv or str(conv.organization_id) != org_id:
        return jsonify({"error": "Conversation not found"}), 404

    data = request.get_json(silent=True) or {}
    
    # Handle assignment side-effects if fields are in payload
    has_assignment = "assigned_user_id" in data or "assigned_agent_id" in data
    if has_assignment:
        assigned_user_id = data.pop("assigned_user_id", None)
        assigned_agent_id = data.pop("assigned_agent_id", None)
        
        if assigned_user_id or assigned_agent_id:
            updated_conv = ConversationService.assign_conversation(
                conversation_id,
                assigned_user_id=assigned_user_id or None,
                assigned_agent_id=assigned_agent_id or None
            )
        else:
            # Unassignment case: clear fields directly
            updated_conv = ConversationService.update_conversation(
                conversation_id,
                assigned_user_id=None,
                assigned_agent_id=None
            )
            
        if not updated_conv:
            return jsonify({"error": "Failed to assign conversation"}), 400
            
        if data:
            updated_conv = ConversationService.update_conversation(conversation_id, **data)
    else:
        updated_conv = ConversationService.update_conversation(conversation_id, **data)

    if not updated_conv:
        return jsonify({"error": "Failed to update conversation"}), 400

    return jsonify({"id": str(updated_conv.id), "updated": True}), 200


@conversations_bp.post("/<conversation_id>/assign")
@jwt_required()
def assign_conversation(conversation_id: str):
    """Assign a conversation to a human agent or AI agent."""
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    conv = ConversationService.get_conversation(conversation_id)
    if not conv or str(conv.organization_id) != org_id:
        return jsonify({"error": "Conversation not found"}), 404

    data = request.get_json(silent=True) or {}
    assigned_user_id = data.get("assigned_user_id")
    assigned_agent_id = data.get("assigned_agent_id")

    updated_conv = ConversationService.assign_conversation(
        conversation_id,
        assigned_user_id=assigned_user_id,
        assigned_agent_id=assigned_agent_id
    )
    if not updated_conv:
        return jsonify({"error": "Failed to assign conversation"}), 400

    return jsonify({"assigned": True}), 200


@conversations_bp.post("/<conversation_id>/resolve")
@jwt_required()
def resolve_conversation(conversation_id: str):
    """Mark a conversation as resolved."""
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    conv = ConversationService.get_conversation(conversation_id)
    if not conv or str(conv.organization_id) != org_id:
        return jsonify({"error": "Conversation not found"}), 404

    updated_conv = ConversationService.resolve_conversation(conversation_id)
    if not updated_conv:
        return jsonify({"error": "Failed to resolve conversation"}), 400

    return jsonify({"resolved": True}), 200


@conversations_bp.post("/<conversation_id>/escalate")
@jwt_required()
def escalate_conversation(conversation_id: str):
    """Escalate to human support."""
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    conv = ConversationService.get_conversation(conversation_id)
    if not conv or str(conv.organization_id) != org_id:
        return jsonify({"error": "Conversation not found"}), 404

    # Use the escalate function from human handoff, which creates ticket and alerts
    from app.integrations.whatsapp.human_handoff import escalate_to_human
    res = escalate_to_human(conversation_id, reason="Manual escalation via API")
    if not res:
        return jsonify({"error": "Failed to escalate conversation"}), 400

    return jsonify({"escalated": True}), 200


@conversations_bp.get("/<conversation_id>/messages")
@jwt_required()
def get_messages(conversation_id: str):
    """Paginated message history for a conversation."""
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    conv = ConversationService.get_conversation(conversation_id)
    if not conv or str(conv.organization_id) != org_id:
        return jsonify({"error": "Conversation not found"}), 404

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    direction = request.args.get("direction")

    result = MessageService.list_messages(
        conversation_id=conversation_id,
        page=page,
        per_page=per_page,
        direction=direction
    )
    return jsonify(result), 200
