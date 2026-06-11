"""
Agents routes — CRUD + toggle active state.
"""
from __future__ import annotations

import uuid
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required

from app.services.agent_service import AgentService

agents_bp = Blueprint("agents", __name__)


@agents_bp.get("/")
@jwt_required()
def list_agents():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))

    result = AgentService.list_agents(org_id, page, per_page)
    return jsonify(result), 200


@agents_bp.get("/<agent_id>")
@jwt_required()
def get_agent(agent_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    agent = AgentService.get_agent(agent_id)
    if not agent or str(agent.organization_id) != org_id:
        return jsonify({"error": "Agent not found"}), 404

    return jsonify({
        "agent": {
            "id": str(agent.id),
            "organization_id": str(agent.organization_id),
            "name": agent.name,
            "role_type": agent.role_type,
            "system_prompt": agent.system_prompt,
            "provider": agent.provider,
            "model_name": agent.model_name,
            "is_active": agent.is_active,
            "created_at": agent.created_at.isoformat() if agent.created_at else None,
            "updated_at": agent.updated_at.isoformat() if agent.updated_at else None,
        }
    }), 200


@agents_bp.post("/")
@jwt_required()
def create_agent():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    system_prompt = data.get("system_prompt")

    if not name or not system_prompt:
        return jsonify({"error": "name and system_prompt are required"}), 400

    agent = AgentService.create_agent(
        org_id=org_id,
        name=name,
        role_type=data.get("role_type", "support"),
        system_prompt=system_prompt,
        provider=data.get("provider", "gemini"),
        model_name=data.get("model_name", "gemini-2.5-flash"),
        is_active=data.get("is_active", True)
    )

    return jsonify({
        "id": str(agent.id),
        "name": agent.name,
        "role_type": agent.role_type,
        "is_active": agent.is_active,
    }), 201


@agents_bp.patch("/<agent_id>")
@jwt_required()
def update_agent(agent_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    agent = AgentService.get_agent(agent_id)
    if not agent or str(agent.organization_id) != org_id:
        return jsonify({"error": "Agent not found"}), 404

    data = request.get_json(silent=True) or {}
    updated_agent = AgentService.update_agent(agent_id, **data)
    if not updated_agent:
        return jsonify({"error": "Failed to update agent"}), 400

    return jsonify({"id": str(updated_agent.id), "updated": True}), 200


@agents_bp.post("/<agent_id>/toggle")
@jwt_required()
def toggle_agent(agent_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    agent = AgentService.get_agent(agent_id)
    if not agent or str(agent.organization_id) != org_id:
        return jsonify({"error": "Agent not found"}), 404

    updated_agent = AgentService.toggle_agent(agent_id)
    if not updated_agent:
        return jsonify({"error": "Failed to toggle agent"}), 400

    return jsonify({"id": str(updated_agent.id), "toggled": True, "is_active": updated_agent.is_active}), 200
