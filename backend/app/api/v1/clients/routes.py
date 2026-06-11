"""
Clients routes — CRUD for customer/client management.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

clients_bp = Blueprint("clients", __name__)


@clients_bp.get("/")
@jwt_required()
def list_clients():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    return jsonify({"data": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}), 200


@clients_bp.get("/<client_id>")
@jwt_required()
def get_client(client_id: str):
    return jsonify({"client": {"id": client_id}}), 200


@clients_bp.post("/")
@jwt_required()
def create_client():
    data = request.get_json(silent=True) or {}
    return jsonify({"id": "new", **data}), 201


@clients_bp.patch("/<client_id>")
@jwt_required()
def update_client(client_id: str):
    data = request.get_json(silent=True) or {}
    return jsonify({"id": client_id, "updated": True}), 200
