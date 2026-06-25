"""
Lead Qualification Workflow Template definition.
"""
from __future__ import annotations

from typing import Any


def get_definition() -> dict[str, Any]:
    """Return the workflow definition for identifying and qualifying prospects."""
    return {
        "name": "Lead Qualification",
        "description": "Qualifies incoming user query leads by asking standard qualification questions.",
        "trigger": "first_contact",
        "trigger_config": {},
        "steps": [
            {
                "action": "update_context",
                "payload": {"intent": "qualify_lead", "lead_status": "new"},
            },
            {
                "action": "send_message",
                "payload": {
                    "body": "Welcome! To better understand your requirements, may I know what business size or industry you represent?",
                },
            },
            {
                "action": "wait",
                "payload": {"duration_seconds": 7200},
            },
        ],
    }
