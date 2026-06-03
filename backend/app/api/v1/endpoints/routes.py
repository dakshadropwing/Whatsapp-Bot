"""
Endpoints routes — stub, implement with service layer.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

endpoints_bp = Blueprint("endpoints", __name__)

@endpoints_bp.get("/")
@jwt_required()
def list_endpoints():
    return jsonify({"endpoints": [], "message": "TODO: implement endpoints service"}), 200
