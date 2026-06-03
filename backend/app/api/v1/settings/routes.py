"""
Settings routes — stub, implement with service layer.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

settings_bp = Blueprint("settings", __name__)

@settings_bp.get("/")
@jwt_required()
def list_settings():
    return jsonify({"settings": [], "message": "TODO: implement settings service"}), 200
