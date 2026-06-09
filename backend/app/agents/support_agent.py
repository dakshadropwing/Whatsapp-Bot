"""
Support Agent — handles customer support conversations.

Uses the tool registry pattern from BaseAgent:
  - SearchTool        → RAG knowledge-base search
  - TicketTool        → create support tickets
  - GetTicketStatusTool → look up ticket status
  - escalate_to_human → manual action (no BaseTool class needed)
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
        """
        Register tool instances and return schemas.

        NOTE: SearchTool and TicketTool require a db_session and
        organization/KB IDs which are normally injected when the
        agent is instantiated from a request context.  For now,
        these tools are registered lazily — the schemas are
        hardcoded so the LLM knows what's available, and the
        tool registry is populated at ``handle()`` time when we
        have the request context.

        This matches the existing pattern where ``_execute_tool``
        does the actual work.
        """
        # Return static schemas so the LLM always knows the tools
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
                    "name": "get_ticket_status",
                    "description": "Get the current status of a support ticket by its ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {"type": "string", "description": "UUID of the ticket."},
                        },
                        "required": ["ticket_id"],
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
                "[SupportAgent] Error handling message from %s",
                from_number,
                exc_info=exc,
            )

    async def _execute_tool(self, tool_name: str, arguments: dict) -> Any:
        """
        Dispatch tool calls.

        For tools that need a DB session (SearchTool, TicketTool), we
        instantiate them here where the request context is available.
        For stateless tools (escalate_to_human), we handle inline.
        """
        if tool_name == "search_knowledge_base":
            return await self._search_kb(arguments.get("query", ""))
        elif tool_name == "create_ticket":
            return await self._create_ticket(
                title=arguments.get("title", ""),
                description=arguments.get("description", ""),
                priority=arguments.get("priority", "medium"),
            )
        elif tool_name == "get_ticket_status":
            return await self._get_ticket_status(
                ticket_id=arguments.get("ticket_id", ""),
            )
        elif tool_name == "escalate_to_human":
            return await self._escalate(arguments.get("reason", ""))

        return await super()._execute_tool(tool_name, arguments)

    # ── Private tool implementations ──────────────────────────────────────

    async def _search_kb(self, query: str) -> dict:
        """
        Search the knowledge base using the SearchTool.

        Falls back gracefully if no KB is configured for the conversation.
        """
        from app.ai.tools import SearchTool
        from app.extensions import db

        # TODO: resolve the KB ID from the conversation's organization
        #       For now, log and return empty results
        logger.info("[SupportAgent] KB search: %r", query)

        # When a KB ID is available, uncomment:
        # tool = SearchTool(
        #     knowledge_base_id=kb_id,
        #     db_session=db.session,
        # )
        # return await tool.safe_execute(query=query)

        return {"found": False, "results": [], "query": query}

    async def _create_ticket(
        self, title: str, description: str, priority: str
    ) -> dict:
        """Create a ticket using the TicketTool."""
        from app.ai.tools import TicketTool
        from app.extensions import db

        # TODO: resolve org_id from the conversation
        #       For now, log and return a stub
        logger.info("[SupportAgent] Creating ticket: %s", title)

        # When org_id is available, uncomment:
        # tool = TicketTool(
        #     db_session=db.session,
        #     organization_id=org_id,
        #     conversation_id=conv_id,
        # )
        # result = await tool.safe_execute(
        #     title=title, description=description, priority=priority,
        # )
        # db.session.commit()
        # return result

        return {"ticket_id": "pending_setup", "status": "created", "title": title}

    async def _get_ticket_status(self, ticket_id: str) -> dict:
        """Look up a ticket using the GetTicketStatusTool."""
        from app.ai.tools import GetTicketStatusTool
        from app.extensions import db

        tool = GetTicketStatusTool(db_session=db.session)
        return await tool.safe_execute(ticket_id=ticket_id)

    async def _escalate(self, reason: str) -> dict:
        """Escalate the conversation to a human agent."""
        # TODO: implement human handoff via WhatsApp handoff manager
        logger.info("[SupportAgent] Escalating: %s", reason)
        return {"escalated": True, "reason": reason}
