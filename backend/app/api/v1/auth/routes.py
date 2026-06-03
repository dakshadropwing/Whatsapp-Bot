"""
Auth routes — login, refresh, logout, register.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

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

    # TODO: delegate to AuthService.login(email, password)
    # For now return a placeholder
    return jsonify({"message": "Login endpoint — implement AuthService"}), 501


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """Refresh the access token using a valid refresh token."""
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
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
    identity = get_jwt_identity()
    # TODO: fetch user from UserService
    return jsonify({"user_id": identity}), 200
