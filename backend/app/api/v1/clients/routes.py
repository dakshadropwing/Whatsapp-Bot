"""
Clients routes — stub, implement with service layer.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

clients_bp = Blueprint("clients", __name__)

@clients_bp.get("/")
@jwt_required()
def list_clients():
    return jsonify({"clients": [], "message": "TODO: implement clients service"}), 200
