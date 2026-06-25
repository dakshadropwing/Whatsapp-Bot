"""
PII masking and data redaction utilities.
"""
from __future__ import annotations

import re

PHONE_REGEX = re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")


def redact_email(text: str) -> str:
    """Replace emails in text with [REDACTED_EMAIL]."""
    return EMAIL_REGEX.sub("[REDACTED_EMAIL]", text)


def redact_phone(text: str) -> str:
    """Replace phone numbers in text with [REDACTED_PHONE]."""
    return PHONE_REGEX.sub("[REDACTED_PHONE]", text)


def mask_pii(text: str) -> str:
    """Redact both phone numbers and email addresses from input text."""
    if not text:
        return ""
    return redact_phone(redact_email(text))
