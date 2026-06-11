"""
Tickets routes — CRUD + status management.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

tickets_bp = Blueprint("tickets", __name__)


@tickets_bp.get("/")
@jwt_required()
def list_tickets():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    # TODO: TicketService.list(org_id, filters, page, per_page)
    return jsonify({"data": [], "total": 0, "page": page, "per_page": per_page, "total_pages": 0}), 200


@tickets_bp.get("/<ticket_id>")
@jwt_required()
def get_ticket(ticket_id: str):
    # TODO: TicketService.get(ticket_id)
    return jsonify({"ticket": {"id": ticket_id}}), 200


@tickets_bp.post("/")
@jwt_required()
def create_ticket():
    data = request.get_json(silent=True) or {}
    # TODO: TicketService.create(data)
    return jsonify({"id": "new", **data}), 201


@tickets_bp.patch("/<ticket_id>")
@jwt_required()
def update_ticket(ticket_id: str):
    data = request.get_json(silent=True) or {}
    # TODO: TicketService.update(ticket_id, data)
    return jsonify({"id": ticket_id, "updated": True}), 200


@tickets_bp.patch("/<ticket_id>/status")
@jwt_required()
def update_ticket_status(ticket_id: str):
    data = request.get_json(silent=True) or {}
    # TODO: TicketService.update_status(ticket_id, data.get("status"))
    return jsonify({"id": ticket_id, "status": data.get("status"), "updated": True}), 200
