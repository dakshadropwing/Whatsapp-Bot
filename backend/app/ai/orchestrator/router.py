"""
Agent Router (Supervisor) — classifies inbound messages and dispatches
them to the appropriate specialist agent.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

AGENT_REGISTRY: dict[str, str] = {
    "lead":        "app.agents.lead_agent.LeadAgent",
    "support":     "app.agents.support_agent.SupportAgent",
    "sales":       "app.agents.sales_agent.SalesAgent",
    "project":     "app.agents.project_agent.ProjectAgent",
    "hr":          "app.agents.hr_agent.HRAgent",
    "knowledge":   "app.agents.knowledge_agent.KnowledgeAgent",
    "appointment": "app.agents.appointment_agent.AppointmentAgent",
}


class AgentRouter:
    """
    Routes a normalized message to the correct specialist agent.

    Strategy:
        1. Look up the conversation's active agent from Redis/DB cache.
        2. If no active agent, run the Supervisor classification prompt.
        3. Instantiate and invoke the selected agent.
        4. Persist the active agent selection back to cache.
    """

    async def route(self, normalized_message: dict[str, Any]) -> None:
        from_number = normalized_message["from"]
        body = normalized_message["body"]
        phone_number_id = normalized_message.get("phone_number_id")

        # Step 0: Check database conversation status for active human handling
        from app.extensions import db
        from sqlalchemy import select
        from app.models.conversation import Conversation, ConversationStatus

        # Resolve tenant organization ID first by querying WhatsAppAccount with receiver's phone_number_id
        org_id = None
        if phone_number_id:
            from app.models.whatsapp_account import WhatsAppAccount
            try:
                acc = db.session.execute(
                    select(WhatsAppAccount).where(WhatsAppAccount.phone_number_id == phone_number_id)
                ).scalar_one_or_none()
                if acc:
                    org_id = acc.organization_id
            except Exception as exc:
                logger.warning("Router: failed to resolve tenant org_id from phone_number_id", exc_info=exc)

        try:
            query = select(Conversation).where(Conversation.contact_phone == from_number)
            if org_id:
                # Cast uuid.UUID if it's a string, or use directly if already a UUID
                query = query.where(Conversation.organization_id == org_id)

            conv = db.session.execute(
                query.order_by(Conversation.created_at.desc())
                .limit(1)
            ).scalar_one_or_none()

            if conv and conv.status in (ConversationStatus.HUMAN_HANDLING, ConversationStatus.ESCALATED):
                logger.info(
                    "Router: bypassing agent routing for phone=%s as status is %s",
                    from_number,
                    conv.status.value,
                )
                return
        except Exception as exc:
            logger.warning("Router: database check failed, routing normally", exc_info=exc)

        # Step 1: Look up existing session
        agent_type = await self._get_active_agent(from_number, org_id)

        # Step 2: Classify if no active agent
        if not agent_type:
            agent_type = await self._classify(body)
            logger.info(f"Router: classified '{from_number}' (org={org_id}) → {agent_type}")

        # Step 3: Extend or save the active session in cache
        await self._set_active_agent(from_number, agent_type, org_id)

        # Step 4: Invoke agent
        agent = self._load_agent(agent_type)
        if agent:
            await agent.handle(normalized_message)
        else:
            logger.warning(f"Router: no agent found for type '{agent_type}'")

    async def _get_active_agent(self, phone: str, org_id: Any | None = None) -> str | None:
        """Check Redis for an ongoing agent session for this phone number."""
        import redis.asyncio as aioredis
        from app.core.config.settings import get_settings
        settings = get_settings()
        try:
            r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            key = f"session:agent:{org_id}:{phone}" if org_id else f"session:agent:{phone}"
            return await r.get(key)
        except Exception as exc:
            logger.warning(f"Failed to fetch active agent session for phone {phone} from Redis", exc_info=exc)
            return None

    async def _set_active_agent(self, phone: str, agent_type: str, org_id: Any | None = None) -> None:
        """Save the active agent to Redis (expires after 30 minutes)."""
        import redis.asyncio as aioredis
        from app.core.config.settings import get_settings
        settings = get_settings()
        try:
            r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            key = f"session:agent:{org_id}:{phone}" if org_id else f"session:agent:{phone}"
            await r.setex(key, 1800, agent_type)
        except Exception as exc:
            logger.warning(f"Failed to persist active agent session for phone {phone} to Redis", exc_info=exc)

    async def _classify(self, text: str) -> str:
        """
        Use the supervisor LLM call to classify intent.
        Returns one of the keys in AGENT_REGISTRY.
        Fallback to 'support' on error.
        """
        from app.ai.orchestrator.supervisor import SupervisorOrchestrator
        try:
            orchestrator = SupervisorOrchestrator()
            return await orchestrator.determine_intent(text)
        except Exception as exc:
            logger.exception("Failed to classify using SupervisorOrchestrator, falling back to 'support'", exc_info=exc)
            return "support"

    def _load_agent(self, agent_type: str):
        """Dynamically import and instantiate the agent class."""
        import importlib
        module_path = AGENT_REGISTRY.get(agent_type)
        if not module_path:
            return None
        try:
            parts = module_path.rsplit(".", 1)
            module = importlib.import_module(parts[0])
            klass = getattr(module, parts[1])
            return klass()
        except Exception as exc:
            logger.exception(f"Failed to load agent '{agent_type}'", exc_info=exc)
            return None
