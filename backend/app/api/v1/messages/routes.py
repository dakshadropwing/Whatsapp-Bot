"""
Messages routes — stub, implement with service layer.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

messages_bp = Blueprint("messages", __name__)

@messages_bp.get("/")
@jwt_required()
def list_messages():
    return jsonify({"messages": [], "message": "TODO: implement messages service"}), 200
