"""
Workflows routes — CRUD + toggle active state.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

workflows_bp = Blueprint("workflows", __name__)


@workflows_bp.get("/")
@jwt_required()
def list_workflows():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    # TODO: WorkflowService.list(org_id, page, per_page)
    return jsonify({"data": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}), 200


@workflows_bp.get("/<workflow_id>")
@jwt_required()
def get_workflow(workflow_id: str):
    return jsonify({"workflow": {"id": workflow_id}}), 200


@workflows_bp.post("/")
@jwt_required()
def create_workflow():
    data = request.get_json(silent=True) or {}
    return jsonify({"id": "new", **data}), 201


@workflows_bp.patch("/<workflow_id>")
@jwt_required()
def update_workflow(workflow_id: str):
    data = request.get_json(silent=True) or {}
    return jsonify({"id": workflow_id, "updated": True}), 200


@workflows_bp.post("/<workflow_id>/toggle")
@jwt_required()
def toggle_workflow(workflow_id: str):
    return jsonify({"id": workflow_id, "toggled": True}), 200
