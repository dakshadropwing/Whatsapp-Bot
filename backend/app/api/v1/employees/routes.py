"""
Employees routes — stub, implement with service layer.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

employees_bp = Blueprint("employees", __name__)

@employees_bp.get("/")
@jwt_required()
def list_employees():
    return jsonify({"employees": [], "message": "TODO: implement employees service"}), 200
