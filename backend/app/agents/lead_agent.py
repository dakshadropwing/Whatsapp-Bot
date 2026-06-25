"""
Lead Agent — handles qualifying potential customers and capturing contact info.
"""
from __future__ import annotations

import logging
from typing import Any

from app.agents.base_agent import BaseAgent
from app.integrations.whatsapp.client import WhatsAppClient
from app.utils.helpers import load_prompt

logger = logging.getLogger(__name__)

LEAD_SYSTEM_PROMPT = load_prompt(
    "prompts/agents/lead_agent.md",
    default=(
        "You are Aria, a friendly sales development representative.\n"
        "Your goal is to qualify potential leads and capture their contact details.\n"
        "Ask about business needs, name, company, email, and update contact facts."
    )
)


class LeadAgent(BaseAgent):
    agent_name = "lead"
    system_prompt = LEAD_SYSTEM_PROMPT

    def _register_tools(self) -> list[dict]:
        return [
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
                    "description": "Save a persistent fact about the customer (e.g. name, company, preferences).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "Fact key, e.g., 'user_name', 'company', 'email'.",
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
                "[LeadAgent] Error handling message from %s",
                from_number,
                exc_info=exc,
            )

    async def _execute_tool(self, tool_name: str, arguments: dict) -> Any:
        from app.extensions import db
        from sqlalchemy import select
        from app.models.conversation import Conversation

        if tool_name == "get_contact_info":
            from app.ai.tools import GetContactInfoTool
            tool = GetContactInfoTool(db_session=db.session)
            return await tool.safe_execute(phone_number=arguments.get("phone_number", ""))

        elif tool_name == "update_contact_fact":
            from app.ai.tools import UpdateContactFactTool
            # Find the conversation object
            conv = db.session.execute(
                select(Conversation)
                .where(Conversation.contact_phone == arguments.get("phone_number", ""))
                .order_by(Conversation.created_at.desc())
                .limit(1)
            ).scalar_one_or_none()
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
