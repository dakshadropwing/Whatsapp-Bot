"""
Supervisor Agent — classifies inbound user messages to determine the appropriate specialist agent.
"""
from __future__ import annotations

import logging
from typing import Any

from app.agents.base_agent import BaseAgent
from app.utils.helpers import load_prompt

logger = logging.getLogger(__name__)

SUPERVISOR_SYSTEM_PROMPT = load_prompt(
    "prompts/agents/supervisor.md",
    default=(
        "You are a message classifier for an AI WhatsApp bot.\n"
        "Your ONLY job is to read a message and output ONE of these agent names:\n"
        "support, sales, lead, project, hr, appointment, knowledge.\n"
        "Output ONLY the agent name, nothing else. No punctuation, no explanation."
    )
)


class SupervisorAgent(BaseAgent):
    agent_name = "supervisor"
    system_prompt = SUPERVISOR_SYSTEM_PROMPT

    def _register_tools(self) -> list[dict]:
        return []  # Supervisor has no tools; it only classifies.

    async def handle(self, message: dict[str, Any]) -> None:
        # Supervisor is not invoked directly to respond to messages via handle()
        pass

    async def classify(self, user_message: str) -> str:
        """
        Classify a message and return the agent type.
        Returns a string like 'support', 'sales', 'lead', etc.
        """
        from app.ai.providers.base_provider import CompletionRequest, Message

        request = CompletionRequest(
            messages=[
                Message(role="system", content=self.system_prompt),
                Message(role="user", content=user_message),
            ],
            temperature=0.0,  # Zero temperature for deterministic classification
            max_tokens=10,    # We only need one word
        )

        try:
            response = await self.provider.complete(request)
            agent_type = response.content.strip().lower()

            # Clean any trailing punctuation (like a period)
            if agent_type.endswith("."):
                agent_type = agent_type[:-1]

            valid_agents = {
                "support",
                "sales",
                "lead",
                "project",
                "hr",
                "appointment",
                "knowledge",
            }

            if agent_type not in valid_agents:
                logger.warning(
                    "[SupervisorAgent] Unknown classification result %r, defaulting to 'support'",
                    agent_type,
                )
                return "support"

            return agent_type

        except Exception as exc:
            logger.exception("[SupervisorAgent] Error during classification classification", exc_info=exc)
            return "support"
