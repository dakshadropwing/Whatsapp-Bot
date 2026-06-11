"""
Prompts routes — CRUD for prompt templates.
"""
from __future__ import annotations

import uuid
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required

from app.services.prompt_service import PromptService

prompts_bp = Blueprint("prompts", __name__)


@prompts_bp.get("/")
@jwt_required()
def list_prompts():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    category = request.args.get("category")

    result = PromptService.list_prompts(org_id, page, per_page, category)
    return jsonify(result), 200


@prompts_bp.get("/<prompt_id>")
@jwt_required()
def get_prompt(prompt_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    prompt = PromptService.get_prompt(prompt_id)
    if not prompt or str(prompt.organization_id) != org_id:
        return jsonify({"error": "Prompt not found"}), 404

    return jsonify({
        "prompt": {
            "id": str(prompt.id),
            "organization_id": str(prompt.organization_id),
            "name": prompt.name,
            "category": prompt.category,
            "system_prompt": prompt.system_prompt,
            "user_prompt": prompt.user_prompt,
            "variables": prompt.variables or [],
            "is_active": prompt.is_active,
            "created_at": prompt.created_at.isoformat() if prompt.created_at else None,
            "updated_at": prompt.updated_at.isoformat() if prompt.updated_at else None,
        }
    }), 200


@prompts_bp.post("/")
@jwt_required()
def create_prompt():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    system_prompt = data.get("system_prompt")

    if not name or not system_prompt:
        return jsonify({"error": "name and system_prompt are required"}), 400

    prompt = PromptService.create_prompt(org_id=org_id, **data)
    return jsonify({
        "id": str(prompt.id),
        "name": prompt.name,
        "category": prompt.category,
    }), 201


@prompts_bp.patch("/<prompt_id>")
@jwt_required()
def update_prompt(prompt_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    prompt = PromptService.get_prompt(prompt_id)
    if not prompt or str(prompt.organization_id) != org_id:
        return jsonify({"error": "Prompt not found"}), 404

    data = request.get_json(silent=True) or {}
    updated_prompt = PromptService.update_prompt(prompt_id, **data)
    if not updated_prompt:
        return jsonify({"error": "Failed to update prompt"}), 400

    return jsonify({"id": str(updated_prompt.id), "updated": True}), 200


@prompts_bp.delete("/<prompt_id>")
@jwt_required()
def delete_prompt(prompt_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    prompt = PromptService.get_prompt(prompt_id)
    if not prompt or str(prompt.organization_id) != org_id:
        return jsonify({"error": "Prompt not found"}), 404

    success = PromptService.delete_prompt(prompt_id)
    return jsonify({"deleted": success}), 200
