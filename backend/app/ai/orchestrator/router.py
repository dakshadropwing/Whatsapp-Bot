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

        # Step 1: Look up existing session
        agent_type = await self._get_active_agent(from_number)

        # Step 2: Classify if no active agent
        if not agent_type:
            agent_type = await self._classify(body)
            logger.info(f"Router: classified '{from_number}' → {agent_type}")

        # Step 3: Invoke agent
        agent = self._load_agent(agent_type)
        if agent:
            await agent.handle(normalized_message)
        else:
            logger.warning(f"Router: no agent found for type '{agent_type}'")

    async def _get_active_agent(self, phone: str) -> str | None:
        """Check Redis for an ongoing agent session for this phone number."""
        # TODO: implement Redis lookup
        return None

    async def _classify(self, text: str) -> str:
        """
        Use the supervisor LLM call to classify intent.
        Returns one of the keys in AGENT_REGISTRY.
        Fallback to 'support' on error.
        """
        # TODO: call supervisor LLM with intent classification prompt
        # For now return default
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
