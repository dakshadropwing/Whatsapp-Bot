"""
Agent Repository — query helpers for AI agent configurations.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from app.extensions import db
from app.models.ai_agent import AIAgent
from app.repositories.base_repository import BaseRepository


class AgentRepository(BaseRepository[AIAgent]):
    """Specialised repository for AIAgent entity queries."""

    def __init__(self) -> None:
        super().__init__(AIAgent)

    def find_by_organization(self, org_id: str) -> list[AIAgent]:
        """Return all agents for an organization, newest first."""
        return (
            db.session.execute(
                select(AIAgent)
                .where(AIAgent.organization_id == org_id)
                .order_by(AIAgent.created_at.desc())
            )
            .scalars()
            .all()
        )

    def find_active_by_organization(self, org_id: str) -> list[AIAgent]:
        """Return only active agents for an organization."""
        return (
            db.session.execute(
                select(AIAgent)
                .where(
                    AIAgent.organization_id == org_id,
                    AIAgent.is_active.is_(True),
                )
                .order_by(AIAgent.created_at.desc())
            )
            .scalars()
            .all()
        )

    def find_by_name(self, org_id: str, name: str) -> Optional[AIAgent]:
        """Look up an agent by org + name."""
        return db.session.execute(
            select(AIAgent).where(
                AIAgent.organization_id == org_id,
                AIAgent.name == name,
            )
        ).scalar_one_or_none()

    def find_by_role_type(self, org_id: str, role_type: str) -> list[AIAgent]:
        """Return agents filtered by role type (support, sales, lead, etc.)."""
        return (
            db.session.execute(
                select(AIAgent)
                .where(
                    AIAgent.organization_id == org_id,
                    AIAgent.role_type == role_type,
                    AIAgent.is_active.is_(True),
                )
                .order_by(AIAgent.created_at.desc())
            )
            .scalars()
            .all()
        )
