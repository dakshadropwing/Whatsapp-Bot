"""
Auth routes — login, refresh, logout, register, profile.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)

from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    """
    POST /api/v1/auth/login
    Body: { "email": str, "password": str }
    Returns: { "access_token": str, "refresh_token": str, "user": {...} }
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    result = AuthService.authenticate_user(email, password)
    if not result:
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify(result), 200


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """Refresh the access token using a valid refresh token."""
    identity = get_jwt_identity()
    claims = get_jwt()
    # Preserve org_id and role in the new access token
    additional_claims = {
        "org_id": claims.get("org_id", ""),
        "role": claims.get("role", ""),
    }
    access_token = create_access_token(
        identity=identity, additional_claims=additional_claims
    )
    return jsonify({"access_token": access_token}), 200


@auth_bp.post("/logout")
@jwt_required()
def logout():
    """Invalidate the current token (add to blocklist)."""
    # TODO: add jti to Redis blocklist
    return jsonify({"message": "Logged out"}), 200


@auth_bp.get("/me")
@jwt_required()
def me():
    """Return the current authenticated user's profile."""
    from app.repositories.user_repo import UserRepository

    identity = get_jwt_identity()
    user_repo = UserRepository()
    user = user_repo.find_active_by_id(identity)

    if not user:
        return jsonify({"error": "User not found or inactive"}), 404

    return jsonify({
        "user": {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "organization_id": str(user.organization_id),
            "org_id": str(user.organization_id),
            "role": str(user.role_id or "member"),
            "role_id": str(user.role_id) if user.role_id else None,
            "last_login_at": user.last_login_at,
            "preferences": user.preferences,
        }
    }), 200
