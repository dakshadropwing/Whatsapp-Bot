"""
TicketTool — create and query support tickets.

Creates ``Ticket`` rows in PostgreSQL.  The caller (agent) is responsible
for committing the transaction — this tool only ``flush()``es to obtain
the generated UUID.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Optional

from sqlalchemy import select

from app.ai.tools.base_tool import BaseTool
from app.models.ticket import Ticket, TicketPriority, TicketStatus

logger = logging.getLogger(__name__)


class TicketTool(BaseTool):
    """Create a new support ticket for a customer issue."""

    name = "create_ticket"
    description = (
        "Create a new support ticket when a customer has an issue that "
        "cannot be resolved immediately.  Returns the new ticket ID and status."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "description": "Short one-line summary of the issue.",
            },
            "description": {
                "type": "string",
                "description": "Full description of the customer's problem.",
            },
            "priority": {
                "type": "string",
                "enum": ["low", "medium", "high", "urgent"],
                "description": "How urgent the issue is.",
            },
        },
        "required": ["title", "description", "priority"],
    }

    def __init__(
        self,
        db_session: Any,
        organization_id: uuid.UUID,
        conversation_id: Optional[uuid.UUID] = None,
        contact_phone: Optional[str] = None,
        contact_name: Optional[str] = None,
    ) -> None:
        self._db = db_session
        self._org_id = organization_id
        self._conv_id = conversation_id
        self._contact_phone = contact_phone
        self._contact_name = contact_name

    async def execute(
        self,
        title: str,
        description: str,
        priority: str = "medium",
        **_: Any,
    ) -> dict:
        # Validate priority value against the enum
        try:
            priority_enum = TicketPriority(priority)
        except ValueError:
            priority_enum = TicketPriority.MEDIUM

        ticket = Ticket(
            organization_id=self._org_id,
            conversation_id=self._conv_id,
            title=title,
            description=description,
            priority=priority_enum,
            status=TicketStatus.OPEN,
            contact_phone=self._contact_phone,
            contact_name=self._contact_name,
        )
        self._db.add(ticket)
        self._db.flush()  # get the ID; caller commits the transaction

        logger.info(
            "TicketTool: created ticket=%s priority=%s org=%s",
            ticket.id,
            priority,
            self._org_id,
        )
        return {
            "ticket_id": str(ticket.id),
            "status": "open",
            "priority": priority,
            "title": title,
        }


class GetTicketStatusTool(BaseTool):
    """Look up the current status of a support ticket by its ID."""

    name = "get_ticket_status"
    description = "Get the current status, priority, and title of a support ticket by its ID."
    parameters_schema = {
        "type": "object",
        "properties": {
            "ticket_id": {
                "type": "string",
                "description": "UUID of the ticket to look up.",
            },
        },
        "required": ["ticket_id"],
    }

    def __init__(self, db_session: Any) -> None:
        self._db = db_session

    async def execute(self, ticket_id: str, **_: Any) -> dict:
        try:
            tid = uuid.UUID(ticket_id)
        except ValueError:
            return {"found": False, "error": "Invalid ticket ID format.", "ticket_id": ticket_id}

        result = self._db.execute(
            select(Ticket).where(Ticket.id == tid)
        ).scalar_one_or_none()

        if not result:
            return {"found": False, "ticket_id": ticket_id}

        return {
            "found": True,
            "ticket_id": str(result.id),
            "title": result.title,
            "status": result.status.value,
            "priority": result.priority.value,
        }
