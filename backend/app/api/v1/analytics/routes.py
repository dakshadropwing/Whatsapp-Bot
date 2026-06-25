"""
Analytics routes — dashboard stats, overview, and chart data.
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import jwt_required

from app.services.analytics_service import AnalyticsService

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("/stats")
@jwt_required()
def get_stats():
    """Dashboard KPI stats."""
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    stats = AnalyticsService.get_stats(org_id)
    return jsonify(stats), 200


@analytics_bp.get("/overview")
@jwt_required()
def get_overview():
    """Full analytics overview with chart data."""
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    period = request.args.get("period", "7d")
    overview = AnalyticsService.get_overview(org_id, period)
    return jsonify(overview), 200


@analytics_bp.get("/messages-by-day")
@jwt_required()
def get_messages_by_day():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    days = int(request.args.get("days", 30))
    data = AnalyticsService.get_messages_by_day(org_id, days)
    return jsonify({"data": data}), 200


@analytics_bp.get("/agent-usage")
@jwt_required()
def get_agent_usage():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    data = AnalyticsService.get_agent_usage(org_id)
    return jsonify({"data": data}), 200


@analytics_bp.get("/response-times")
@jwt_required()
def get_response_times():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    data = AnalyticsService.get_response_times(org_id)
    return jsonify(data), 200


@analytics_bp.get("/")
@jwt_required()
def list_analytics():
    org_id = g.org_id
    if not org_id:
        return jsonify({"error": "Tenant context missing"}), 401

    overview = AnalyticsService.get_overview(org_id, "7d")
    return jsonify({"data": overview}), 200
