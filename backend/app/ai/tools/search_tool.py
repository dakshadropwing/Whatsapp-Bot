"""
SearchTool — RAG knowledge-base search via Retriever → VectorStore → pgvector.

Wraps the existing ``app.ai.rag.retriever.Retriever`` so agents can call
``search_knowledge_base`` as a tool and get grounded answers.

Dependencies (all already built):
    - ``Retriever`` → ``Embedder`` → provider embedding endpoint
    - ``VectorStore`` → pgvector cosine-similarity ANN search
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Optional

from app.ai.tools.base_tool import BaseTool
from app.ai.rag.retriever import Retriever

logger = logging.getLogger(__name__)


class SearchTool(BaseTool):
    """Search the company knowledge base for relevant articles and FAQs."""

    name = "search_knowledge_base"
    description = (
        "Search the company knowledge base for relevant articles, FAQs, "
        "and documentation.  Use this before answering any factual question "
        "about the company, its products, or its policies."
    )
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural-language search query derived from the user's message.",
            },
            "top_k": {
                "type": "integer",
                "description": "Maximum number of results to return (default: 5).",
            },
        },
        "required": ["query"],
    }

    def __init__(
        self,
        knowledge_base_id: uuid.UUID,
        db_session: Any,
        top_k: int = 5,
        min_score: float = 0.50,
        provider_type: Optional[str] = None,
    ) -> None:
        """
        Args:
            knowledge_base_id:  UUID of the KnowledgeBase to search.
            db_session:         Active SQLAlchemy ``Session`` (Flask ``db.session``).
            top_k:              Default number of chunks to return.
            min_score:          Minimum cosine-similarity threshold.
            provider_type:      Override embedding provider (``"gemini"`` | ``"ollama"``).
        """
        self._kb_id = knowledge_base_id
        self._db = db_session
        self._top_k = top_k
        self._retriever = Retriever(
            top_k=top_k,
            min_score=min_score,
            provider_type=provider_type,
        )

    async def execute(self, query: str, top_k: Optional[int] = None, **_: Any) -> dict:
        """
        Embed ``query``, run a vector-similarity search, and return
        formatted results for the LLM.
        """
        k = top_k if top_k is not None else self._top_k

        if not query or not query.strip():
            return {"found": False, "results": [], "query": query}

        results = await self._retriever.search(
            db=self._db,
            query=query,
            knowledge_base_id=self._kb_id,
            top_k=k,
        )

        if not results:
            return {"found": False, "results": [], "query": query}

        formatted = [
            {
                "rank": i + 1,
                "score": round(r.score, 3),
                "source": r.document_name,
                "content": r.content[:800],  # cap per-chunk length
            }
            for i, r in enumerate(results)
        ]

        logger.info("SearchTool: query=%r → %d results", query[:60], len(results))
        return {"found": True, "results": formatted, "query": query}
