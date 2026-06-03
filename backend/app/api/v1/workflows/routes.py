"""
Workflows routes — stub, implement with service layer.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

workflows_bp = Blueprint("workflows", __name__)

@workflows_bp.get("/")
@jwt_required()
def list_workflows():
    return jsonify({"workflows": [], "message": "TODO: implement workflows service"}), 200
