"""
Employees routes — CRUD for team member management.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

employees_bp = Blueprint("employees", __name__)


@employees_bp.get("/")
@jwt_required()
def list_employees():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    return jsonify({"data": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}), 200


@employees_bp.get("/<employee_id>")
@jwt_required()
def get_employee(employee_id: str):
    return jsonify({"employee": {"id": employee_id}}), 200


@employees_bp.post("/")
@jwt_required()
def create_employee():
    data = request.get_json(silent=True) or {}
    return jsonify({"id": "new", **data}), 201


@employees_bp.patch("/<employee_id>")
@jwt_required()
def update_employee(employee_id: str):
    data = request.get_json(silent=True) or {}
    return jsonify({"id": employee_id, "updated": True}), 200
