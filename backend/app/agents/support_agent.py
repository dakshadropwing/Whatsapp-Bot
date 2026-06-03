"""
Support Agent — handles customer support conversations.
"""
from __future__ import annotations

import logging
from typing import Any

from app.agents.base_agent import BaseAgent
from app.integrations.whatsapp.client import WhatsAppClient

logger = logging.getLogger(__name__)

SUPPORT_SYSTEM_PROMPT = """
You are Aria, a friendly and professional AI customer support specialist.

Your responsibilities:
- Understand customer issues clearly and empathetically.
- Provide accurate, helpful solutions from the knowledge base.
- Create support tickets for unresolved issues.
- Escalate to a human agent when the customer is frustrated or the issue is complex.
- Always maintain a warm, professional tone.

Guidelines:
- Keep responses concise and WhatsApp-friendly (no markdown).
- If you cannot resolve an issue, say so honestly and offer escalation.
- Never make up information. If unsure, say "Let me check on that for you."
- Ask clarifying questions one at a time.

Available actions:
- search_knowledge_base: Look up documentation and FAQs.
- create_ticket: Create a support ticket.
- escalate_to_human: Transfer the conversation to a human agent.
- get_ticket_status: Check the status of an existing ticket.
"""


class SupportAgent(BaseAgent):
    agent_name = "support"
    system_prompt = SUPPORT_SYSTEM_PROMPT

    def _register_tools(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_knowledge_base",
                    "description": "Search the company knowledge base for relevant articles.",
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
                    "name": "create_ticket",
                    "description": "Create a support ticket for the customer issue.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "urgent"],
                            },
                        },
                        "required": ["title", "description", "priority"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "escalate_to_human",
                    "description": "Escalate the conversation to a human support agent.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "reason": {"type": "string", "description": "Reason for escalation."}
                        },
                        "required": ["reason"],
                    },
                },
            },
        ]

    async def handle(self, message: dict[str, Any]) -> None:
        from_number = message["from"]
        body = message["body"]
        conversation_id = from_number  # Use phone as conversation key for simplicity

        try:
            response_text = await self._generate_response(
                conversation_id=conversation_id,
                user_message=body,
            )

            async with WhatsAppClient() as wa:
                await wa.send_text(to=from_number, body=response_text)

        except Exception as exc:
            logger.exception(
                f"[SupportAgent] Error handling message from {from_number}",
                exc_info=exc,
            )

    async def _execute_tool(self, tool_name: str, arguments: dict) -> Any:
        if tool_name == "search_knowledge_base":
            return await self._search_kb(arguments["query"])
        elif tool_name == "create_ticket":
            return await self._create_ticket(**arguments)
        elif tool_name == "escalate_to_human":
            return await self._escalate(arguments["reason"])
        return await super()._execute_tool(tool_name, arguments)

    async def _search_kb(self, query: str) -> dict:
        # TODO: implement RAG retrieval
        logger.info(f"[SupportAgent] KB search: {query}")
        return {"results": [], "query": query}

    async def _create_ticket(self, title: str, description: str, priority: str) -> dict:
        # TODO: implement ticket creation service call
        logger.info(f"[SupportAgent] Creating ticket: {title}")
        return {"ticket_id": "TICKET-001", "status": "created"}

    async def _escalate(self, reason: str) -> dict:
        # TODO: implement human handoff via WhatsApp handoff manager
        logger.info(f"[SupportAgent] Escalating: {reason}")
        return {"escalated": True, "reason": reason}
