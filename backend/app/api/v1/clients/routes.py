"""
Clients routes — CRUD for customer/client management.
"""
from __future__ import annotations

import uuid
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required

from app.services.client_service import ClientService

clients_bp = Blueprint("clients", __name__)


@clients_bp.get("/")
@jwt_required()
def list_clients():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    search = request.args.get("search")

    result = ClientService.list_clients(
        org_id=org_id,
        page=page,
        per_page=per_page,
        search=search
    )
    return jsonify(result), 200


@clients_bp.get("/<client_id>")
@jwt_required()
def get_client(client_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    client = ClientService.get_client(client_id)
    if not client or str(client.organization_id) != org_id:
        return jsonify({"error": "Client not found"}), 404

    return jsonify({
        "client": {
            "id": str(client.id),
            "organization_id": str(client.organization_id),
            "name": client.name,
            "email": client.email,
            "phone": client.phone,
            "company": client.company,
            "tags": client.tags or [],
            "created_at": client.created_at.isoformat() if client.created_at else None,
            "updated_at": client.updated_at.isoformat() if client.updated_at else None,
        }
    }), 200


@clients_bp.post("/")
@jwt_required()
def create_client():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name:
        return jsonify({"error": "name is required"}), 400

    client = ClientService.create_client(org_id=org_id, **data)
    return jsonify({
        "id": str(client.id),
        "name": client.name,
        "email": client.email,
        "phone": client.phone,
    }), 201


@clients_bp.patch("/<client_id>")
@jwt_required()
def update_client(client_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    client = ClientService.get_client(client_id)
    if not client or str(client.organization_id) != org_id:
        return jsonify({"error": "Client not found"}), 404

    data = request.get_json(silent=True) or {}
    updated_client = ClientService.update_client(client_id, **data)
    if not updated_client:
        return jsonify({"error": "Failed to update client"}), 400

    return jsonify({"id": str(updated_client.id), "updated": True}), 200


@clients_bp.delete("/<client_id>")
@jwt_required()
def delete_client(client_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    client = ClientService.get_client(client_id)
    if not client or str(client.organization_id) != org_id:
        return jsonify({"error": "Client not found"}), 404

    success = ClientService.delete_client(client_id)
    return jsonify({"deleted": success}), 200
