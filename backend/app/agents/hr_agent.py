"""
HR Agent — handles internal employee queries using the RAG search.
"""
from __future__ import annotations

import logging
from typing import Any

from app.agents.base_agent import BaseAgent
from app.integrations.whatsapp.client import WhatsAppClient
from app.utils.helpers import load_prompt

logger = logging.getLogger(__name__)

HR_SYSTEM_PROMPT = load_prompt(
    "prompts/agents/hr_agent.md",
    default=(
        "You are Aria, an internal HR assistant.\n"
        "Your goal is to help employees with HR-related queries (policies, handbook, leave policies, payroll FAQs).\n"
        "Search the knowledge base using search_knowledge_base to answer HR questions."
    )
)


class HRAgent(BaseAgent):
    agent_name = "hr"
    system_prompt = HR_SYSTEM_PROMPT

    def _register_tools(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Search the HR knowledge base for policies, handbooks, and documents.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query."}
                        },
                        "required": ["query"],
                    },
                },
            }
        ]

    async def handle(self, message: dict[str, Any]) -> None:
        from_number = message["from"]
        body = message["body"]
        conversation_id = from_number

        try:
            response_text = await self._generate_response(
                conversation_id=conversation_id,
                user_message=body,
            )

            async with WhatsAppClient() as wa:
                await wa.send_text(to=from_number, body=response_text)

        except Exception as exc:
            logger.exception(
                "[HRAgent] Error handling message from %s",
                from_number,
                exc_info=exc,
            )

    async def _execute_tool(self, tool_name: str, arguments: dict) -> Any:
        if tool_name == "search_knowledge_base":
            from app.extensions import db
            from sqlalchemy import select
            from app.models.conversation import Conversation
            from app.models.knowledge_base import KnowledgeBase
            from app.ai.tools import SearchTool

            # Find the conversation object to resolve organization_id
            # We assume conversation ID is the phone number from the handle loop
            conv = db.session.query(Conversation).order_by(Conversation.created_at.desc()).first()

            if conv:
                kb = db.session.execute(
                    select(KnowledgeBase)
                    .where(KnowledgeBase.organization_id == conv.organization_id, KnowledgeBase.is_active == True)
                    .limit(1)
                ).scalar_one_or_none()
                if kb:
                    tool = SearchTool(knowledge_base_id=kb.id, db_session=db.session)
                    return await tool.safe_execute(query=arguments.get("query", ""))

            return {"found": False, "results": [], "error": "Knowledge base not configured"}

        return await super()._execute_tool(tool_name, arguments)
