"""
Ticket Repository — support ticket queries and lifecycle management.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select

from app.extensions import db
from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.repositories.base_repository import BaseRepository


class TicketRepository(BaseRepository[Ticket]):
    """Specialised repository for Ticket entity queries."""

    def __init__(self) -> None:
        super().__init__(Ticket)

    def find_by_organization(
        self,
        org_id: str,
        status: Optional[TicketStatus] = None,
        priority: Optional[TicketPriority] = None,
    ) -> list[Ticket]:
        """Return tickets for an org with optional status/priority filter."""
        query = select(Ticket).where(
            Ticket.organization_id == org_id,
            Ticket.deleted_at.is_(None),
        )
        if status:
            query = query.where(Ticket.status == status)
        if priority:
            query = query.where(Ticket.priority == priority)
        query = query.order_by(Ticket.created_at.desc())
        return db.session.execute(query).scalars().all()

    def find_by_conversation(self, conversation_id: str) -> list[Ticket]:
        """Return all tickets linked to a conversation."""
        return (
            db.session.execute(
                select(Ticket)
                .where(
                    Ticket.conversation_id == conversation_id,
                    Ticket.deleted_at.is_(None),
                )
                .order_by(Ticket.created_at.desc())
            )
            .scalars()
            .all()
        )

    def find_by_assignee(self, user_id: str) -> list[Ticket]:
        """Return open/in-progress tickets assigned to a user."""
        return (
            db.session.execute(
                select(Ticket)
                .where(
                    Ticket.assigned_user_id == user_id,
                    Ticket.deleted_at.is_(None),
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

    def count_open_by_organization(self, org_id: str) -> int:
        """Count open + in-progress tickets for an org."""
        result = db.session.execute(
            select(func.count())
            .select_from(Ticket)
            .where(
                Ticket.organization_id == org_id,
                Ticket.deleted_at.is_(None),
                Ticket.status.in_([
                    TicketStatus.OPEN,
                    TicketStatus.IN_PROGRESS,
                    TicketStatus.WAITING_ON_CUSTOMER,
                ]),
            )
        ).scalar()
        return result or 0

    def count_by_status(self, org_id: str) -> dict:
        """Return ticket counts grouped by status for an org."""
        rows = db.session.execute(
            select(Ticket.status, func.count().label("cnt"))
            .where(Ticket.organization_id == org_id, Ticket.deleted_at.is_(None))
            .group_by(Ticket.status)
        ).all()
        return {str(row.status.value if hasattr(row.status, "value") else row.status): row.cnt for row in rows}
