"""
Knowledge Base routes — CRUD for knowledge bases and document management.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

knowledge_base_bp = Blueprint("knowledge_base", __name__)
kb_bp = knowledge_base_bp


@knowledge_base_bp.get("/")
@jwt_required()
def list_knowledge_base():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    return jsonify({"data": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}), 200


@knowledge_base_bp.get("/<kb_id>")
@jwt_required()
def get_knowledge_base(kb_id: str):
    return jsonify({"knowledge_base": {"id": kb_id}}), 200


@knowledge_base_bp.post("/")
@jwt_required()
def create_knowledge_base():
    data = request.get_json(silent=True) or {}
    return jsonify({"id": "new", **data}), 201


@knowledge_base_bp.post("/<kb_id>/documents")
@jwt_required()
def upload_document(kb_id: str):
    # TODO: handle file upload
    return jsonify({"uploaded": True}), 201


@knowledge_base_bp.delete("/<kb_id>")
@jwt_required()
def delete_knowledge_base(kb_id: str):
    return jsonify({"deleted": True}), 200
