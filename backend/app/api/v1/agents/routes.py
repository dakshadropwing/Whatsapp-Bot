"""
Agents routes — stub, implement with service layer.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

agents_bp = Blueprint("agents", __name__)

@agents_bp.get("/")
@jwt_required()
def list_agents():
    return jsonify({"agents": [], "message": "TODO: implement agents service"}), 200
