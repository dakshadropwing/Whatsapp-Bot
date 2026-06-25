"""
Workflows routes — CRUD + toggle active state.
"""
from __future__ import annotations

import uuid
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required

from app.services.workflow_service import WorkflowService

workflows_bp = Blueprint("workflows", __name__)


@workflows_bp.get("/")
@jwt_required()
def list_workflows():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))

    result = WorkflowService.list_workflows(org_id, page, per_page)
    return jsonify(result), 200


@workflows_bp.get("/<workflow_id>")
@jwt_required()
def get_workflow(workflow_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    wf = WorkflowService.get_workflow(workflow_id)
    if not wf or str(wf.organization_id) != org_id:
        return jsonify({"error": "Workflow not found"}), 404

    return jsonify({
        "workflow": {
            "id": str(wf.id),
            "organization_id": str(wf.organization_id),
            "name": wf.name,
            "description": wf.description,
            "trigger": wf.trigger,
            "steps": wf.steps or [],
            "is_active": wf.is_active,
            "run_count": wf.run_count,
            "last_run_at": wf.last_run_at.isoformat() if wf.last_run_at else None,
            "created_at": wf.created_at.isoformat() if wf.created_at else None,
            "updated_at": wf.updated_at.isoformat() if wf.updated_at else None,
        }
    }), 200


@workflows_bp.post("/")
@jwt_required()
def create_workflow():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    trigger = data.get("trigger")

    if not name or not trigger:
        return jsonify({"error": "name and trigger are required"}), 400

    wf = WorkflowService.create_workflow(
        org_id=org_id,
        name=name,
        trigger=trigger,
        description=data.get("description"),
        steps=data.get("steps", [])
    )
    return jsonify({
        "id": str(wf.id),
        "name": wf.name,
        "trigger": wf.trigger,
        "is_active": wf.is_active,
    }), 201


@workflows_bp.patch("/<workflow_id>")
@jwt_required()
def update_workflow(workflow_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    wf = WorkflowService.get_workflow(workflow_id)
    if not wf or str(wf.organization_id) != org_id:
        return jsonify({"error": "Workflow not found"}), 404

    data = request.get_json(silent=True) or {}
    updated_wf = WorkflowService.update_workflow(workflow_id, **data)
    if not updated_wf:
        return jsonify({"error": "Failed to update workflow"}), 400

    return jsonify({"id": str(updated_wf.id), "updated": True}), 200


@workflows_bp.post("/<workflow_id>/toggle")
@jwt_required()
def toggle_workflow(workflow_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    wf = WorkflowService.get_workflow(workflow_id)
    if not wf or str(wf.organization_id) != org_id:
        return jsonify({"error": "Workflow not found"}), 404

    updated_wf = WorkflowService.toggle_workflow(workflow_id)
    if not updated_wf:
        return jsonify({"error": "Failed to toggle workflow"}), 400

    return jsonify({"id": str(updated_wf.id), "toggled": True, "is_active": updated_wf.is_active}), 200


@workflows_bp.delete("/<workflow_id>")
@jwt_required()
def delete_workflow(workflow_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    wf = WorkflowService.get_workflow(workflow_id)
    if not wf or str(wf.organization_id) != org_id:
        return jsonify({"error": "Workflow not found"}), 404

    success = WorkflowService.delete_workflow(workflow_id)
    return jsonify({"deleted": success}), 200
