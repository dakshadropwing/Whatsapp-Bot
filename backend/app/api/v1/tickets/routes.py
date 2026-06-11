"""
Tickets routes — CRUD + status management.
"""
from __future__ import annotations

import uuid
from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required
from sqlalchemy import select, func

from app.extensions import db
from app.models.ticket import Ticket, TicketPriority, TicketStatus
from app.services.ticket_service import TicketService

tickets_bp = Blueprint("tickets", __name__)


@tickets_bp.get("/")
@jwt_required()
def list_tickets():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    status = request.args.get("status")
    priority = request.args.get("priority")
    search = request.args.get("search")

    query = select(Ticket).where(Ticket.organization_id == uuid.UUID(org_id))

    if status:
        try:
            query = query.where(Ticket.status == TicketStatus(status))
        except ValueError:
            pass
    if priority:
        try:
            query = query.where(Ticket.priority == TicketPriority(priority))
        except ValueError:
            pass
    if search:
        term = f"%{search.lower()}%"
        query = query.where(
            db.or_(
                func.lower(Ticket.title).like(term),
                func.lower(Ticket.description).like(term),
                func.lower(Ticket.contact_name).like(term),
                Ticket.contact_phone.like(term),
            )
        )

    total = db.session.execute(
        select(func.count()).select_from(query.subquery())
    ).scalar() or 0

    tickets = (
        db.session.execute(
            query.order_by(Ticket.created_at.desc())
            .offset((page - 1) * per_page)
            .limit(per_page)
        )
        .scalars()
        .all()
    )

    return jsonify({
        "data": [
            {
                "id": str(t.id),
                "organization_id": str(t.organization_id),
                "conversation_id": str(t.conversation_id) if t.conversation_id else None,
                "assigned_user_id": str(t.assigned_user_id) if t.assigned_user_id else None,
                "title": t.title,
                "description": t.description,
                "status": t.status.value,
                "priority": t.priority.value,
                "contact_phone": t.contact_phone,
                "contact_name": t.contact_name,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "updated_at": t.updated_at.isoformat() if t.updated_at else None,
            }
            for t in tickets
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }), 200


@tickets_bp.get("/<ticket_id>")
@jwt_required()
def get_ticket(ticket_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    ticket = db.session.get(Ticket, uuid.UUID(ticket_id))
    if not ticket or str(ticket.organization_id) != org_id:
        return jsonify({"error": "Ticket not found"}), 404

    return jsonify({
        "ticket": {
            "id": str(ticket.id),
            "organization_id": str(ticket.organization_id),
            "conversation_id": str(ticket.conversation_id) if ticket.conversation_id else None,
            "assigned_user_id": str(ticket.assigned_user_id) if ticket.assigned_user_id else None,
            "title": ticket.title,
            "description": ticket.description,
            "status": ticket.status.value,
            "priority": ticket.priority.value,
            "contact_phone": ticket.contact_phone,
            "contact_name": ticket.contact_name,
            "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
            "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
        }
    }), 200


@tickets_bp.post("/")
@jwt_required()
def create_ticket():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    data = request.get_json(silent=True) or {}
    title = data.get("title")
    description = data.get("description", "")
    priority = data.get("priority", "medium")
    phone = data.get("contact_phone")
    name = data.get("contact_name")
    conversation_id = data.get("conversation_id")

    if not title:
        return jsonify({"error": "title is required"}), 400

    ticket = TicketService.create_support_ticket(
        org_id=org_id,
        title=title,
        description=description,
        priority=priority,
        phone=phone,
        name=name,
        conversation_id=conversation_id
    )

    return jsonify({
        "id": str(ticket.id),
        "organization_id": str(ticket.organization_id),
        "title": ticket.title,
        "status": ticket.status.value,
        "priority": ticket.priority.value,
    }), 201


@tickets_bp.patch("/<ticket_id>")
@jwt_required()
def update_ticket(ticket_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    ticket = db.session.get(Ticket, uuid.UUID(ticket_id))
    if not ticket or str(ticket.organization_id) != org_id:
        return jsonify({"error": "Ticket not found"}), 404

    data = request.get_json(silent=True) or {}
    for key, value in data.items():
        if hasattr(ticket, key) and key not in ("id", "organization_id"):
            if key == "status" and isinstance(value, str):
                try:
                    value = TicketStatus(value)
                except ValueError:
                    continue
            elif key == "priority" and isinstance(value, str):
                try:
                    value = TicketPriority(value)
                except ValueError:
                    continue
            elif key in ("assigned_user_id", "conversation_id") and isinstance(value, str):
                value = uuid.UUID(value) if value else None
            setattr(ticket, key, value)
            
    db.session.commit()
    return jsonify({"id": str(ticket.id), "updated": True}), 200


@tickets_bp.patch("/<ticket_id>/status")
@jwt_required()
def update_ticket_status(ticket_id: str):
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    ticket = db.session.get(Ticket, uuid.UUID(ticket_id))
    if not ticket or str(ticket.organization_id) != org_id:
        return jsonify({"error": "Ticket not found"}), 404

    data = request.get_json(silent=True) or {}
    status = data.get("status")
    assigned_user_id = data.get("assigned_user_id")

    if not status:
        return jsonify({"error": "status is required"}), 400

    updated_ticket = TicketService.update_ticket_status(
        ticket_id=ticket_id,
        new_status=status,
        assigned_user_id=assigned_user_id
    )

    if not updated_ticket:
        return jsonify({"error": "Failed to update ticket status"}), 400

    return jsonify({"id": str(updated_ticket.id), "status": updated_ticket.status.value, "updated": True}), 200
