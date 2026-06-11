"""
Endpoints routes — CRUD for external API endpoint configs.
"""
from __future__ import annotations

import uuid
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required
from sqlalchemy import select, func

from app.extensions import db
from app.models.endpoint_config import EndpointConfig
from app.services.endpoint_service import EndpointService

endpoints_bp = Blueprint("endpoints", __name__)


@endpoints_bp.get("/")
@jwt_required()
def list_endpoints():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))

    query = select(EndpointConfig).where(EndpointConfig.organization_id == uuid.UUID(org_id))

    total = db.session.execute(
        select(func.count()).select_from(query.subquery())
    ).scalar() or 0

    endpoints = (
        db.session.execute(
            query.order_by(EndpointConfig.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        .scalars()
        .all()
    )

    return jsonify({
        "data": [
            {
                "id": str(e.id),
                "organization_id": str(e.organization_id),
                "name": e.name,
                "description": e.description,
                "url": e.url,
                "method": e.method,
                "headers": e.headers,
                "is_active": e.is_active,
                "created_at": e.created_at.isoformat() if e.created_at else None,
                "updated_at": e.updated_at.isoformat() if e.updated_at else None,
            }
            for e in endpoints
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }), 200


@endpoints_bp.get("/<endpoint_id>")
@jwt_required()
def get_endpoint(endpoint_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    endpoint = db.session.get(EndpointConfig, uuid.UUID(endpoint_id))
    if not endpoint or str(endpoint.organization_id) != org_id:
        return jsonify({"error": "Endpoint not found"}), 404

    return jsonify({
        "endpoint": {
            "id": str(endpoint.id),
            "organization_id": str(endpoint.organization_id),
            "name": endpoint.name,
            "description": endpoint.description,
            "url": endpoint.url,
            "method": endpoint.method,
            "headers": endpoint.headers,
            "is_active": endpoint.is_active,
            "created_at": endpoint.created_at.isoformat() if endpoint.created_at else None,
            "updated_at": endpoint.updated_at.isoformat() if endpoint.updated_at else None,
        }
    }), 200


@endpoints_bp.post("/")
@jwt_required()
def create_endpoint():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    url = data.get("url")

    if not name or not url:
        return jsonify({"error": "name and url are required"}), 400

    endpoint = EndpointConfig(
        organization_id=uuid.UUID(org_id),
        name=name,
        description=data.get("description"),
        url=url,
        method=data.get("method", "POST").upper(),
        headers=data.get("headers", {}),
        is_active=data.get("is_active", True)
    )
    db.session.add(endpoint)
    db.session.commit()

    return jsonify({
        "id": str(endpoint.id),
        "name": endpoint.name,
        "url": endpoint.url,
    }), 201


@endpoints_bp.patch("/<endpoint_id>")
@jwt_required()
def update_endpoint(endpoint_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    endpoint = db.session.get(EndpointConfig, uuid.UUID(endpoint_id))
    if not endpoint or str(endpoint.organization_id) != org_id:
        return jsonify({"error": "Endpoint not found"}), 404

    data = request.get_json(silent=True) or {}
    for key, value in data.items():
        if hasattr(endpoint, key) and key not in ("id", "organization_id"):
            if key == "method":
                value = str(value).upper()
            setattr(endpoint, key, value)

    db.session.commit()
    return jsonify({"id": str(endpoint.id), "updated": True}), 200


@endpoints_bp.delete("/<endpoint_id>")
@jwt_required()
def delete_endpoint(endpoint_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    endpoint = db.session.get(EndpointConfig, uuid.UUID(endpoint_id))
    if not endpoint or str(endpoint.organization_id) != org_id:
        return jsonify({"error": "Endpoint not found"}), 404

    db.session.delete(endpoint)
    db.session.commit()
    return jsonify({"deleted": True}), 200


@endpoints_bp.post("/<endpoint_id>/test")
@jwt_required()
def test_endpoint(endpoint_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    endpoint = db.session.get(EndpointConfig, uuid.UUID(endpoint_id))
    if not endpoint or str(endpoint.organization_id) != org_id:
        return jsonify({"error": "Endpoint not found"}), 404

    data = request.get_json(silent=True) or {}
    payload = data.get("payload", {})

    result = EndpointService.dispatch(
        org_id=org_id,
        endpoint_name=endpoint.name,
        payload=payload
    )

    return jsonify({
        "id": str(endpoint.id),
        "success": result.get("success", False),
        "status_code": result.get("status_code", 0),
        "response": result.get("body", "")
    }), 200
