"""
Ticket Service — ticket workflows & human escalation alerts.
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from app.extensions import db
from app.models.ticket import Ticket, TicketPriority, TicketStatus

logger = logging.getLogger(__name__)


class TicketService:
    """Manages support ticket lifecycle — creation, assignment, status transitions."""

    @staticmethod
    def create_support_ticket(
        org_id: str,
        title: str,
        description: str,
        priority: str = "medium",
        phone: Optional[str] = None,
        name: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> Ticket:
        """
        Create a new support ticket.

        Args:
            org_id: Organization UUID string.
            title: Short summary of the issue.
            description: Detailed problem description.
            priority: One of 'low', 'medium', 'high', 'urgent'.
            phone: Contact phone number (if from a WhatsApp conversation).
            name: Contact display name.
            conversation_id: Optional linked conversation UUID.

        Returns:
            The newly created and persisted Ticket instance.
        """
        ticket = Ticket(
            organization_id=uuid.UUID(org_id),
            title=title,
            description=description,
            priority=TicketPriority(priority),
            status=TicketStatus.OPEN,
            contact_phone=phone,
            contact_name=name,
            conversation_id=uuid.UUID(conversation_id) if conversation_id else None,
        )
        db.session.add(ticket)
        db.session.commit()
        logger.info("Created support ticket %s for org %s", ticket.id, org_id)
        return ticket

    @staticmethod
    def update_ticket_status(
        ticket_id: str, new_status: str, assigned_user_id: Optional[str] = None
    ) -> Optional[Ticket]:
        """
        Transition a ticket to a new status and optionally reassign it.

        Returns:
            The updated Ticket, or None if not found.
        """
        ticket = db.session.get(Ticket, uuid.UUID(ticket_id))
        if not ticket:
            logger.warning("Ticket %s not found", ticket_id)
            return None

        ticket.status = TicketStatus(new_status)
        if assigned_user_id:
            ticket.assigned_user_id = uuid.UUID(assigned_user_id)
        db.session.commit()
        logger.info("Ticket %s → %s", ticket.id, new_status)
        return ticket

    @staticmethod
    def get_open_tickets(org_id: str) -> list[Ticket]:
        """Return all open / in-progress tickets for an organization."""
        from sqlalchemy import select

        return (
            db.session.execute(
                select(Ticket)
                .where(
                    Ticket.organization_id == uuid.UUID(org_id),
                    Ticket.status.in_([
                        TicketStatus.OPEN,
                        TicketStatus.IN_PROGRESS,
                        TicketStatus.WAITING_ON_CUSTOMER,
                    ]),
                )
                .order_by(Ticket.created_at.desc())
            )
            .scalars()
            .all()
        )
