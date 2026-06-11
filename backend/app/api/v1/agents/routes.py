"""
Agents routes — CRUD + toggle active state.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

agents_bp = Blueprint("agents", __name__)


@agents_bp.get("/")
@jwt_required()
def list_agents():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    # TODO: AgentService.list(org_id, page, per_page)
    return jsonify({"data": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}), 200


@agents_bp.get("/<agent_id>")
@jwt_required()
def get_agent(agent_id: str):
    # TODO: AgentService.get(agent_id)
    return jsonify({"agent": {"id": agent_id}}), 200


@agents_bp.post("/")
@jwt_required()
def create_agent():
    data = request.get_json(silent=True) or {}
    # TODO: AgentService.create(data)
    return jsonify({"id": "new", **data}), 201


@agents_bp.patch("/<agent_id>")
@jwt_required()
def update_agent(agent_id: str):
    data = request.get_json(silent=True) or {}
    # TODO: AgentService.update(agent_id, data)
    return jsonify({"id": agent_id, "updated": True}), 200


@agents_bp.post("/<agent_id>/toggle")
@jwt_required()
def toggle_agent(agent_id: str):
    # TODO: AgentService.toggle(agent_id)
    return jsonify({"id": agent_id, "toggled": True}), 200
