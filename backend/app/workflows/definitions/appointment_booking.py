"""
Appointment Booking Workflow Template definition.
"""
from __future__ import annotations

from typing import Any


def get_definition() -> dict[str, Any]:
    """Return the workflow definition for booking appointments."""
    return {
        "name": "Appointment Booking Workflow",
        "description": "Guides contacts through booking an appointment after matching request keywords.",
        "trigger": "message_received",
        "trigger_config": {
            "keywords": ["book", "appointment", "schedule", "reserve"],
        },
        "steps": [
            {
                "action": "update_context",
                "payload": {"intent": "book_appointment", "current_stage": "ask_time"},
            },
            {
                "action": "send_message",
                "payload": {
                    "body": "Sure! I can help you book an appointment. What date and time works best for you?",
                },
            },
            {
                "action": "wait",
                "payload": {"duration_seconds": 3600},
            },
        ],
    }
