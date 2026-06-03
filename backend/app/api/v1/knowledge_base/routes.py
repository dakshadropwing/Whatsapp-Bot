"""
Knowledge Base routes — stub, implement with service layer.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

knowledge_base_bp = Blueprint("knowledge_base", __name__)

@knowledge_base_bp.get("/")
@jwt_required()
def list_knowledge_base():
    return jsonify({"knowledge_base": [], "message": "TODO: implement knowledge_base service"}), 200
