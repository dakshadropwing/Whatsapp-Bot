"""
Support Ticket Workflow Template definition.
"""
from __future__ import annotations

from typing import Any


def get_definition() -> dict[str, Any]:
    """Return the workflow definition for opening support cases."""
    return {
        "name": "Auto Support Ticket Creation",
        "description": "Auto-creates a support ticket when a contact reports an error or issue.",
        "trigger": "message_received",
        "trigger_config": {
            "keywords": ["error", "issue", "bug", "broken", "fail", "not working"],
        },
        "steps": [
            {
                "action": "create_ticket",
                "payload": {
                    "title": "Customer Reported Issue",
                    "description": "Automated ticket created because of keyword match: bug/error.",
                },
            },
            {
                "action": "send_message",
                "payload": {
                    "body": "I have created a support ticket for this issue. A human agent will review and update you soon.",
                },
            },
        ],
    }
