"""
WhatsApp Business Cloud API client.
Handles all outbound API calls to Meta's Graph API.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config.settings import get_settings

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """
    Thin wrapper around the WhatsApp Business Cloud REST API.
    All methods are async and return the raw JSON response.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.access_token = settings.WHATSAPP_ACCESS_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.api_version = settings.WHATSAPP_API_VERSION
        self.base_url = (
            f"{settings.WHATSAPP_API_BASE_URL}/{self.api_version}"
        )
        self._http = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
        )

    # ── Send Messages ─────────────────────────────────────────

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def send_text(self, to: str, body: str) -> dict:
        """Send a plain text message."""
        return await self._post(
            f"{self.base_url}/{self.phone_number_id}/messages",
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "text",
                "text": {"preview_url": False, "body": body},
            },
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def send_template(
        self,
        to: str,
        template_name: str,
        language_code: str = "en_US",
        components: Optional[list] = None,
    ) -> dict:
        """Send a pre-approved WhatsApp Template message."""
        payload: dict[str, Any] = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
            },
        }
        if components:
            payload["template"]["components"] = components
        return await self._post(
            f"{self.base_url}/{self.phone_number_id}/messages", payload
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def send_interactive_buttons(
        self, to: str, body_text: str, buttons: list[dict]
    ) -> dict:
        """Send an interactive message with reply buttons (max 3)."""
        return await self._post(
            f"{self.base_url}/{self.phone_number_id}/messages",
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": body_text},
                    "action": {"buttons": buttons},
                },
            },
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def send_interactive_list(
        self,
        to: str,
        header_text: str,
        body_text: str,
        button_text: str,
        sections: list[dict],
    ) -> dict:
        """Send an interactive list message."""
        return await self._post(
            f"{self.base_url}/{self.phone_number_id}/messages",
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "header": {"type": "text", "text": header_text},
                    "body": {"text": body_text},
                    "action": {"button": button_text, "sections": sections},
                },
            },
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def send_media(
        self,
        to: str,
        media_type: str,
        media_url: str,
        caption: Optional[str] = None,
    ) -> dict:
        """Send image / video / audio / document from URL."""
        media_payload: dict[str, Any] = {"link": media_url}
        if caption:
            media_payload["caption"] = caption
        return await self._post(
            f"{self.base_url}/{self.phone_number_id}/messages",
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": media_type,
                media_type: media_payload,
            },
        )

    async def mark_as_read(self, message_id: str) -> dict:
        """Mark a received message as read (shows double blue ticks)."""
        return await self._post(
            f"{self.base_url}/{self.phone_number_id}/messages",
            {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id,
            },
        )

    async def get_media_url(self, media_id: str) -> str:
        """Resolve a media ID to a download URL."""
        resp = await self._http.get(f"{self.base_url}/{media_id}")
        resp.raise_for_status()
        return resp.json()["url"]

    # ── Private Helpers ────────────────────────────────────────

    async def _post(self, url: str, payload: dict) -> dict:
        try:
            response = await self._http.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "WhatsApp API error",
                extra={"status": exc.response.status_code, "body": exc.response.text},
            )
            raise

    async def close(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> "WhatsAppClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()
