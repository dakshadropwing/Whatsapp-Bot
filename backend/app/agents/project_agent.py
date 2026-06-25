"""
Project Agent — handles project status, deliverables, or timelines using RAG and custom endpoints.
"""
from __future__ import annotations

import logging
from typing import Any

from app.agents.base_agent import BaseAgent
from app.integrations.whatsapp.client import WhatsAppClient
from app.utils.helpers import load_prompt

logger = logging.getLogger(__name__)

PROJECT_SYSTEM_PROMPT = load_prompt(
    "prompts/agents/project_agent.md",
    default=(
        "You are Aria, a project management assistant.\n"
        "Your goal is to answer questions about project status, deliverables, or timelines.\n"
        "Use search_knowledge_base or call_custom_endpoint to find project details."
    )
)


class ProjectAgent(BaseAgent):
    agent_name = "project"
    system_prompt = PROJECT_SYSTEM_PROMPT

    def _register_tools(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Search the knowledge base for project specs, status logs, or documentation.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query."}
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "call_custom_endpoint",
                    "description": "Call an external endpoint to query live project management tool state.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "endpoint_name": {
                                "type": "string",
                                "description": "Name of the configured endpoint (e.g. 'project_status').",
                            },
                            "payload": {
                                "type": "object",
                                "description": "JSON payload containing project IDs or parameters.",
                            },
                        },
                        "required": ["endpoint_name", "payload"],
                    },
                },
            },
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
                "[ProjectAgent] Error handling message from %s",
                from_number,
                exc_info=exc,
            )

    async def _execute_tool(self, tool_name: str, arguments: dict) -> Any:
        from app.extensions import db
        from sqlalchemy import select
        from app.models.conversation import Conversation

        # Find active conversation to resolve organization_id
        conv = db.session.query(Conversation).order_by(Conversation.created_at.desc()).first()
        if not conv:
            return {"error": "No conversation context to resolve tenant organization"}

        if tool_name == "search_knowledge_base":
            from app.models.knowledge_base import KnowledgeBase
            from app.ai.tools import SearchTool

            kb = db.session.execute(
                select(KnowledgeBase)
                .where(KnowledgeBase.organization_id == conv.organization_id, KnowledgeBase.is_active == True)
                .limit(1)
            ).scalar_one_or_none()
            if kb:
                tool = SearchTool(knowledge_base_id=kb.id, db_session=db.session)
                return await tool.safe_execute(query=arguments.get("query", ""))

            return {"found": False, "results": [], "error": "Knowledge base not configured"}

        elif tool_name == "call_custom_endpoint":
            from app.ai.tools.endpoint_tool import CallEndpointTool
            tool = CallEndpointTool(
                db_session=db.session,
                organization_id=conv.organization_id,
            )
            return await tool.safe_execute(
                endpoint_name=arguments.get("endpoint_name", ""),
                payload=arguments.get("payload", {}),
            )

        return await super()._execute_tool(tool_name, arguments)
