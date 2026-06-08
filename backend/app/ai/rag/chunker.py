"""
Chunker — splits raw document text into overlapping fixed-size windows.

Strategy:
    1. Split text into sentences (punctuation-aware).
    2. Accumulate sentences until the chunk_size token budget is reached.
    3. Start the next chunk with `chunk_overlap` tokens of overlap
       to preserve context across boundaries.
    4. If a single sentence exceeds chunk_size, word-split it directly.

This approach preserves sentence integrity, which improves embedding quality
compared to hard character/word splits.

For production workloads with precise token counting, swap
`_count_tokens()` to use tiktoken:

    import tiktoken
    enc = tiktoken.get_encoding("cl100k_base")
    def _count_tokens(self, text): return len(enc.encode(text))

Usage:
    chunker = Chunker(chunk_size=512, chunk_overlap=64)
    chunks  = chunker.chunk(raw_text, metadata={"doc_id": "abc"})
"""
from __future__ import annotations

import re
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ── Defaults ──────────────────────────────────────────────────────────────────
# Tuned for text-embedding-004 (max context ~2048 tokens; sweet spot ~512)
DEFAULT_CHUNK_SIZE    = 512   # approximate tokens per chunk
DEFAULT_CHUNK_OVERLAP = 64    # tokens of overlap between consecutive chunks


@dataclass
class Chunk:
    """A single text chunk produced by the Chunker."""
    index:       int
    content:     str
    token_count: int
    metadata:    dict = field(default_factory=dict)


class Chunker:
    """
    Sentence-boundary-aware sliding-window text chunker.

    Attributes:
        chunk_size:    target token count per chunk
        chunk_overlap: overlap token budget between adjacent chunks
    """

    # Sentence-boundary pattern: split on . ! ? followed by whitespace
    _SENTENCE_SPLIT_RE = re.compile(r'(?<=[.!?])\s+')

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({chunk_overlap}) must be less than "
                f"chunk_size ({chunk_size})"
            )
        self.chunk_size    = chunk_size
        self.chunk_overlap = chunk_overlap

    # ── Public API ─────────────────────────────────────────────────────────

    def chunk(
        self,
        text: str,
        metadata: dict | None = None,
    ) -> list[Chunk]:
        """
        Split `text` into overlapping chunks.

        Args:
            text:     raw document text to split
            metadata: optional dict attached to every chunk
                      (e.g. {"document_id": "...", "source_url": "..."})

        Returns:
            Ordered list of Chunk objects (index 0 = beginning of doc)
        """
        if not text or not text.strip():
            logger.warning("Chunker.chunk: received empty text, returning []")
            return []

        meta = metadata or {}
        sentences = self._split_sentences(text)
        chunks: list[Chunk] = []

        current_sents: list[str] = []
        current_tokens: int = 0
        chunk_idx: int = 0

        for sentence in sentences:
            s_tokens = self._count_tokens(sentence)

            # ── Case 1: single sentence exceeds budget → hard word-split ───
            if s_tokens > self.chunk_size:
                # Flush current buffer first
                if current_sents:
                    chunk_idx = self._flush(
                        chunks, current_sents, chunk_idx, meta
                    )
                    current_sents, current_tokens = self._overlap_seed(
                        current_sents
                    )

                # Word-split the giant sentence
                words = sentence.split()
                for i in range(0, len(words), self.chunk_size):
                    sub = " ".join(words[i : i + self.chunk_size])
                    chunks.append(Chunk(
                        index=chunk_idx,
                        content=sub,
                        token_count=self._count_tokens(sub),
                        metadata=meta.copy(),
                    ))
                    chunk_idx += 1
                continue

            # ── Case 2: adding this sentence overflows the chunk ────────────
            if current_tokens + s_tokens > self.chunk_size and current_sents:
                chunk_idx = self._flush(chunks, current_sents, chunk_idx, meta)
                current_sents, current_tokens = self._overlap_seed(current_sents)

            current_sents.append(sentence)
            current_tokens += s_tokens

        # ── Flush remaining sentences ───────────────────────────────────────
        if current_sents:
            self._flush(chunks, current_sents, chunk_idx, meta)

        logger.debug(
            "Chunker.chunk: %d sentences → %d chunks "
            "(size=%d overlap=%d)",
            len(sentences), len(chunks), self.chunk_size, self.chunk_overlap,
        )
        return chunks

    # ── Internals ──────────────────────────────────────────────────────────

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentence strings. Filters blank entries."""
        raw = self._SENTENCE_SPLIT_RE.split(text.strip())
        return [s.strip() for s in raw if s.strip()]

    def _count_tokens(self, text: str) -> int:
        """
        Approximate token count by whitespace-splitting.
        Swap with tiktoken for exact counts.
        """
        return len(text.split())

    def _flush(
        self,
        chunks: list[Chunk],
        sents: list[str],
        idx: int,
        meta: dict,
    ) -> int:
        """Build a Chunk from `sents`, append to `chunks`, return next idx."""
        content = " ".join(sents)
        chunks.append(Chunk(
            index=idx,
            content=content,
            token_count=self._count_tokens(content),
            metadata=meta.copy(),
        ))
        return idx + 1

    def _overlap_seed(self, sents: list[str]) -> tuple[list[str], int]:
        """
        Return a subset of `sents` that fits within the overlap budget,
        taking from the end (most recent context).
        """
        overlap_budget = 0
        overlap_sents: list[str] = []
        for s in reversed(sents):
            t = self._count_tokens(s)
            if overlap_budget + t <= self.chunk_overlap:
                overlap_sents.insert(0, s)
                overlap_budget += t
            else:
                break
        return overlap_sents, overlap_budget
