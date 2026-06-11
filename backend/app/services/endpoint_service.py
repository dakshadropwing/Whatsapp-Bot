"""
Endpoint Service — dynamic external webhook dispatcher.

Looks up user-configured EndpointConfig records and dispatches HTTP
requests to those external systems on behalf of AI agents.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

import requests
from sqlalchemy import select

from app.extensions import db
from app.models.endpoint_config import EndpointConfig
from app.services.encryption_service import EncryptionService

logger = logging.getLogger(__name__)

# Timeouts for external calls (connect, read) in seconds.
REQUEST_TIMEOUT = (5, 15)


class EndpointService:
    """Resolves org-specific endpoints and fires HTTP requests to them."""

    @staticmethod
    def get_active_endpoints(org_id: str) -> list[EndpointConfig]:
        """Return all active endpoint configs for an organization."""
        return (
            db.session.execute(
                select(EndpointConfig).where(
                    EndpointConfig.organization_id == org_id,
                    EndpointConfig.is_active.is_(True),
                )
            )
            .scalars()
            .all()
        )

    @staticmethod
    def find_endpoint_by_name(org_id: str, name: str) -> Optional[EndpointConfig]:
        """Look up a single endpoint config by org + name."""
        return db.session.execute(
            select(EndpointConfig).where(
                EndpointConfig.organization_id == org_id,
                EndpointConfig.name == name,
                EndpointConfig.is_active.is_(True),
            )
        ).scalar_one_or_none()

    @classmethod
    def dispatch(
        cls,
        org_id: str,
        endpoint_name: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Fire an HTTP request to the named endpoint for the given organization.

        Args:
            org_id: Organization UUID string.
            endpoint_name: Logical name of the endpoint (e.g. "crm_update").
            payload: JSON-serialisable request body.

        Returns:
            A dict with ``status_code``, ``body``, and ``success`` keys.

        Raises:
            ValueError: If the endpoint is not found or inactive.
        """
        endpoint = cls.find_endpoint_by_name(org_id, endpoint_name)
        if not endpoint:
            raise ValueError(
                f"Endpoint '{endpoint_name}' not found for org '{org_id}'"
            )

        # Decrypt any encrypted header values
        headers = dict(endpoint.headers)
        for key, value in headers.items():
            if isinstance(value, str) and value.startswith("enc:"):
                try:
                    headers[key] = EncryptionService.decrypt(value[4:])
                except Exception:
                    logger.error(
                        "Failed to decrypt header '%s' for endpoint %s",
                        key,
                        endpoint.id,
                    )

        try:
            response = requests.request(
                method=endpoint.method.upper(),
                url=endpoint.url,
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
            result = {
                "status_code": response.status_code,
                "body": response.text[:2000],  # Cap response body
                "success": 200 <= response.status_code < 300,
            }
            logger.info(
                "Dispatched %s to %s → %s",
                endpoint.method,
                endpoint.url,
                result["status_code"],
            )
            return result

        except requests.RequestException as exc:
            logger.error(
                "Endpoint dispatch failed for %s (%s): %s",
                endpoint_name,
                endpoint.url,
                exc,
            )
            return {
                "status_code": 0,
                "body": str(exc),
                "success": False,
            }
