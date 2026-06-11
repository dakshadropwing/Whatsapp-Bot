"""
Users routes — CRUD for platform user management.
"""
from __future__ import annotations

import uuid
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required

from app.services.user_service import UserService

users_bp = Blueprint("users", __name__)


@users_bp.get("/")
@jwt_required()
def list_users():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    search = request.args.get("search")

    result = UserService.list_users(
        org_id=org_id,
        page=page,
        per_page=per_page,
        search=search
    )
    return jsonify(result), 200


@users_bp.get("/<user_id>")
@jwt_required()
def get_user(user_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    user = UserService.get_user(user_id)
    if not user or str(user.organization_id) != org_id:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "user": {
            "id": str(user.id),
            "organization_id": str(user.organization_id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "role_id": str(user.role_id) if user.role_id else None,
            "is_active": user.is_active,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
    }), 200


@users_bp.post("/")
@jwt_required()
def create_user():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    data = request.get_json(silent=True) or {}
    email = data.get("email")
    username = data.get("username")
    full_name = data.get("full_name")
    password = data.get("password")
    role_id = data.get("role_id")

    if not email or not username or not full_name or not password:
        return jsonify({"error": "email, username, full_name, and password are required"}), 400

    try:
        user = UserService.create_user(
            org_id=org_id,
            email=email,
            username=username,
            full_name=full_name,
            password=password,
            role_id=role_id
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
    }), 201


@users_bp.patch("/<user_id>")
@jwt_required()
def update_user(user_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    user = UserService.get_user(user_id)
    if not user or str(user.organization_id) != org_id:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}
    updated_user = UserService.update_user(user_id, **data)
    if not updated_user:
        return jsonify({"error": "Failed to update user"}), 400

    return jsonify({"id": str(updated_user.id), "updated": True}), 200


@users_bp.delete("/<user_id>")
@jwt_required()
def delete_user(user_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    user = UserService.get_user(user_id)
    if not user or str(user.organization_id) != org_id:
        return jsonify({"error": "User not found"}), 404

    deactivated = UserService.deactivate_user(user_id)
    if not deactivated:
        return jsonify({"error": "Failed to deactivate user"}), 400

    return jsonify({"deleted": True}), 200
