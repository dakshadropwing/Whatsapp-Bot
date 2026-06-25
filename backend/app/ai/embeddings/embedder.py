"""
Embedder — generates text embeddings via the configured AI provider.

Wraps GeminiProvider.embed() (text-embedding-004, 768-dim) with:
    - Single-text embedding (embed_one)
    - Batched embedding with rate-limit delay (embed_batch)
    - Cosine similarity helper

Usage:
    embedder = Embedder()
    vec = await embedder.embed_one("What is the refund policy?")

    # Batch (for indexing)
    vecs = await embedder.embed_batch(["text 1", "text 2", ...])
"""
from __future__ import annotations

import asyncio
import logging
import math
from typing import Optional

from app.ai.providers.provider_factory import ProviderFactory

logger = logging.getLogger(__name__)

# Must match DocumentChunk.EMBEDDING_DIM and the model used in GeminiProvider.embed()
EMBEDDING_DIM = 768


class Embedder:
    """
    Async wrapper around any provider's embed() method.

    Handles batching to avoid Gemini API rate limits (default: 1500 RPM
    on the free tier, 60 RPM per second). A small delay between batches
    keeps us well under the quota.
    """

    def __init__(self, provider_type: Optional[str] = None) -> None:
        # None → resolved from settings.DEFAULT_AI_PROVIDER
        self._provider_type = provider_type

    def _get_provider(self):
        return ProviderFactory.get_provider(self._provider_type)

    # ── Single ─────────────────────────────────────────────────────────────

    async def embed_one(self, text: str) -> list[float]:
        """
        Embed a single string. Returns a 768-dim float list.

        Raises:
            Exception: propagated from the underlying provider on API error.
        """
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")
        provider = self._get_provider()
        vector = await provider.embed(text.strip())
        logger.debug("Embedder.embed_one: dim=%d", len(vector))
        return vector

    # ── Batch ──────────────────────────────────────────────────────────────

    async def embed_batch(
        self,
        texts: list[str],
        batch_size: int = 20,
        delay_between_batches: float = 0.5,
    ) -> list[list[float]]:
        """
        Embed a list of strings in parallel batches.

        Args:
            texts:                  list of raw strings to embed (order preserved)
            batch_size:             number of concurrent embed calls per batch
                                    (20 is safe for Gemini free tier)
            delay_between_batches:  seconds to sleep between batches to avoid
                                    429 rate-limit errors

        Returns:
            list of embedding vectors in the same order as input texts

        Raises:
            ValueError: if texts is empty
        """
        if not texts:
            raise ValueError("embed_batch requires at least one text")

        total_batches = math.ceil(len(texts) / batch_size)
        results: list[list[float]] = []

        for batch_num, i in enumerate(range(0, len(texts), batch_size), start=1):
            batch = texts[i : i + batch_size]
            logger.debug(
                "Embedder.embed_batch: batch %d/%d (%d texts)",
                batch_num, total_batches, len(batch),
            )
            batch_vectors = await asyncio.gather(
                *[self.embed_one(t) for t in batch]
            )
            results.extend(batch_vectors)

            # Rate-limit guard: pause between batches (not after the last one)
            if i + batch_size < len(texts):
                await asyncio.sleep(delay_between_batches)

        logger.info(
            "Embedder.embed_batch: embedded %d texts in %d batches",
            len(texts), total_batches,
        )
        return results

    # ── Utility ────────────────────────────────────────────────────────────

    @staticmethod
    def cosine_similarity(a: list[float], b: list[float]) -> float:
        """
        Compute cosine similarity between two vectors.
        Returns a value in [-1, 1]; 1 = identical direction.
        """
        if len(a) != len(b):
            raise ValueError(
                f"Vector dimension mismatch: {len(a)} vs {len(b)}"
            )
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
