"""
Calendar Tools — appointment availability and booking.

Provider-agnostic design:  the private ``_fetch_slots()`` and booking
logic can be backed by Google Calendar API, Calendly, Cal.com, or any
custom system.  The current implementation returns deterministic stub
data so the rest of the agent pipeline can be tested end-to-end without
an external calendar service.

When you're ready to integrate a real provider, replace only the private
methods — the tool schema and ``execute()`` signature stay the same.
"""
from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

from app.ai.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class CheckAvailabilityTool(BaseTool):
    """Check available appointment slots for the next N days."""

    name = "check_calendar_availability"
    description = (
        "Check available appointment slots for the next N days.  "
        "Use when a customer wants to schedule a meeting, demo, or callback."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "days_ahead": {
                "type": "integer",
                "description": "How many days ahead to check (default: 3, max: 14).",
            },
        },
        "required": [],
    }

    async def execute(self, days_ahead: int = 3, **_: Any) -> dict:
        # Clamp to a reasonable range
        days_ahead = max(1, min(days_ahead, 14))

        slots = await self._fetch_slots(days_ahead)
        return {
            "available_slots": slots,
            "days_checked": days_ahead,
        }

    async def _fetch_slots(self, days_ahead: int) -> list[dict]:
        """
        Fetch available slots from the calendar backend.

        TODO: Replace with real API integration:
            - Google Calendar: use ``google-api-python-client`` with OAuth2
            - Calendly: use ``httpx`` to call Calendly v2 REST API
            - Cal.com: use ``httpx`` to call Cal.com API

        Returns a list of slot dicts with ``date``, ``time``, ``slot_id``.
        """
        today = date.today()
        slots: list[dict] = []

        for i in range(1, days_ahead + 1):
            day = today + timedelta(days=i)
            day_str = day.strftime("%A, %B %d, %Y")  # e.g. "Monday, June 10, 2026"
            day_iso = day.isoformat()

            # Stub: two slots per day
            for time, slot_suffix in [("10:00 AM", "morning"), ("3:00 PM", "afternoon")]:
                slots.append({
                    "date": day_str,
                    "date_iso": day_iso,
                    "time": time,
                    "slot_id": f"{day_iso}_{slot_suffix}",
                })

        return slots


class BookAppointmentTool(BaseTool):
    """Book an appointment slot for the customer."""

    name = "book_appointment"
    description = (
        "Book a specific appointment slot for a customer.  "
        "Always call ``check_calendar_availability`` first to get "
        "available slot_ids, then pass the chosen slot_id here."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "slot_id": {
                "type": "string",
                "description": (
                    "The slot_id from check_calendar_availability results."
                ),
            },
            "contact_name": {
                "type": "string",
                "description": "Customer's name for the booking.",
            },
            "contact_phone": {
                "type": "string",
                "description": "Customer's phone in E.164 format.",
            },
            "notes": {
                "type": "string",
                "description": "Optional notes or agenda for the appointment.",
            },
        },
        "required": ["slot_id", "contact_name", "contact_phone"],
    }

    async def execute(
        self,
        slot_id: str,
        contact_name: str,
        contact_phone: str,
        notes: str = "",
        **_: Any,
    ) -> dict:
        """
        Book the appointment.

        TODO: Replace with real API call to your calendar provider.
        """
        logger.info(
            "BookAppointmentTool: slot=%s name=%s phone=%s",
            slot_id,
            contact_name,
            contact_phone,
        )

        # Stub: always succeeds.  In production, handle conflicts / errors.
        confirmation_id = f"APPT-{contact_phone[-4:]}-{slot_id[:10]}"

        return {
            "booked": True,
            "slot_id": slot_id,
            "contact_name": contact_name,
            "confirmation_id": confirmation_id,
            "notes": notes,
        }
