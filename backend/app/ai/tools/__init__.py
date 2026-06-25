"""
AI Tools — agent-callable functions.

All tools extend ``BaseTool`` and provide:
    - ``to_openai_schema()`` → schema for ``CompletionRequest(tools=[...])``.
    - ``safe_execute(**kwargs)`` → error-safe execution returning a ``dict``.

Import from here in agents::

    from app.ai.tools import SearchTool, TicketTool, GetTicketStatusTool
"""
from app.ai.tools.base_tool import BaseTool
from app.ai.tools.search_tool import SearchTool
from app.ai.tools.ticket_tool import GetTicketStatusTool, TicketTool
from app.ai.tools.whatsapp_tool import SendWhatsAppMessageTool
from app.ai.tools.crm_tool import GetContactInfoTool, UpdateContactFactTool
from app.ai.tools.calendar_tool import BookAppointmentTool, CheckAvailabilityTool
from app.ai.tools.endpoint_tool import CallEndpointTool

__all__ = [
    "BaseTool",
    "SearchTool",
    "TicketTool",
    "GetTicketStatusTool",
    "SendWhatsAppMessageTool",
    "GetContactInfoTool",
    "UpdateContactFactTool",
    "CheckAvailabilityTool",
    "BookAppointmentTool",
    "CallEndpointTool",
]
