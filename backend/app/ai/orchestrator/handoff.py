"""
SessionHandoffManager — handles conversation state transitions between bot agents and human operators.
"""
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select

from app.extensions import db
from app.models.conversation import Conversation, ConversationStatus
from app.core.config.settings import get_settings
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class SessionHandoffManager:
    """
    Manages locks and database state transitions for WhatsApp conversation threads.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self._redis_url = settings.REDIS_URL

    async def _get_redis(self) -> Any:
        return aioredis.from_url(self._redis_url, decode_responses=True)

    async def handoff_to_agent(self, phone_number: str, target_agent: str) -> bool:
        """
        Transition a conversation from the current agent to another specialist agent.
        """
        logger.info(
            "SessionHandoffManager: transitioning phone=%s to agent=%s",
            phone_number,
            target_agent,
        )
        try:
            # 1. Update Redis active agent session lock (expires in 30 minutes)
            r = await self._get_redis()
            await r.setex(f"session:agent:{phone_number}", 1800, target_agent)

            # 2. Update Database Conversation Status
            conv = db.session.execute(
                select(Conversation)
                .where(Conversation.contact_phone == phone_number)
                .order_by(Conversation.created_at.desc())
                .limit(1)
            ).scalar_one_or_none()

            if conv:
                conv.status = ConversationStatus.BOT_HANDLING
                # Store dynamic context pointer of current locked agent
                if not conv.context:
                    conv.context = {}
                conv.context["active_agent"] = target_agent
                db.session.commit()
                return True

            logger.warning("SessionHandoffManager: conversation not found for phone=%s", phone_number)
            return False

        except Exception as exc:
            logger.exception("Failed to execute agent-to-agent handoff", exc_info=exc)
            return False

    async def handoff_to_human(self, phone_number: str, reason: str) -> bool:
        """
        Escalate a bot conversation to a human handler.
        Removes the Redis active agent lock and sets DB state to HUMAN_HANDLING / ESCALATED.
        """
        logger.info(
            "SessionHandoffManager: escalating phone=%s to human. Reason: %s",
            phone_number,
            reason,
        )
        try:
            # 1. Delete active Redis lock to prevent bot from intercepting further messages
            r = await self._get_redis()
            await r.delete(f"session:agent:{phone_number}")

            # 2. Update Conversation status in Database
            conv = db.session.execute(
                select(Conversation)
                .where(Conversation.contact_phone == phone_number)
                .order_by(Conversation.created_at.desc())
                .limit(1)
            ).scalar_one_or_none()

            if conv:
                conv.status = ConversationStatus.HUMAN_HANDLING
                if not conv.context:
                    conv.context = {}
                conv.context["escalation"] = {
                    "reason": reason,
                    "escalated_by": "bot",
                }
                # Unassign any active bot agent from the DB record
                conv.assigned_agent_id = None
                db.session.commit()
                return True

            logger.warning("SessionHandoffManager: conversation not found for phone=%s", phone_number)
            return False

        except Exception as exc:
            logger.exception("Failed to execute bot-to-human escalation", exc_info=exc)
            return False

    async def resolve_conversation(self, phone_number: str) -> bool:
        """
        Mark the conversation as resolved and clear all active bot session locks.
        """
        logger.info("SessionHandoffManager: resolving conversation for phone=%s", phone_number)
        try:
            # 1. Delete Redis session lock
            r = await self._get_redis()
            await r.delete(f"session:agent:{phone_number}")

            # 2. Update DB Conversation status to RESOLVED
            conv = db.session.execute(
                select(Conversation)
                .where(Conversation.contact_phone == phone_number)
                .order_by(Conversation.created_at.desc())
                .limit(1)
            ).scalar_one_or_none()

            if conv:
                conv.status = ConversationStatus.RESOLVED
                if "active_agent" in (conv.context or {}):
                    del conv.context["active_agent"]
                db.session.commit()
                return True

            logger.warning("SessionHandoffManager: conversation not found for phone=%s", phone_number)
            return False

        except Exception as exc:
            logger.exception("Failed to resolve conversation", exc_info=exc)
            return False
