"""
Analytics routes — dashboard stats, overview, and chart data.
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.get("/stats")
@jwt_required()
def get_stats():
    """Dashboard KPI stats."""
    # TODO: AnalyticsService.get_stats(org_id)
    return jsonify({
        "total_conversations": 0,
        "active_conversations": 0,
        "messages_today": 0,
        "avg_response_time_ms": 0,
        "tickets_open": 0,
        "tickets_resolved_today": 0,
        "ai_resolution_rate": 0,
        "customer_satisfaction": 0,
    }), 200


@analytics_bp.get("/overview")
@jwt_required()
def get_overview():
    """Full analytics overview with chart data."""
    period = request.args.get("period", "7d")
    # TODO: AnalyticsService.get_overview(org_id, period)
    return jsonify({
        "messages_by_day": [],
        "conversations_by_status": [],
        "agent_usage": [],
        "response_times": [],
    }), 200


@analytics_bp.get("/messages-by-day")
@jwt_required()
def get_messages_by_day():
    days = int(request.args.get("days", 30))
    # TODO: AnalyticsService.messages_by_day(org_id, days)
    return jsonify({"data": []}), 200


@analytics_bp.get("/agent-usage")
@jwt_required()
def get_agent_usage():
    # TODO: AnalyticsService.agent_usage(org_id)
    return jsonify({"data": []}), 200


@analytics_bp.get("/response-times")
@jwt_required()
def get_response_times():
    # TODO: AnalyticsService.response_times(org_id)
    return jsonify({"data": []}), 200


@analytics_bp.get("/")
@jwt_required()
def list_analytics():
    return jsonify({"data": []}), 200
