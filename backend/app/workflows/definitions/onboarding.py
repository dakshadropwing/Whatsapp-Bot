"""
Onboarding Workflow Template definition.
"""
from __future__ import annotations

from typing import Any


def get_definition() -> dict[str, Any]:
    """Return the workflow definition for onboarding new users or customers."""
    return {
        "name": "Customer Onboarding Sequence",
        "description": "Sends welcoming instructions and collects registration parameters.",
        "trigger": "signup",
        "trigger_config": {},
        "steps": [
            {
                "action": "send_message",
                "payload": {
                    "body": "Welcome aboard! We are excited to help you get started. First, let's complete your profile configuration.",
                },
            },
            {
                "action": "wait",
                "payload": {"duration_seconds": 1800},
            },
        ],
    }
