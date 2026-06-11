"""
KnowledgeBase Repository — document collection queries.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select

from app.extensions import db
from app.models.knowledge_base import KnowledgeBase
from app.repositories.base_repository import BaseRepository


class KnowledgeBaseRepository(BaseRepository[KnowledgeBase]):
    """Specialised repository for KnowledgeBase entity queries."""

    def __init__(self) -> None:
        super().__init__(KnowledgeBase)

    def find_by_organization(self, org_id: str) -> list[KnowledgeBase]:
        """Return all knowledge bases for an organization, newest first."""
        return (
            db.session.execute(
                select(KnowledgeBase)
                .where(KnowledgeBase.organization_id == org_id)
                .order_by(KnowledgeBase.created_at.desc())
            )
            .scalars()
            .all()
        )

    def find_active_by_organization(self, org_id: str) -> list[KnowledgeBase]:
        """Return only active knowledge bases for an organization."""
        return (
            db.session.execute(
                select(KnowledgeBase)
                .where(
                    KnowledgeBase.organization_id == org_id,
                    KnowledgeBase.is_active.is_(True),
                )
                .order_by(KnowledgeBase.created_at.desc())
            )
            .scalars()
            .all()
        )

    def find_by_name(self, org_id: str, name: str) -> Optional[KnowledgeBase]:
        """Look up a KB by org + name (unique constraint)."""
        return db.session.execute(
            select(KnowledgeBase).where(
                KnowledgeBase.organization_id == org_id,
                KnowledgeBase.name == name,
            )
        ).scalar_one_or_none()

    def count_documents(self, kb_id: str) -> int:
        """Return the number of documents in a knowledge base."""
        from app.models.document import Document

        result = db.session.execute(
            select(func.count())
            .select_from(Document)
            .where(Document.knowledge_base_id == kb_id)
        ).scalar()
        return result or 0
