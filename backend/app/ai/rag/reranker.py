"""
Reranker — LLM-as-judge cross-encoder for RAG result refinement.

After the Retriever returns top-K candidates via vector similarity,
the Reranker asks the LLM to re-score each chunk on true relevance
to the user's query. This catches false positives from embedding-space
similarity (chunks that are topically similar but don't actually answer
the question).

When to use:
    - High-precision use cases (support, legal, medical)
    - When your initial top_k is large (10–20) and you want the best 3–5
    - When users report "the bot answered with irrelevant info"

When to skip:
    - Latency-sensitive paths (adds ~1–2 LLM calls)
    - When initial retrieval quality is already high

Usage:
    retriever = Retriever(top_k=10, min_score=0.40)
    reranker  = Reranker()

    candidates = await retriever.search(db, query, kb_id, top_k=10)
    top_chunks = await reranker.rerank(query, candidates, top_n=3)
    context    = retriever.format_context(top_chunks)
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

from app.ai.embeddings.vector_store import SearchResult
from app.ai.providers.provider_factory import ProviderFactory
from app.ai.providers.base_provider import CompletionRequest, Message

logger = logging.getLogger(__name__)

# ── Prompt ────────────────────────────────────────────────────────────────────

_RERANK_PROMPT = """\
You are a relevance evaluator. Given a QUERY and a PASSAGE, output a single \
integer from 0 to 10 indicating how relevant the passage is to the query.

Scoring guide:
  0  = completely unrelated to the query
  3  = loosely related but doesn't answer it
  5  = partially answers the query
  8  = clearly relevant and helpful
  10 = directly and fully answers the query

Output ONLY the integer, nothing else. No explanation, no punctuation.

QUERY: {query}

PASSAGE:
{passage}

SCORE:"""


class Reranker:
    """
    Re-scores retrieval candidates using an LLM relevance score.

    Each candidate gets one LLM call with temperature=0 for determinism.
    Results are sorted by the new score and trimmed to top_n.

    For larger scale, replace with a dedicated cross-encoder model such as
    mixedbread-ai/mxbai-rerank-base-v1 via sentence-transformers.

    Args:
        provider_type:         override AI provider (None → settings default)
        concurrency:           max parallel LLM scoring calls (default: 3)
        passage_max_chars:     truncate passages to this length before scoring
    """

    def __init__(
        self,
        provider_type: Optional[str] = None,
        concurrency: int = 3,
        passage_max_chars: int = 800,
    ) -> None:
        self._provider_type     = provider_type
        self._concurrency       = concurrency
        self._passage_max_chars = passage_max_chars

    # ── Public API ─────────────────────────────────────────────────────────

    async def rerank(
        self,
        query: str,
        candidates: list[SearchResult],
        top_n: int = 3,
    ) -> list[SearchResult]:
        """
        Re-score and filter retrieval candidates.

        Args:
            query:      the original user query string
            candidates: list[SearchResult] from Retriever.search()
            top_n:      how many to return after reranking

        Returns:
            top_n SearchResults with score updated to reranker score [0..1],
            sorted descending (best first).
        """
        if not candidates:
            return []

        top_n = min(top_n, len(candidates))

        # Score all candidates concurrently (respect concurrency limit)
        scores = await self._score_all(query, candidates)

        # Pair results with scores, sort descending
        scored_pairs = sorted(
            zip(scores, candidates),
            key=lambda pair: pair[0],
            reverse=True,
        )

        reranked: list[SearchResult] = []
        for score, result in scored_pairs[:top_n]:
            result.score = score   # overwrite vector similarity with LLM score
            reranked.append(result)

        logger.info(
            "Reranker: %d candidates → top %d "
            "(scores: %s)",
            len(candidates),
            len(reranked),
            [f"{r.score:.2f}" for r in reranked],
        )
        return reranked

    # ── Internals ──────────────────────────────────────────────────────────

    async def _score_all(
        self,
        query: str,
        candidates: list[SearchResult],
    ) -> list[float]:
        """Score all candidates, respecting the concurrency cap."""
        semaphore = asyncio.Semaphore(self._concurrency)

        async def score_one(result: SearchResult) -> float:
            async with semaphore:
                return await self._score_chunk(query, result)

        return list(await asyncio.gather(*[score_one(r) for r in candidates]))

    async def _score_chunk(self, query: str, result: SearchResult) -> float:
        """
        Ask the LLM to score a single chunk 0–10, return as float 0.0–1.0.
        Falls back to the original vector similarity score on any error.
        """
        passage = result.content.strip()[: self._passage_max_chars]
        prompt  = _RERANK_PROMPT.format(query=query, passage=passage)

        try:
            provider = ProviderFactory.get_provider(self._provider_type)
            response = await provider.complete(
                CompletionRequest(
                    messages=[Message(role="user", content=prompt)],
                    temperature=0.0,    # deterministic
                    max_tokens=5,       # we only need "0"–"10"
                )
            )
            raw = response.content.strip().split()[0]
            score = max(0.0, min(10.0, float(raw))) / 10.0
            logger.debug(
                "Reranker._score_chunk: chunk=%s raw=%r → %.2f",
                result.chunk_id, raw, score,
            )
            return score

        except (ValueError, IndexError) as exc:
            logger.warning(
                "Reranker: could not parse score for chunk=%s (%s), "
                "falling back to vector score %.2f",
                result.chunk_id, exc, result.score,
            )
            return result.score  # fall back to vector similarity

        except Exception as exc:
            logger.error(
                "Reranker: LLM call failed for chunk=%s: %s, "
                "using vector score %.2f",
                result.chunk_id, exc, result.score,
            )
            return result.score
