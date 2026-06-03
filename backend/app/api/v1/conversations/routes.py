"""
Conversations routes — CRUD + real-time conversation management.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

conversations_bp = Blueprint("conversations", __name__)


@conversations_bp.get("/")
@jwt_required()
def list_conversations():
    """
    GET /api/v1/conversations
    Query params: status, page, per_page, search
    """
    status = request.args.get("status")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    # TODO: ConversationService.list(org_id, status, page, per_page)
    return jsonify({"conversations": [], "page": page, "per_page": per_page}), 200


@conversations_bp.get("/<conversation_id>")
@jwt_required()
def get_conversation(conversation_id: str):
    """GET /api/v1/conversations/{id} — fetch a single conversation with messages."""
    # TODO: ConversationService.get(conversation_id)
    return jsonify({"id": conversation_id}), 200


@conversations_bp.post("/<conversation_id>/assign")
@jwt_required()
def assign_conversation(conversation_id: str):
    """Assign a conversation to a human agent or AI agent."""
    data = request.get_json(silent=True) or {}
    # TODO: ConversationService.assign(conversation_id, data)
    return jsonify({"assigned": True}), 200


@conversations_bp.post("/<conversation_id>/resolve")
@jwt_required()
def resolve_conversation(conversation_id: str):
    """Mark a conversation as resolved."""
    # TODO: ConversationService.resolve(conversation_id)
    return jsonify({"resolved": True}), 200


@conversations_bp.post("/<conversation_id>/escalate")
@jwt_required()
def escalate_conversation(conversation_id: str):
    """Escalate to human support."""
    data = request.get_json(silent=True) or {}
    return jsonify({"escalated": True}), 200


@conversations_bp.get("/<conversation_id>/messages")
@jwt_required()
def get_messages(conversation_id: str):
    """Paginated message history for a conversation."""
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    # TODO: MessageService.list(conversation_id, page, per_page)
    return jsonify({"messages": [], "page": page}), 200
