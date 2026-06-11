"""
Audit routes — query audit log entries.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

audit_bp = Blueprint("audit", __name__)


@audit_bp.get("/")
@jwt_required()
def list_audit():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    action = request.args.get("action")
    resource_type = request.args.get("resource_type")
    # TODO: AuditService.list(org_id, filters, page, per_page)
    return jsonify({"data": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}), 200


@audit_bp.get("/<audit_id>")
@jwt_required()
def get_audit_entry(audit_id: str):
    return jsonify({"audit": {"id": audit_id}}), 200


@audit_bp.get("/export")
@jwt_required()
def export_audit():
    # TODO: AuditService.export_csv(org_id, filters)
    return jsonify({"url": "", "message": "Export not yet implemented"}), 200
