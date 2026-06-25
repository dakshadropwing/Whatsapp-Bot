from __future__ import annotations

from typing import List, Dict, Any
from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):
    total_conversations: int
    open_tickets: int
    resolved_tickets: int
    bot_containment_rate: float
    average_response_time_seconds: float


class AnalyticsOverviewResponse(BaseModel):
    messages_by_day: List[Dict[str, Any]]
    agent_usage: List[Dict[str, Any]]
    response_times: Dict[str, Any]
    conversion_rate: float
