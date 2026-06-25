"""
CRM Tools — read and update customer profile data.

``GetContactInfoTool`` queries the ``Conversation`` model to pull stored
contact metadata (name, tags, context memory).

``UpdateContactFactTool`` writes persistent facts via the existing
``ContextManager.update_fact()`` method, which stores data in the
``conversations.context`` JSONB column under the ``memory`` namespace.
"""
from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select

from app.ai.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class GetContactInfoTool(BaseTool):
    """Retrieve stored information about a customer."""

    name = "get_contact_info"
    description = (
        "Retrieve stored information about the customer: name, company, "
        "tags, conversation count, and any previously saved facts."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "phone_number": {
                "type": "string",
                "description": "Customer phone number in E.164 format.",
            },
        },
        "required": ["phone_number"],
    }

    def __init__(self, db_session: Any) -> None:
        self._db = db_session

    async def execute(self, phone_number: str, **_: Any) -> dict:
        from app.models.conversation import Conversation

        # Get the most recent conversation for this phone number
        conv = self._db.execute(
            select(Conversation)
            .where(Conversation.contact_phone == phone_number)
            .order_by(Conversation.created_at.desc())
            .limit(1)
        ).scalar_one_or_none()

        if not conv:
            return {"found": False, "phone_number": phone_number}

        # Extract long-term memory from the context JSONB column
        memory = (conv.context or {}).get("memory", {})

        return {
            "found": True,
            "phone_number": phone_number,
            "contact_name": conv.contact_name or memory.get("user_name", "Unknown"),
            "message_count": conv.message_count or 0,
            "total_turns": memory.get("total_turns", 0),
            "language": memory.get("language"),
            "last_intent": memory.get("last_intent"),
            "key_facts": memory.get("key_facts", []),
            "tags": conv.tags or [],
            "status": conv.status.value if conv.status else "unknown",
        }


class UpdateContactFactTool(BaseTool):
    """Save a persistent fact about the customer to long-term memory."""

    name = "update_contact_fact"
    description = (
        "Save a fact about the customer to long-term memory (e.g. their "
        "name, preferences, plan type, language).  This persists across "
        "conversations so the agent remembers it next time."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": (
                    "Fact key — e.g. 'user_name', 'language', 'plan', "
                    "'preferred_contact_time'."
                ),
            },
            "value": {
                "type": "string",
                "description": "Fact value to store.",
            },
        },
        "required": ["key", "value"],
    }

    def __init__(
        self,
        db_session: Any,
        conversation_obj: Any,
        context_manager: Any,
    ) -> None:
        """
        Args:
            db_session:       Active SQLAlchemy session.
            conversation_obj: The current ``Conversation`` ORM instance.
            context_manager:  ``ContextManager`` instance from the agent.
        """
        self._db = db_session
        self._conv = conversation_obj
        self._memory = context_manager

    async def execute(self, key: str, value: str, **_: Any) -> dict:
        self._memory.update_fact(self._conv, key, value, self._db)
        logger.info(
            "UpdateContactFactTool: key=%s for conversation=%s",
            key,
            self._conv.id,
        )
        return {"updated": True, "key": key, "value": value}
