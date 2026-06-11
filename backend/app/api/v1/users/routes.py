"""
Users routes — CRUD for platform user management.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

users_bp = Blueprint("users", __name__)


@users_bp.get("/")
@jwt_required()
def list_users():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    return jsonify({"data": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}), 200


@users_bp.get("/<user_id>")
@jwt_required()
def get_user(user_id: str):
    return jsonify({"user": {"id": user_id}}), 200


@users_bp.post("/")
@jwt_required()
def create_user():
    data = request.get_json(silent=True) or {}
    return jsonify({"id": "new", **data}), 201


@users_bp.patch("/<user_id>")
@jwt_required()
def update_user(user_id: str):
    data = request.get_json(silent=True) or {}
    return jsonify({"id": user_id, "updated": True}), 200


@users_bp.delete("/<user_id>")
@jwt_required()
def delete_user(user_id: str):
    return jsonify({"deleted": True}), 200
