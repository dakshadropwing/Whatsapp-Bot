"""
Audit routes — stub, implement with service layer.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

audit_bp = Blueprint("audit", __name__)

@audit_bp.get("/")
@jwt_required()
def list_audit():
    return jsonify({"audit": [], "message": "TODO: implement audit service"}), 200
