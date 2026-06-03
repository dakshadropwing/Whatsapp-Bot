"""
Users routes — stub, implement with service layer.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

users_bp = Blueprint("users", __name__)

@users_bp.get("/")
@jwt_required()
def list_users():
    return jsonify({"users": [], "message": "TODO: implement users service"}), 200
