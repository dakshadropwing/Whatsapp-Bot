"""
Analytics Service — dashboard stats, charts, and reporting.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func, select

from app.extensions import db
from app.models.conversation import Conversation, ConversationStatus
from app.models.message import Message, MessageDirection
from app.models.ticket import Ticket, TicketStatus

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Computes KPIs and chart data for the admin dashboard."""

    @staticmethod
    def get_stats(org_id: str) -> dict:
        """Return dashboard KPI stats for an organization."""
        oid = uuid.UUID(org_id)
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        total_conv = db.session.execute(
            select(func.count()).select_from(Conversation).where(Conversation.organization_id == oid)
        ).scalar() or 0

        active_conv = db.session.execute(
            select(func.count()).select_from(Conversation).where(
                Conversation.organization_id == oid,
                Conversation.status.in_([
                    ConversationStatus.ACTIVE, ConversationStatus.WAITING,
                    ConversationStatus.BOT_HANDLING, ConversationStatus.HUMAN_HANDLING,
                ]),
            )
        ).scalar() or 0

        messages_today = db.session.execute(
            select(func.count()).select_from(Message).where(
                Message.organization_id == oid, Message.created_at >= today,
            )
        ).scalar() or 0

        avg_response = db.session.execute(
            select(func.avg(Message.processing_time_ms)).where(
                Message.organization_id == oid,
                Message.processing_time_ms.isnot(None),
                Message.ai_generated.is_(True),
            )
        ).scalar() or 0

        tickets_open = db.session.execute(
            select(func.count()).select_from(Ticket).where(
                Ticket.organization_id == oid,
                Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]),
            )
        ).scalar() or 0

        tickets_resolved = db.session.execute(
            select(func.count()).select_from(Ticket).where(
                Ticket.organization_id == oid,
                Ticket.status == TicketStatus.RESOLVED,
                Ticket.updated_at >= today,
            )
        ).scalar() or 0

        ai_msgs = db.session.execute(
            select(func.count()).select_from(Message).where(
                Message.organization_id == oid, Message.ai_generated.is_(True),
            )
        ).scalar() or 0
        total_msgs = db.session.execute(
            select(func.count()).select_from(Message).where(Message.organization_id == oid)
        ).scalar() or 0
        ai_rate = round((ai_msgs / total_msgs * 100), 1) if total_msgs > 0 else 0

        return {
            "total_conversations": total_conv,
            "active_conversations": active_conv,
            "messages_today": messages_today,
            "avg_response_time_ms": round(float(avg_response), 0),
            "tickets_open": tickets_open,
            "tickets_resolved_today": tickets_resolved,
            "ai_resolution_rate": ai_rate,
            "customer_satisfaction": 0,
        }

    @staticmethod
    def get_overview(org_id: str, period: str = "7d") -> dict:
        """Return chart-ready data for the analytics overview."""
        oid = uuid.UUID(org_id)
        days = int(period.replace("d", "")) if "d" in period else 7
        since = datetime.now(timezone.utc) - timedelta(days=days)

        # Messages by day
        msg_by_day = db.session.execute(
            select(
                func.date(Message.created_at).label("label"),
                func.count().label("value"),
            )
            .where(Message.organization_id == oid, Message.created_at >= since)
            .group_by(func.date(Message.created_at))
            .order_by(func.date(Message.created_at))
        ).all()

        # Conversations by status
        conv_by_status = db.session.execute(
            select(
                Conversation.status.label("label"),
                func.count().label("value"),
            )
            .where(Conversation.organization_id == oid)
            .group_by(Conversation.status)
        ).all()

        return {
            "messages_by_day": [{"label": str(r.label), "value": r.value} for r in msg_by_day],
            "conversations_by_status": [{"label": r.label.value if r.label else "unknown", "value": r.value} for r in conv_by_status],
            "agent_usage": [],
            "response_times": [],
        }

    @staticmethod
    def get_messages_by_day(org_id: str, days: int = 30) -> list[dict]:
        oid = uuid.UUID(org_id)
        since = datetime.now(timezone.utc) - timedelta(days=days)
        rows = db.session.execute(
            select(func.date(Message.created_at).label("day"), func.count().label("count"))
            .where(Message.organization_id == oid, Message.created_at >= since)
            .group_by(func.date(Message.created_at))
            .order_by(func.date(Message.created_at))
        ).all()
        return [{"day": str(r.day), "count": r.count} for r in rows]

    @staticmethod
    def get_agent_usage(org_id: str) -> list[dict]:
        oid = uuid.UUID(org_id)
        rows = db.session.execute(
            select(Conversation.assigned_agent_id, func.count().label("count"))
            .where(Conversation.organization_id == oid, Conversation.assigned_agent_id.isnot(None))
            .group_by(Conversation.assigned_agent_id)
        ).all()
        return [{"agent_id": str(r.assigned_agent_id), "count": r.count} for r in rows]

    @staticmethod
    def get_response_times(org_id: str) -> dict:
        oid = uuid.UUID(org_id)
        avg_ms = db.session.execute(
            select(func.avg(Message.processing_time_ms)).where(
                Message.organization_id == oid, Message.processing_time_ms.isnot(None),
            )
        ).scalar() or 0
        return {"avg_response_time_ms": round(float(avg_ms), 0)}
