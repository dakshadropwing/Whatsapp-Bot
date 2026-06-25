"""
OAuth configuration and token exchange utilities.
"""
from __future__ import annotations

import logging

import requests

from app.core.config.settings import get_settings

logger = logging.getLogger(__name__)


def exchange_meta_token(code: str, redirect_uri: str) -> dict | None:
    """
    Exchange Meta authorization code for short-lived access token.
    """
    settings = get_settings()
    url = "https://graph.facebook.com/v19.0/oauth/access_token"
    params = {
        "client_id": settings.META_APP_ID if hasattr(settings, "META_APP_ID") else "",
        "client_secret": settings.META_APP_SECRET if hasattr(settings, "META_APP_SECRET") else "",
        "redirect_uri": redirect_uri,
        "code": code,
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        logger.error("Meta token exchange failed: %s", response.text)
    except Exception:
        logger.exception("Error exchanging Meta oauth token")
    return None
