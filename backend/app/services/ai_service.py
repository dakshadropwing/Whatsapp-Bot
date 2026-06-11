"""
AI Service — bridge between admin API and the AI orchestrator / providers.
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from sqlalchemy import func, select

from app.extensions import db
from app.models.ai_agent import AIAgent
from app.models.ai_session import AISession

logger = logging.getLogger(__name__)


class AIService:
    """Admin-facing AI operations — model health checks, session management, provider config."""

    @staticmethod
    def list_sessions(
        org_id: str,
        conversation_id: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """Return paginated AI sessions for an organization."""
        query = select(AISession).where(AISession.organization_id == uuid.UUID(org_id))
        if conversation_id:
            query = query.where(AISession.conversation_id == uuid.UUID(conversation_id))

        total = db.session.execute(select(func.count()).select_from(query.subquery())).scalar() or 0
        sessions = db.session.execute(
            query.order_by(AISession.created_at.desc()).offset((page - 1) * per_page).limit(per_page)
        ).scalars().all()

        return {
            "data": [
                {
                    "id": str(s.id),
                    "conversation_id": str(s.conversation_id) if s.conversation_id else None,
                    "agent_name": s.agent_name,
                    "status": s.status,
                    "metadata": s.metadata_,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in sessions
            ],
            "total": total, "page": page, "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }

    @staticmethod
    def get_session(session_id: str) -> Optional[AISession]:
        return db.session.get(AISession, uuid.UUID(session_id))

    @staticmethod
    def check_provider_health(provider: str = "gemini") -> dict:
        """Check if an AI provider is reachable and healthy."""
        try:
            from app.ai.providers.provider_factory import ProviderFactory
            p = ProviderFactory.get_provider(provider)
            if hasattr(p, "health_check"):
                ok = p.health_check()
                return {"provider": provider, "healthy": ok}
            return {"provider": provider, "healthy": True}
        except Exception as exc:
            logger.error("Health check failed for provider %s: %s", provider, exc)
            return {"provider": provider, "healthy": False, "error": str(exc)}

    @staticmethod
    def get_active_agents(org_id: str) -> list[dict]:
        """Return active AI agents with their provider info."""
        agents = db.session.execute(
            select(AIAgent).where(
                AIAgent.organization_id == uuid.UUID(org_id),
                AIAgent.is_active.is_(True),
            )
        ).scalars().all()
        return [
            {
                "id": str(a.id), "name": a.name, "role_type": a.role_type,
                "provider": a.provider, "model_name": a.model_name,
            }
            for a in agents
        ]

    @staticmethod
    def get_token_usage(org_id: str, days: int = 30) -> dict:
        """Return aggregate token usage stats."""
        from datetime import datetime, timedelta, timezone
        from app.models.message import Message

        since = datetime.now(timezone.utc) - timedelta(days=days)
        total_tokens = db.session.execute(
            select(func.coalesce(func.sum(Message.tokens_used), 0)).where(
                Message.organization_id == uuid.UUID(org_id),
                Message.ai_generated.is_(True),
                Message.created_at >= since,
            )
        ).scalar() or 0
        ai_messages = db.session.execute(
            select(func.count()).select_from(Message).where(
                Message.organization_id == uuid.UUID(org_id),
                Message.ai_generated.is_(True),
                Message.created_at >= since,
            )
        ).scalar() or 0
        return {"total_tokens": total_tokens, "ai_messages": ai_messages, "days": days}
