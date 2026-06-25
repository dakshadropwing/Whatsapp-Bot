"""
Knowledge Base Service — manage document collections for RAG.
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from sqlalchemy import func, select

from app.extensions import db
from app.models.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """Manages knowledge base collections — CRUD and document counts."""

    @staticmethod
    def list_knowledge_bases(org_id: str, page: int = 1, per_page: int = 20) -> dict:
        query = select(KnowledgeBase).where(KnowledgeBase.organization_id == uuid.UUID(org_id))
        total = db.session.execute(select(func.count()).select_from(query.subquery())).scalar() or 0
        kbs = db.session.execute(
            query.order_by(KnowledgeBase.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        ).scalars().all()
        return {
            "data": [
                {
                    "id": str(k.id), "organization_id": str(k.organization_id),
                    "name": k.name, "description": k.description,
                    "document_count": k.documents.count() if k.documents else 0,
                    "is_active": k.is_active,
                    "created_at": k.created_at.isoformat() if k.created_at else None,
                }
                for k in kbs
            ],
            "total": total, "page": page, "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    @staticmethod
    def get_knowledge_base(kb_id: str) -> Optional[KnowledgeBase]:
        return db.session.get(KnowledgeBase, uuid.UUID(kb_id))

    @staticmethod
    def create_knowledge_base(org_id: str, name: str, description: Optional[str] = None) -> KnowledgeBase:
        kb = KnowledgeBase(organization_id=uuid.UUID(org_id), name=name, description=description)
        db.session.add(kb)
        db.session.commit()
        logger.info("Created knowledge base %s (%s)", kb.name, kb.id)
        return kb

    @staticmethod
    def update_knowledge_base(kb_id: str, **kwargs) -> Optional[KnowledgeBase]:
        kb = db.session.get(KnowledgeBase, uuid.UUID(kb_id))
        if not kb:
            return None
        for key, value in kwargs.items():
            if hasattr(kb, key) and key not in ("id", "organization_id"):
                setattr(kb, key, value)
        db.session.commit()
        return kb

    @staticmethod
    def delete_knowledge_base(kb_id: str) -> bool:
        kb = db.session.get(KnowledgeBase, uuid.UUID(kb_id))
        if not kb:
            return False
        db.session.delete(kb)
        db.session.commit()
        logger.info("Deleted knowledge base %s", kb.id)
        return True
