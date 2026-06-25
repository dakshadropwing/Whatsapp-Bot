"""
Knowledge Base routes — CRUD for knowledge bases and document management.
"""
from __future__ import annotations

import uuid
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.knowledge_base import KnowledgeBase
from app.models.document import Document, SourceType, DocumentStatus
from app.services.knowledge_base_service import KnowledgeBaseService

knowledge_base_bp = Blueprint("knowledge_base", __name__)
kb_bp = knowledge_base_bp


@knowledge_base_bp.get("/")
@jwt_required()
def list_knowledge_base():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))

    result = KnowledgeBaseService.list_knowledge_bases(org_id, page, per_page)
    return jsonify(result), 200


@knowledge_base_bp.get("/<kb_id>")
@jwt_required()
def get_knowledge_base(kb_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    kb = KnowledgeBaseService.get_knowledge_base(kb_id)
    if not kb or str(kb.organization_id) != org_id:
        return jsonify({"error": "Knowledge base not found"}), 404

    return jsonify({
        "knowledge_base": {
            "id": str(kb.id),
            "organization_id": str(kb.organization_id),
            "name": kb.name,
            "description": kb.description,
            "is_active": kb.is_active,
            "created_at": kb.created_at.isoformat() if kb.created_at else None,
            "updated_at": kb.updated_at.isoformat() if kb.updated_at else None,
        }
    }), 200


@knowledge_base_bp.post("/")
@jwt_required()
def create_knowledge_base():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    data = request.get_json(silent=True) or {}
    name = data.get("name")
    description = data.get("description")

    if not name:
        return jsonify({"error": "name is required"}), 400

    kb = KnowledgeBaseService.create_knowledge_base(org_id, name, description)
    return jsonify({
        "id": str(kb.id),
        "name": kb.name,
        "description": kb.description,
    }), 201


@knowledge_base_bp.post("/<kb_id>/documents")
@jwt_required()
def upload_document(kb_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    kb = KnowledgeBaseService.get_knowledge_base(kb_id)
    if not kb or str(kb.organization_id) != org_id:
        return jsonify({"error": "Knowledge base not found"}), 404

    # We support either file upload or json upload (e.g. text/url)
    if 'file' in request.files:
        file = request.files['file']
        name = file.filename or "uploaded_file"
        raw_text = file.read().decode('utf-8', errors='ignore')
        source_type = SourceType.TEXT
        if name.endswith('.pdf'):
            source_type = SourceType.PDF
        elif name.endswith('.csv'):
            source_type = SourceType.CSV
        elif name.endswith('.docx'):
            source_type = SourceType.DOCX
        file_size_bytes = len(raw_text)
        source_url = None
    else:
        data = request.get_json(silent=True) or {}
        name = data.get("name")
        raw_text = data.get("raw_text", "")
        source_type = data.get("source_type", SourceType.TEXT)
        source_url = data.get("source_url")
        file_size_bytes = len(raw_text) if raw_text else 0

    if not name:
        return jsonify({"error": "Document name or file is required"}), 400

    doc = Document(
        knowledge_base_id=uuid.UUID(kb_id),
        name=name,
        source_type=source_type,
        source_url=source_url,
        raw_text=raw_text,
        file_size_bytes=file_size_bytes,
        status=DocumentStatus.PENDING
    )
    db.session.add(doc)
    db.session.commit()

    if raw_text:
        from app.tasks.ai_tasks import generate_embedding
        generate_embedding.delay(str(doc.id), raw_text)

    return jsonify({
        "id": str(doc.id),
        "name": doc.name,
        "status": doc.status,
        "uploaded": True
    }), 201


@knowledge_base_bp.delete("/<kb_id>")
@jwt_required()
def delete_knowledge_base(kb_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    kb = KnowledgeBaseService.get_knowledge_base(kb_id)
    if not kb or str(kb.organization_id) != org_id:
        return jsonify({"error": "Knowledge base not found"}), 404

    success = KnowledgeBaseService.delete_knowledge_base(kb_id)
    return jsonify({"deleted": success}), 200
