"""
Base Agent — all specialist agents extend this class.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from app.ai.providers.provider_factory import ProviderFactory
from app.ai.memory.context_manager import ContextManager

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base for all specialist agents.

    Every agent has:
      - A system prompt that defines its persona and capabilities.
      - Access to the AI provider via ProviderFactory.
      - Access to conversation memory via ContextManager.
      - An optional list of tools it can invoke.
    """

    agent_name: str = "base"
    system_prompt: str = ""

    def __init__(self) -> None:
        self.provider = ProviderFactory.get_provider()
        self.memory = ContextManager()
        self.tools: list[dict] = self._register_tools()

    @abstractmethod
    def _register_tools(self) -> list[dict]:
        """Return a list of tool definitions in OpenAI function-calling format."""
        return []

    @abstractmethod
    async def handle(self, message: dict[str, Any]) -> None:
        """Process an inbound normalized message end-to-end."""
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
                    Message(role="tool", content=str(tool_result), name=tc.name)
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

        return response.content

    async def _execute_tool(self, tool_name: str, arguments: dict) -> Any:
        """Dispatch tool execution. Override in subclasses to add tools."""
        logger.warning(f"[{self.agent_name}] Unknown tool: {tool_name}")
        return {"error": f"Tool '{tool_name}' not implemented"}

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} agent={self.agent_name}>"
