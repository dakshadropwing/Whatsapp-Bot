"""
Agent Service — CRUD for AI agent configurations.
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from sqlalchemy import func, select

from app.extensions import db
from app.models.ai_agent import AIAgent

logger = logging.getLogger(__name__)


class AgentService:
    """Manages AI agent configurations — listing, creation, toggle, updates."""

    @staticmethod
    def list_agents(
        org_id: str,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        query = select(AIAgent).where(AIAgent.organization_id == uuid.UUID(org_id))
        total = db.session.execute(
            select(func.count()).select_from(query.subquery())
        ).scalar() or 0
        agents = (
            db.session.execute(query.order_by(AIAgent.created_at.desc()).offset((page - 1) * per_page).limit(per_page))
            .scalars().all()
        )
        return {
            "data": [
                {
                    "id": str(a.id), "name": a.name, "type": a.role_type,
                    "description": a.system_prompt[:100] if a.system_prompt else "",
                    "is_active": a.is_active, "provider": a.provider,
                    "model_name": a.model_name, "organization_id": str(a.organization_id),
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                    "updated_at": a.updated_at.isoformat() if a.updated_at else None,
                }
                for a in agents
            ],
            "total": total, "page": page, "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    @staticmethod
    def get_agent(agent_id: str) -> Optional[AIAgent]:
        return db.session.get(AIAgent, uuid.UUID(agent_id))

    @staticmethod
    def create_agent(org_id: str, **kwargs) -> AIAgent:
        agent = AIAgent(organization_id=uuid.UUID(org_id), **kwargs)
        db.session.add(agent)
        db.session.commit()
        logger.info("Created agent %s (%s)", agent.name, agent.id)
        return agent

    @staticmethod
    def update_agent(agent_id: str, **kwargs) -> Optional[AIAgent]:
        agent = db.session.get(AIAgent, uuid.UUID(agent_id))
        if not agent:
            return None
        for key, value in kwargs.items():
            if hasattr(agent, key) and key not in ("id", "organization_id"):
                setattr(agent, key, value)
        db.session.commit()
        return agent

    @staticmethod
    def toggle_agent(agent_id: str) -> Optional[AIAgent]:
        agent = db.session.get(AIAgent, uuid.UUID(agent_id))
        if not agent:
            return None
        agent.is_active = not agent.is_active
        db.session.commit()
        logger.info("Toggled agent %s → %s", agent.name, agent.is_active)
        return agent

    @staticmethod
    def get_active_agents(org_id: str) -> list[AIAgent]:
        return (
            db.session.execute(
                select(AIAgent).where(
                    AIAgent.organization_id == uuid.UUID(org_id),
                    AIAgent.is_active.is_(True),
                )
            ).scalars().all()
        )

    @staticmethod
    def delete_agent(agent_id: str) -> bool:
        agent = db.session.get(AIAgent, uuid.UUID(agent_id))
        if not agent:
            return False
        agent.soft_delete()
        db.session.commit()
        logger.info("Soft-deleted agent %s (%s)", agent.name, agent.id)
        return True
