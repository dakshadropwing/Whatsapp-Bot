"""
Base Agent — all specialist agents extend this class.
"""
from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from app.ai.providers.provider_factory import ProviderFactory
from app.ai.memory.context_manager import ContextManager
from app.ai.tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base for all specialist agents.

    Every agent has:
      - A system prompt that defines its persona and capabilities.
      - Access to the AI provider via ProviderFactory.
      - Access to conversation memory via ContextManager.
      - A registry of BaseTool instances for automatic dispatch.
    """

    agent_name: str = "base"
    system_prompt: str = ""

    def __init__(self) -> None:
        self.provider = ProviderFactory.get_provider()
        self.memory = ContextManager()
        # _tool_instances: name → BaseTool (used for execution dispatch)
        self._tool_instances: dict[str, BaseTool] = {}
        self.tools: list[dict] = self._register_tools()

    # ── Tool registration ─────────────────────────────────────────────────

    @abstractmethod
    def _register_tools(self) -> list[dict]:
        """
        Return a list of tool definitions in OpenAI function-calling format.

        Subclasses should call ``self._register_tool(instance)`` for each
        ``BaseTool`` and then return ``self._get_tool_schemas()``.  They
        may also append raw dicts for simple tools that don't need a class.
        """
        return []

    def _register_tool(self, tool: BaseTool) -> None:
        """
        Register a BaseTool instance in the internal registry.

        The tool's ``name`` is used as the dispatch key in ``_execute_tool``.
        """
        self._tool_instances[tool.name] = tool

    def _get_tool_schemas(self) -> list[dict]:
        """Return OpenAI-format schemas for all registered tool instances."""
        return [t.to_openai_schema() for t in self._tool_instances.values()]

    # ── Message handling ──────────────────────────────────────────────────

    @abstractmethod
    async def handle(self, message: dict[str, Any]) -> None:
        """Process an inbound normalised message end-to-end."""
        ...

    async def _generate_response(
        self,
        conversation_id: str,
        user_message: str,
    ) -> str:
        """
        Build message history, call the LLM, execute any tool calls,
        and return the final text response.
        """
        from app.ai.providers.base_provider import CompletionRequest, Message

        history = await self.memory.get_history(conversation_id)

        messages = [Message(role="system", content=self.system_prompt)]
        messages.extend(history)
        messages.append(Message(role="user", content=user_message))

        request = CompletionRequest(
            messages=messages,
            tools=self.tools,
        )

        response = await self.provider.complete(request)

        # Handle tool calls if present
        if response.tool_calls:
            for tc in response.tool_calls:
                tool_result = await self._execute_tool(tc.name, tc.arguments)
                messages.append(
                    Message(role="assistant", content=response.content)
                )
                messages.append(
                    Message(
                        role="tool",
                        content=self._serialise_tool_result(tool_result),
                        name=tc.name,
                    )
                )

            # Second pass with tool results
            final_request = CompletionRequest(messages=messages)
            response = await self.provider.complete(final_request)

        # Save to memory
        await self.memory.save_turn(
            conversation_id=conversation_id,
            user_message=user_message,
            assistant_message=response.content,
        )

        # Save outbound AI response to PostgreSQL
        try:
            from app.extensions import db
            from sqlalchemy import select
            from app.models.conversation import Conversation
            from app.services.message_service import MessageService

            conv = db.session.execute(
                select(Conversation)
                .where(Conversation.contact_phone == conversation_id)
                .order_by(Conversation.created_at.desc())
                .limit(1)
            ).scalar_one_or_none()

            if conv:
                MessageService.create_message(
                    org_id=str(conv.organization_id),
                    conversation_id=str(conv.id),
                    direction="outbound",
                    body=response.content,
                    message_type="text",
                    ai_generated=True
                )
        except Exception as db_exc:
            logger.exception("BaseAgent: Failed to persist outbound message to database", exc_info=db_exc)

        return response.content

    # ── Tool execution ────────────────────────────────────────────────────

    async def _execute_tool(self, tool_name: str, arguments: dict) -> Any:
        """
        Dispatch tool execution.

        First checks the ``_tool_instances`` registry for a matching
        ``BaseTool``.  If not found, logs a warning and returns an
        error dict.  Subclasses can override to handle non-BaseTool
        actions (e.g. ``escalate_to_human``).
        """
        tool = self._tool_instances.get(tool_name)
        if tool is not None:
            return await tool.safe_execute(**arguments)

        logger.warning("[%s] Unknown tool: %s", self.agent_name, tool_name)
        return {"error": f"Tool '{tool_name}' not implemented"}

    # ── Utility ───────────────────────────────────────────────────────────

    @staticmethod
    def _serialise_tool_result(result: Any) -> str:
        """
        Convert a tool result to a string suitable for ``Message.content``.

        Handles dicts (JSON), strings, and arbitrary objects.
        """
        if isinstance(result, dict):
            try:
                return json.dumps(result, default=str)
            except (TypeError, ValueError):
                return str(result)
        return str(result)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} agent={self.agent_name}>"
