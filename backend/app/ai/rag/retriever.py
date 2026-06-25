"""
Retriever — main entry point for RAG search at query time.

Pipeline:
    user query (str)
        → Embedder.embed_one()       → query_vector [768 floats]
        → VectorStore.search()       → top-K SearchResults
        → (optional Reranker)
        → Retriever.format_context() → str injected into system prompt

Usage:
    retriever = Retriever(top_k=5, min_score=0.50)

    results = await retriever.search(
        db=db_session,
        query="What is the refund policy?",
        knowledge_base_id=kb_uuid,
    )
    context_str = retriever.format_context(results)

    # Inject context_str into ContextManager.build_messages(rag_context=...)
"""
from __future__ import annotations

import logging
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.ai.embeddings.embedder import Embedder
from app.ai.embeddings.vector_store import VectorStore, SearchResult

logger = logging.getLogger(__name__)


class Retriever:
    """
    Combines Embedder + VectorStore into a single async search call.

    Args:
        top_k:     default number of chunks to return (overridable per call)
        min_score: default minimum cosine similarity threshold
        provider_type: override embedding provider ("gemini" | "ollama" | None)
    """

    def __init__(
        self,
        top_k: int = 5,
        min_score: float = 0.50,
        provider_type: Optional[str] = None,
    ) -> None:
        self.top_k = top_k
        self.min_score = min_score
        self._embedder = Embedder(provider_type=provider_type)
        self._store = VectorStore()

    # ── Search ─────────────────────────────────────────────────────────────

    async def search(
        self,
        db: Session,
        query: str,
        knowledge_base_id: uuid.UUID,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
    ) -> list[SearchResult]:
        """
        Embed the query and return ranked chunks from the given KB.

        Args:
            db:                active SQLAlchemy session
            query:             natural-language question from the user
            knowledge_base_id: which KnowledgeBase to search
            top_k:             number of results (overrides instance default)
            min_score:         minimum similarity threshold (overrides default)

        Returns:
            list[SearchResult] sorted by score descending (best match first)
            Empty list if no chunks meet the threshold or KB has no content.
        """
        k = top_k if top_k is not None else self.top_k
        threshold = min_score if min_score is not None else self.min_score

        if not query or not query.strip():
            logger.warning("Retriever.search: empty query, returning []")
            return []

        # Step 1: Embed the query
        query_embedding = await self._embedder.embed_one(query.strip())

        # Step 2: Vector similarity search
        results = self._store.search(
            db=db,
            query_embedding=query_embedding,
            knowledge_base_id=knowledge_base_id,
            top_k=k,
            min_score=threshold,
        )

        logger.info(
            "Retriever.search: query=%r kb=%s top_k=%d → %d results",
            query[:80], knowledge_base_id, k, len(results),
        )
        return results

    async def search_multi_kb(
        self,
        db: Session,
        query: str,
        knowledge_base_ids: list[uuid.UUID],
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
    ) -> list[SearchResult]:
        """
        Search across multiple KnowledgeBases and merge results by score.

        Useful when an organisation has separate KBs (e.g. "Support FAQ"
        and "Product Docs") and you want to search both at once.

        Returns top_k results across all KBs, sorted by score descending.
        """
        k = top_k if top_k is not None else self.top_k
        threshold = min_score if min_score is not None else self.min_score

        if not knowledge_base_ids:
            return []

        query_embedding = await self._embedder.embed_one(query.strip())

        all_results: list[SearchResult] = []
        for kb_id in knowledge_base_ids:
            results = self._store.search(
                db=db,
                query_embedding=query_embedding,
                knowledge_base_id=kb_id,
                top_k=k,
                min_score=threshold,
            )
            all_results.extend(results)

        # Merge and re-sort by score, cap at top_k
        all_results.sort(key=lambda r: r.score, reverse=True)
        return all_results[:k]

    # ── Context formatting ─────────────────────────────────────────────────

    def format_context(
        self,
        results: list[SearchResult],
        max_chars: int = 4000,
        header: str = "--- Relevant Knowledge ---",
    ) -> str:
        """
        Format retrieval results into a text block for system prompt injection.

        Args:
            results:   list of SearchResult (from search())
            max_chars: hard cap on total output length (avoid token overflow)
            header:    section header line

        Returns:
            Formatted string, or "" if results is empty.

        Example output:
            --- Relevant Knowledge ---
            [1] (score: 0.87) From: Product FAQ
            Our refund policy allows returns within 30 days of purchase...

            [2] (score: 0.81) From: Terms of Service
            Digital goods are non-refundable once downloaded...
        """
        if not results:
            return ""

        lines: list[str] = [header]
        total_chars = len(header)

        for i, r in enumerate(results, start=1):
            snippet = r.content.strip()
            entry = (
                f"\n[{i}] (score: {r.score:.2f}) From: {r.document_name}\n"
                f"{snippet}"
            )
            if total_chars + len(entry) > max_chars:
                logger.debug(
                    "Retriever.format_context: truncated at result %d "
                    "(char limit %d reached)", i, max_chars
                )
                break
            lines.append(entry)
            total_chars += len(entry)

        return "\n".join(lines)

    # ── Convenience: check if KB has indexed content ───────────────────────

    def has_content(self, db: Session, knowledge_base_id: uuid.UUID) -> bool:
        """
        Return True if the KB has at least one indexed chunk.
        Lightweight check — does not embed anything.
        """
        from sqlalchemy import text
        result = db.execute(
            text("""
                SELECT EXISTS (
                    SELECT 1
                    FROM document_chunks dc
                    JOIN documents d ON d.id = dc.document_id
                    WHERE d.knowledge_base_id = :kb_id
                      AND d.status = 'indexed'
                      AND dc.embedding IS NOT NULL
                    LIMIT 1
                )
            """),
            {"kb_id": str(knowledge_base_id)},
        ).scalar()
        return bool(result)
