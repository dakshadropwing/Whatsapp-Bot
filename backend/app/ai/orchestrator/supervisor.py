"""
SupervisorOrchestrator — orchestrator-level wrapper managing intents classification.
"""
from __future__ import annotations

import logging
from app.agents.supervisor_agent import SupervisorAgent

logger = logging.getLogger(__name__)


class SupervisorOrchestrator:
    """
    Decoupled orchestrator classification service that determines routing intent.
    """

    def __init__(self) -> None:
        self._agent = SupervisorAgent()

    async def determine_intent(self, text: str) -> str:
        """
        Determines the appropriate specialist agent intent for the user message.
        Falls back to 'support' on error.
        """
        try:
            intent = await self._agent.classify(text)
            logger.info("SupervisorOrchestrator: classified intent as %r", intent)
            return intent
        except Exception as exc:
            logger.exception("SupervisorOrchestrator: intent classification failed, falling back to 'support'", exc_info=exc)
            return "support"
