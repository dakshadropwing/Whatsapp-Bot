"""
Follow-up Workflow Template definition.
"""
from __future__ import annotations

from typing import Any


def get_definition() -> dict[str, Any]:
    """Return the workflow definition for following up with inactive contacts."""
    return {
        "name": "Inactive Contact Follow-up",
        "description": "Sends a sequence of messages to re-engage inactive contacts.",
        "trigger": "conversation_idle",
        "trigger_config": {
            "idle_hours": 24,
        },
        "steps": [
            {
                "action": "send_message",
                "payload": {
                    "body": "Hi there! Just checking in to see if you have any other questions for us today.",
                },
            },
            {
                "action": "wait",
                "payload": {"duration_seconds": 86400},
            },
            {
                "action": "send_message",
                "payload": {
                    "body": "If you are all set, we will close this thread for now. Feel free to message back anytime!",
                },
            },
        ],
    }
