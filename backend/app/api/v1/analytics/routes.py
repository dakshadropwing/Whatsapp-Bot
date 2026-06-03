"""
Analytics routes — stub, implement with service layer.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.get("/")
@jwt_required()
def list_analytics():
    return jsonify({"analytics": [], "message": "TODO: implement analytics service"}), 200
