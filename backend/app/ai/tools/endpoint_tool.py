"""
EndpointTool — call user-configured custom webhook endpoints.

Reads ``EndpointConfig`` rows from the database (per organization) and
makes HTTP calls using ``httpx``.  This lets non-technical users wire
up external systems (CRMs, ERPs, order managers) through the admin UI
without writing code.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Optional

import httpx
from sqlalchemy import select

from app.ai.tools.base_tool import BaseTool
from app.models.endpoint_config import EndpointConfig

logger = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 10.0  # seconds


class CallEndpointTool(BaseTool):
    """Call a configured external API endpoint by name."""

    name = "call_custom_endpoint"
    description = (
        "Call an external API endpoint that has been configured for this "
        "organization.  Use when you need to fetch data from or send data "
        "to an external system (e.g. order status, CRM update, inventory check)."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "endpoint_name": {
                "type": "string",
                "description": (
                    "Name of the configured endpoint "
                    "(e.g. 'order_status', 'crm_update', 'inventory_check')."
                ),
            },
            "payload": {
                "type": "object",
                "description": "JSON payload to send to the endpoint.",
            },
        },
        "required": ["endpoint_name", "payload"],
    }

    def __init__(
        self,
        db_session: Any,
        organization_id: uuid.UUID,
    ) -> None:
        self._db = db_session
        self._org_id = organization_id

    async def execute(
        self,
        endpoint_name: str,
        payload: Optional[dict] = None,
        **_: Any,
    ) -> dict:
        if payload is None:
            payload = {}

        config = self._load_config(endpoint_name)
        if not config:
            return {
                "error": f"Endpoint '{endpoint_name}' is not configured or inactive.",
                "endpoint": endpoint_name,
            }

        url = config["url"]
        method = config["method"]
        headers = config["headers"]

        try:
            async with httpx.AsyncClient(timeout=_DEFAULT_TIMEOUT) as client:
                if method == "GET":
                    resp = await client.get(url, params=payload, headers=headers)
                else:
                    resp = await client.request(
                        method, url, json=payload, headers=headers
                    )

                resp.raise_for_status()

                # Try to parse JSON; fall back to text
                try:
                    data = resp.json()
                except Exception:
                    data = resp.text[:2000]

                logger.info(
                    "EndpointTool: %s %s → %d",
                    method,
                    url,
                    resp.status_code,
                )
                return {
                    "success": True,
                    "status_code": resp.status_code,
                    "data": data,
                }

        except httpx.TimeoutException:
            logger.warning("EndpointTool: timeout calling %s", url)
            return {
                "error": "Request timed out.",
                "endpoint": endpoint_name,
            }
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "EndpointTool: HTTP %d from %s",
                exc.response.status_code,
                url,
            )
            return {
                "error": f"HTTP {exc.response.status_code}",
                "endpoint": endpoint_name,
                "detail": exc.response.text[:500],
            }
        except httpx.RequestError as exc:
            logger.exception("EndpointTool: connection error calling %s", url)
            return {
                "error": f"Connection error: {exc}",
                "endpoint": endpoint_name,
            }

    def _load_config(self, endpoint_name: str) -> Optional[dict]:
        """Load endpoint configuration from the database."""
        result = self._db.execute(
            select(EndpointConfig).where(
                EndpointConfig.organization_id == self._org_id,
                EndpointConfig.name == endpoint_name,
                EndpointConfig.is_active == True,  # noqa: E712
            )
        ).scalar_one_or_none()

        if not result:
            return None

        return {
            "url": result.url,
            "method": (result.method or "POST").upper(),
            "headers": result.headers or {},
        }
