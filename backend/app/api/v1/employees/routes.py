"""
Employees routes — CRUD for team member management.
"""
from __future__ import annotations

import uuid
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required

from app.services.employee_service import EmployeeService

employees_bp = Blueprint("employees", __name__)


@employees_bp.get("/")
@jwt_required()
def list_employees():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    search = request.args.get("search")

    result = EmployeeService.list_employees(
        org_id=org_id,
        page=page,
        per_page=per_page,
        search=search
    )
    return jsonify(result), 200


@employees_bp.get("/<employee_id>")
@jwt_required()
def get_employee(employee_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    employee = EmployeeService.get_employee(employee_id)
    if not employee or str(employee.organization_id) != org_id:
        return jsonify({"error": "Employee not found"}), 404

    return jsonify({
        "employee": {
            "id": str(employee.id),
            "organization_id": str(employee.organization_id),
            "name": employee.name,
            "email": employee.email,
            "phone": employee.phone,
            "department": employee.department,
            "role": employee.role,
            "status": employee.status,
            "created_at": employee.created_at.isoformat() if employee.created_at else None,
            "updated_at": employee.updated_at.isoformat() if employee.updated_at else None,
        }
    }), 200


@employees_bp.post("/")
@jwt_required()
def create_employee():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400

    employee = EmployeeService.create_employee(org_id=org_id, **data)
    return jsonify({
        "id": str(employee.id),
        "name": employee.name,
        "email": employee.email,
        "role": employee.role,
    }), 201


@employees_bp.patch("/<employee_id>")
@jwt_required()
def update_employee(employee_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    employee = EmployeeService.get_employee(employee_id)
    if not employee or str(employee.organization_id) != org_id:
        return jsonify({"error": "Employee not found"}), 404

    data = request.get_json(silent=True) or {}
    updated_employee = EmployeeService.update_employee(employee_id, **data)
    if not updated_employee:
        return jsonify({"error": "Failed to update employee"}), 400

    return jsonify({"id": str(updated_employee.id), "updated": True}), 200


@employees_bp.delete("/<employee_id>")
@jwt_required()
def delete_employee(employee_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    employee = EmployeeService.get_employee(employee_id)
    if not employee or str(employee.organization_id) != org_id:
        return jsonify({"error": "Employee not found"}), 404

    success = EmployeeService.delete_employee(employee_id)
    return jsonify({"deleted": success}), 200
