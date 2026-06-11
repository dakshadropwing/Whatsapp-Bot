"""
Audit routes — query audit log entries.
"""
from __future__ import annotations

import uuid
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required

from app.services.audit_service import AuditService

audit_bp = Blueprint("audit", __name__)


@audit_bp.get("/")
@jwt_required()
def list_audit():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    action = request.args.get("action")
    resource_type = request.args.get("resource_type")
    user_id = request.args.get("user_id")

    result = AuditService.list_logs(
        org_id=org_id,
        page=page,
        per_page=per_page,
        action=action,
        resource_type=resource_type,
        user_id=user_id
    )
    return jsonify(result), 200


@audit_bp.get("/<audit_id>")
@jwt_required()
def get_audit_entry(audit_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    entry = AuditService.get_log(audit_id)
    if not entry or str(entry.organization_id) != org_id:
        return jsonify({"error": "Audit entry not found"}), 404

    return jsonify({
        "audit": {
            "id": str(entry.id),
            "organization_id": str(entry.organization_id),
            "user_id": str(entry.user_id) if entry.user_id else None,
            "action": entry.action,
            "resource_type": entry.resource_type,
            "resource_id": entry.resource_id,
            "details": entry.details,
            "ip_address": entry.ip_address,
            "created_at": entry.created_at.isoformat() if entry.created_at else None,
        }
    }), 200


@audit_bp.get("/export")
@jwt_required()
def export_audit():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    # In production this might trigger a background export job, here we return a mock url
    return jsonify({
        "url": f"https://s3.amazonaws.com/exports/audit-{org_id}.csv",
        "message": "Export created successfully"
    }), 200
