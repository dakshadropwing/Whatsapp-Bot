"""
Interactive Messages integration — formatting and parsing WhatsApp interactive components.
"""
from __future__ import annotations

from typing import Any


def build_button_message(
    body_text: str,
    buttons: list[dict[str, str]],
    header_text: str | None = None,
    footer_text: str | None = None,
) -> dict[str, Any]:
    """
    Format a WhatsApp Cloud API interactive button message payload.
    Buttons list should be: [{"id": "btn_1", "title": "Yes"}, ...] (Max 3 buttons).
    """
    if len(buttons) > 3:
        buttons = buttons[:3]

    interactive_payload: dict[str, Any] = {
        "type": "button",
        "body": {"text": body_text},
        "action": {
            "buttons": [
                {
                    "type": "reply",
                    "reply": {"id": b["id"], "title": b["title"]},
                }
                for b in buttons
            ]
        },
    }

    if header_text:
        interactive_payload["header"] = {"type": "text", "text": header_text}
    if footer_text:
        interactive_payload["footer"] = {"text": footer_text}

    return {"type": "interactive", "interactive": interactive_payload}


def build_list_message(
    body_text: str,
    button_label: str,
    sections: list[dict[str, Any]],
    title: str | None = None,
    footer_text: str | None = None,
) -> dict[str, Any]:
    """
    Format a WhatsApp Cloud API interactive list message payload.
    Sections should follow the structure:
        [{"title": "Section Title", "rows": [{"id": "row_1", "title": "Title", "description": "Desc"}]}]
    """
    interactive_payload: dict[str, Any] = {
        "type": "list",
        "body": {"text": body_text},
        "action": {
            "button": button_label,
            "sections": sections,
        },
    }

    if title:
        interactive_payload["header"] = {"type": "text", "text": title}
    if footer_text:
        interactive_payload["footer"] = {"text": footer_text}

    return {"type": "interactive", "interactive": interactive_payload}


def parse_interactive_reply(message_value: dict[str, Any]) -> dict[str, str] | None:
    """
    Extract the interactive reply details (id and title) from an inbound webhook message dict.
    Returns None if the message is not an interactive reply.
    """
    if message_value.get("type") != "interactive":
        return None

    interactive = message_value.get("interactive", {})
    interactive_type = interactive.get("type")

    if interactive_type == "button_reply":
        reply = interactive.get("button_reply", {})
        return {"id": reply.get("id", ""), "title": reply.get("title", "")}
    elif interactive_type == "list_reply":
        reply = interactive.get("list_reply", {})
        return {"id": reply.get("id", ""), "title": reply.get("title", "")}

    return None
