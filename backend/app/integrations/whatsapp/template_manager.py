"""
Template Manager Integration — compiles and validates Meta WhatsApp message template payloads.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def build_template_payload(
    template_name: str,
    language_code: str = "en_US",
    components: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Format a template message payload for the WhatsApp Cloud API.

    Args:
        template_name: The registered template name (e.g., 'hello_world').
        language_code: The code of the template language (e.g., 'en_US').
        components: List of template parameters (header, body, buttons).

    Returns:
        dict: Standardised template payload.
    """
    payload: dict[str, Any] = {
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": language_code},
        },
    }

    if components:
        payload["template"]["components"] = components

    return payload


def build_text_parameter(text: str) -> dict[str, str]:
    """Helper to build a text parameter for template bodies or headers."""
    return {"type": "text", "text": text}


def build_currency_parameter(amount_1000: int, code: str) -> dict[str, Any]:
    """Helper to build a currency parameter."""
    return {
        "type": "currency",
        "currency": {
            "fallback_value": str(amount_1000 / 1000.0),
            "code": code,
            "amount_1000": amount_1000,
        },
    }


def build_date_time_parameter(fallback_value: str) -> dict[str, Any]:
    """Helper to build a date_time parameter."""
    return {
        "type": "date_time",
        "date_time": {"fallback_value": fallback_value},
    }
