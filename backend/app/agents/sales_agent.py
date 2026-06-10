"""
Sales Agent — handles product, package, pricing inquiries, and qualifying sales leads.
"""
from __future__ import annotations

import logging
from typing import Any

from app.agents.base_agent import BaseAgent
from app.integrations.whatsapp.client import WhatsAppClient
from app.utils.helpers import load_prompt

logger = logging.getLogger(__name__)

SALES_SYSTEM_PROMPT = load_prompt(
    "prompts/agents/sales_agent.md",
    default=(
        "You are Aria, a friendly sales specialist.\n"
        "Your goal is to answer sales inquiries about pricing, packages, and options, and guide users to make purchasing decisions.\n"
        "Use search_knowledge_base to answer questions accurately."
    )
)


class SalesAgent(BaseAgent):
    agent_name = "sales"
    system_prompt = SALES_SYSTEM_PROMPT

    def _register_tools(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Search the company knowledge base for sales playbooks, pricing lists, and packages.",
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
                    "name": "get_contact_info",
                    "description": "Retrieve stored information about the customer.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "phone_number": {
                                "type": "string",
                                "description": "Customer phone number in E.164 format.",
                            }
                        },
                        "required": ["phone_number"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "update_contact_fact",
                    "description": "Save a persistent fact about the customer (e.g. key interests, budget, timeline).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "Fact key, e.g., 'user_name', 'interests', 'budget'.",
                            },
                            "value": {
                                "type": "string",
                                "description": "Fact value to store.",
                            },
                        },
                        "required": ["key", "value"],
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
                "[SalesAgent] Error handling message from %s",
                from_number,
                exc_info=exc,
            )

    async def _execute_tool(self, tool_name: str, arguments: dict) -> Any:
        from app.extensions import db
        from sqlalchemy import select
        from app.models.conversation import Conversation
        from app.models.knowledge_base import KnowledgeBase

        # We assume the conversation ID is the customer phone number
        phone_number = arguments.get("phone_number") or arguments.get("conversation_id")

        # Fallback to query database for the active phone number
        conv = None
        if phone_number:
            conv = db.session.execute(
                select(Conversation)
                .where(Conversation.contact_phone == phone_number)
                .order_by(Conversation.created_at.desc())
                .limit(1)
            ).scalar_one_or_none()

        if tool_name == "search_knowledge_base":
            from app.ai.tools import SearchTool
            # Find the conversation object to resolve organization_id
            if not conv:
                # Find any active conversation for general lookup, or use organization's default KB
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

        elif tool_name == "get_contact_info":
            from app.ai.tools import GetContactInfoTool
            query_phone = phone_number or (conv.contact_phone if conv else "")
            tool = GetContactInfoTool(db_session=db.session)
            return await tool.safe_execute(phone_number=query_phone)

        elif tool_name == "update_contact_fact":
            from app.ai.tools import UpdateContactFactTool
            if not conv:
                return {"error": "Conversation not found"}
            tool = UpdateContactFactTool(
                db_session=db.session,
                conversation_obj=conv,
                context_manager=self.memory,
            )
            result = await tool.safe_execute(
                key=arguments.get("key", ""),
                value=arguments.get("value", ""),
            )
            db.session.commit()
            return result

        return await super()._execute_tool(tool_name, arguments)
