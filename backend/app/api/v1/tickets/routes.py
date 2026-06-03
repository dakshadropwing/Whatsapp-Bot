"""
Tickets routes — stub, implement with service layer.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

tickets_bp = Blueprint("tickets", __name__)

@tickets_bp.get("/")
@jwt_required()
def list_tickets():
    return jsonify({"tickets": [], "message": "TODO: implement tickets service"}), 200
