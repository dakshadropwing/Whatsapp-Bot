"""
PromptTemplate Repository — reusable prompt template queries.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from app.extensions import db
from app.models.prompt_template import PromptTemplate
from app.repositories.base_repository import BaseRepository


class PromptRepository(BaseRepository[PromptTemplate]):
    """Specialised repository for PromptTemplate entity queries."""

    def __init__(self) -> None:
        super().__init__(PromptTemplate)

    def find_by_organization(self, org_id: str) -> list[PromptTemplate]:
        """Return all prompt templates for an organization, newest first."""
        return (
            db.session.execute(
                select(PromptTemplate)
                .where(PromptTemplate.organization_id == org_id)
                .order_by(PromptTemplate.created_at.desc())
            )
            .scalars()
            .all()
        )

    def find_by_category(self, org_id: str, category: str) -> list[PromptTemplate]:
        """Return prompt templates filtered by category."""
        return (
            db.session.execute(
                select(PromptTemplate)
                .where(
                    PromptTemplate.organization_id == org_id,
                    PromptTemplate.category == category,
                )
                .order_by(PromptTemplate.created_at.desc())
            )
            .scalars()
            .all()
        )

    def find_by_name(self, org_id: str, name: str) -> Optional[PromptTemplate]:
        """Look up a template by org + name (unique constraint)."""
        return db.session.execute(
            select(PromptTemplate).where(
                PromptTemplate.organization_id == org_id,
                PromptTemplate.name == name,
            )
        ).scalar_one_or_none()

    def find_active_by_organization(self, org_id: str) -> list[PromptTemplate]:
        """Return only active prompt templates for an organization."""
        return (
            db.session.execute(
                select(PromptTemplate)
                .where(
                    PromptTemplate.organization_id == org_id,
                    PromptTemplate.is_active.is_(True),
                )
                .order_by(PromptTemplate.created_at.desc())
            )
            .scalars()
            .all()
        )
