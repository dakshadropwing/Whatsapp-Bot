"""
BaseTool — abstract interface for all agent tools.

Every tool must:
    1. Define ``name`` and ``description`` (used in the schema sent to the LLM).
    2. Define ``parameters_schema`` (JSON-Schema dict for function arguments).
    3. Implement ``async execute(**kwargs) -> dict``.

The schema is returned in **OpenAI function-calling format** via
``to_openai_schema()`` — which is exactly what ``GeminiProvider``
converts into ``types.FunctionDeclaration`` automatically.

Usage in an agent::

    tool = SearchTool(kb_id=..., db_session=...)
    schema = tool.to_openai_schema()        # → CompletionRequest(tools=[...])
    result = await tool.safe_execute(query="refund policy")
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """
    Abstract base for all agent-callable tools.

    Mirrors the pattern used by ``BaseAIProvider`` in the providers layer:
    subclasses define identity fields and implement a single entry-point method.
    """

    # ── Identity (subclasses MUST override) ────────────────────────────────
    name: str = "base_tool"
    description: str = ""
    parameters_schema: dict = {
        "type": "object",
        "properties": {},
        "required": [],
    }

    # ── Core contract ──────────────────────────────────────────────────────

    @abstractmethod
    async def execute(self, **kwargs: Any) -> dict:
        """
        Run the tool with the arguments the LLM chose.

        Args:
            **kwargs: Arguments matching ``parameters_schema`` properties.

        Returns:
            A JSON-serialisable ``dict``.  This is stringified and sent
            back to the LLM as a ``Message(role="tool", ...)``.
        """
        ...

    # ── Schema export ──────────────────────────────────────────────────────

    def to_openai_schema(self) -> dict:
        """
        Return the tool definition in OpenAI function-calling format::

            {"type": "function", "function": {"name": ..., "description": ..., "parameters": ...}}

        ``GeminiProvider._build_gemini_contents_and_config()`` already
        converts this format into ``types.FunctionDeclaration``.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema,
            },
        }

    # ── Safe wrapper ───────────────────────────────────────────────────────

    async def safe_execute(self, **kwargs: Any) -> dict:
        """
        Call ``execute()`` with error handling so a failing tool never
        crashes the agent — it returns an error dict instead.

        Agents should always prefer ``safe_execute`` over ``execute``
        in production paths.
        """
        try:
            return await self.execute(**kwargs)
        except Exception as exc:
            logger.exception(
                "Tool '%s' failed with args=%s",
                self.name,
                kwargs,
                exc_info=exc,
            )
            return {"error": str(exc), "tool": self.name}

    # ── Utility ────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
