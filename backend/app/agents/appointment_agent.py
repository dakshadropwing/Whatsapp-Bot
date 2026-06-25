"""
Appointment Agent — handles checking availability and booking appointments.
"""
from __future__ import annotations

import logging
from typing import Any

from app.agents.base_agent import BaseAgent
from app.integrations.whatsapp.client import WhatsAppClient
from app.ai.tools.calendar_tool import CheckAvailabilityTool, BookAppointmentTool
from app.utils.helpers import load_prompt

logger = logging.getLogger(__name__)

APPOINTMENT_SYSTEM_PROMPT = load_prompt(
    "prompts/agents/appointment_agent.md",
    default=(
        "You are Aria, a friendly scheduling assistant.\n"
        "Your goal is to help users check availability, book, reschedule, or cancel appointments.\n"
        "Use check_calendar_availability to check slot availability and book_appointment to confirm slots."
    )
)


class AppointmentAgent(BaseAgent):
    agent_name = "appointment"
    system_prompt = APPOINTMENT_SYSTEM_PROMPT

    def _register_tools(self) -> list[dict]:
        self._register_tool(CheckAvailabilityTool())
        self._register_tool(BookAppointmentTool())
        return self._get_tool_schemas()

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
                "[AppointmentAgent] Error handling message from %s",
                from_number,
                exc_info=exc,
            )
