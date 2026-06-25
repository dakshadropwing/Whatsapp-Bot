"""
Prompt Service — CRUD for reusable AI prompt templates.
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from sqlalchemy import func, select

from app.extensions import db
from app.models.prompt_template import PromptTemplate

logger = logging.getLogger(__name__)


class PromptService:
    """Manages prompt templates — creation, editing, variable management."""

    @staticmethod
    def list_prompts(org_id: str, page: int = 1, per_page: int = 20, category: Optional[str] = None) -> dict:
        query = select(PromptTemplate).where(PromptTemplate.organization_id == uuid.UUID(org_id))
        if category:
            query = query.where(PromptTemplate.category == category)
        total = db.session.execute(select(func.count()).select_from(query.subquery())).scalar() or 0
        prompts = db.session.execute(
            query.order_by(PromptTemplate.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        ).scalars().all()
        return {
            "data": [
                {
                    "id": str(p.id), "name": p.name, "category": p.category,
                    "system_prompt": p.system_prompt, "user_prompt": p.user_prompt,
                    "variables": p.variables or [], "organization_id": str(p.organization_id),
                    "is_active": p.is_active,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in prompts
            ],
            "total": total, "page": page, "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    @staticmethod
    def get_prompt(prompt_id: str) -> Optional[PromptTemplate]:
        return db.session.get(PromptTemplate, uuid.UUID(prompt_id))

    @staticmethod
    def create_prompt(org_id: str, **kwargs) -> PromptTemplate:
        pt = PromptTemplate(organization_id=uuid.UUID(org_id), **kwargs)
        db.session.add(pt)
        db.session.commit()
        logger.info("Created prompt template %s (%s)", pt.name, pt.id)
        return pt

    @staticmethod
    def update_prompt(prompt_id: str, **kwargs) -> Optional[PromptTemplate]:
        pt = db.session.get(PromptTemplate, uuid.UUID(prompt_id))
        if not pt:
            return None
        for key, value in kwargs.items():
            if hasattr(pt, key) and key not in ("id", "organization_id"):
                setattr(pt, key, value)
        db.session.commit()
        return pt

    @staticmethod
    def delete_prompt(prompt_id: str) -> bool:
        pt = db.session.get(PromptTemplate, uuid.UUID(prompt_id))
        if not pt:
            return False
        db.session.delete(pt)
        db.session.commit()
        return True

    @staticmethod
    def get_by_name(org_id: str, name: str) -> Optional[PromptTemplate]:
        return db.session.execute(
            select(PromptTemplate).where(
                PromptTemplate.organization_id == uuid.UUID(org_id),
                PromptTemplate.name == name,
            )
        ).scalar_one_or_none()
