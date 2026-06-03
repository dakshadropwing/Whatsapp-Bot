"""
Prompts routes — stub, implement with service layer.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

prompts_bp = Blueprint("prompts", __name__)

@prompts_bp.get("/")
@jwt_required()
def list_prompts():
    return jsonify({"prompts": [], "message": "TODO: implement prompts service"}), 200
