"""
Prompts routes — CRUD for prompt templates.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

prompts_bp = Blueprint("prompts", __name__)


@prompts_bp.get("/")
@jwt_required()
def list_prompts():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    return jsonify({"data": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}), 200


@prompts_bp.get("/<prompt_id>")
@jwt_required()
def get_prompt(prompt_id: str):
    return jsonify({"prompt": {"id": prompt_id}}), 200


@prompts_bp.post("/")
@jwt_required()
def create_prompt():
    data = request.get_json(silent=True) or {}
    return jsonify({"id": "new", **data}), 201


@prompts_bp.patch("/<prompt_id>")
@jwt_required()
def update_prompt(prompt_id: str):
    data = request.get_json(silent=True) or {}
    return jsonify({"id": prompt_id, "updated": True}), 200


@prompts_bp.delete("/<prompt_id>")
@jwt_required()
def delete_prompt(prompt_id: str):
    return jsonify({"deleted": True}), 200
