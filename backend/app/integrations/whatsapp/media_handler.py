"""
Media Handler Integration — downloading and uploading media attachments via Meta Graph APIs.
"""
from __future__ import annotations

import logging
import mimetypes
import requests

from app.core.config.settings import get_settings

logger = logging.getLogger(__name__)


class MediaHandler:
    """Manages media file retrieval and storage integrations with Meta Graph API."""

    def __init__(self, access_token: str | None = None) -> None:
        settings = get_settings()
        self.access_token = access_token or settings.WHATSAPP_ACCESS_TOKEN
        self.base_url = "https://graph.facebook.com/v19.0"

    def download_media(self, media_id: str) -> dict[str, Any] | None:
        """
        Download media file from WhatsApp Cloud API using its media_id.
        Returns a dict with raw data, filename, and mime_type.
        """
        if not self.access_token:
            logger.error("Missing access token for WhatsApp Media download")
            return None

        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{self.base_url}/{media_id}"

        try:
            # 1. Fetch Meta Media metadata (retrieves the actual download URL)
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                logger.error("Failed to fetch media details for ID %s: %s", media_id, response.text)
                return None

            details = response.json()
            download_url = details.get("url")
            mime_type = details.get("mime_type", "application/octet-stream")
            file_size = details.get("file_size", 0)

            if not download_url:
                logger.error("Download URL not found in media metadata for %s", media_id)
                return None

            # 2. Download the actual binary payload
            media_response = requests.get(download_url, headers=headers, timeout=30)
            if media_response.status_code != 200:
                logger.error("Failed to download binary file for ID %s: %s", media_id, media_response.text)
                return None

            ext = mimetypes.guess_extension(mime_type) or ".bin"
            filename = f"{media_id}{ext}"

            return {
                "data": media_response.content,
                "filename": filename,
                "mime_type": mime_type,
                "size": file_size,
            }

        except Exception as exc:
            logger.exception("Exception occurred during media download for %s", media_id)
            return None

    def upload_media(
        self, phone_number_id: str, file_bytes: bytes, mime_type: str, filename: str
    ) -> str | None:
        """
        Upload binary media payload to Meta Graph APIs.
        Returns the Meta media ID string.
        """
        if not self.access_token:
            logger.error("Missing access token for WhatsApp Media upload")
            return None

        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{self.base_url}/{phone_number_id}/media"

        files = {
            "file": (filename, file_bytes, mime_type),
        }
        data = {
            "messaging_product": "whatsapp",
        }

        try:
            response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
            if response.status_code == 200:
                media_id = response.json().get("id")
                logger.info("Successfully uploaded media %s; Meta media ID: %s", filename, media_id)
                return media_id

            logger.error("Failed to upload media %s to Meta: %s", filename, response.text)
            return None

        except Exception as exc:
            logger.exception("Exception occurred during media upload for %s", filename)
            return None
