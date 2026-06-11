"""
Messages routes — standalone message queries.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

messages_bp = Blueprint("messages", __name__)


@messages_bp.get("/")
@jwt_required()
def list_messages():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    return jsonify({"data": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}), 200


@messages_bp.get("/<message_id>")
@jwt_required()
def get_message(message_id: str):
    return jsonify({"message": {"id": message_id}}), 200
