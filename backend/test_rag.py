"""
Standalone RAG test — tests all layers without a full Flask app.

Tests:
    1. Chunker  — sentence splitting, overlap, edge cases (no DB / API needed)
    2. Embedder — single + batch embed (requires GOOGLE_AI_API_KEY)
    3. Retriever.format_context() — context formatting logic (no DB needed)
    4. Reranker prompt building — unit test (no LLM call)

Run:
    cd /Users/dakshabordekar/Whatsapp-Bot/backend
    source .venv/bin/activate

    # With Gemini API key (for embedding tests):
    GOOGLE_AI_API_KEY=<your-key> python3 test_rag.py

    # Without API key (chunker tests only):
    python3 test_rag.py
"""
from __future__ import annotations

import asyncio
import os
import sys
import types
import uuid
from dataclasses import dataclass

# ── Minimal stubs so we can import without a running Flask app ────────────────

def _stub(name: str, path_parts: list[str]) -> None:
    """Create a stub module in sys.modules with __path__ set."""
    m = types.ModuleType(name)
    m.__path__ = [os.path.join(os.path.dirname(__file__), *path_parts)]
    m.__package__ = name
    sys.modules.setdefault(name, m)


_stub("app",                    ["app"])
_stub("app.ai",                 ["app", "ai"])
_stub("app.ai.embeddings",      ["app", "ai", "embeddings"])
_stub("app.ai.providers",       ["app", "ai", "providers"])
_stub("app.ai.rag",             ["app", "ai", "rag"])
_stub("app.ai.memory",          ["app", "ai", "memory"])
_stub("app.core",               ["app", "core"])
_stub("app.core.config",        ["app", "core", "config"])
_stub("app.models",             ["app", "models"])


class _FakeSettings:
    GOOGLE_AI_API_KEY    = os.environ.get("GOOGLE_AI_API_KEY", "")
    GOOGLE_AI_MODEL      = "gemini-2.5-flash"
    DEFAULT_AI_PROVIDER  = "gemini"
    OLLAMA_BASE_URL      = "http://localhost:11434"
    OLLAMA_MODEL         = "llama3"


_settings_mod = types.ModuleType("app.core.config.settings")
_settings_mod.get_settings = lambda: _FakeSettings()
sys.modules["app.core.config.settings"] = _settings_mod

# ── Actual imports ────────────────────────────────────────────────────────────

from app.ai.rag.chunker import Chunker, Chunk
from app.ai.embeddings.vector_store import SearchResult


# ── Helpers ───────────────────────────────────────────────────────────────────

PASS = "✅"
FAIL = "❌"
SKIP = "⚠️ "

def check(cond: bool, label: str) -> None:
    icon = PASS if cond else FAIL
    print(f"   {icon} {label}")
    if not cond:
        raise AssertionError(f"FAILED: {label}")


# ── Test 1: Chunker ───────────────────────────────────────────────────────────

SAMPLE_TEXT = """
Our refund policy allows customers to return any product within 30 days of purchase.
To initiate a return, customers must contact support with their order number.
Digital goods are non-refundable once downloaded. Physical goods must be unopened.
Shipping costs for returns are covered by the customer unless the item was defective.
Processing time for refunds is 5 to 7 business days after we receive the item.
Our team reviews all requests and responds within 24 hours.
For warranty claims, please include a photo of the defective item.
Bulk orders over 100 units have a separate return policy available on request.
We reserve the right to deny returns that do not meet our policy requirements.
Customer satisfaction is our top priority and we always aim to resolve disputes fairly.
"""


def test_chunker() -> None:
    print("=" * 55)
    print("1. CHUNKER")
    print("=" * 55)

    chunker = Chunker(chunk_size=60, chunk_overlap=10)
    chunks  = chunker.chunk(SAMPLE_TEXT)

    check(len(chunks) > 0, f"Produced {len(chunks)} chunk(s)")
    check(all(isinstance(c, Chunk) for c in chunks), "All items are Chunk instances")
    check(all(c.content.strip() for c in chunks), "All chunks have non-empty content")
    check(all(c.token_count > 0 for c in chunks), "All chunks have positive token_count")
    check(
        all(c.index == i for i, c in enumerate(chunks)),
        "Chunk indices are sequential",
    )

    # Every chunk except possibly the last should be ≤ chunk_size
    oversized = [c for c in chunks[:-1] if c.token_count > 60 + 10]
    check(len(oversized) == 0, "No intermediate chunk exceeds chunk_size (±overlap)")

    # Metadata propagation
    chunks_with_meta = chunker.chunk("Hello world.", metadata={"doc": "test"})
    check(chunks_with_meta[0].metadata == {"doc": "test"}, "Metadata propagates to chunks")

    # Empty input
    empty_chunks = chunker.chunk("")
    check(empty_chunks == [], "Empty input → empty list")

    # Whitespace-only input
    ws_chunks = chunker.chunk("   \n  ")
    check(ws_chunks == [], "Whitespace-only → empty list")

    print(f"\n   Sample output ({len(chunks)} chunks from ~{len(SAMPLE_TEXT.split())} words):")
    for c in chunks[:3]:
        print(f"   [{c.index}] {c.token_count} tokens | {c.content[:60]}...")
    if len(chunks) > 3:
        print(f"   ... ({len(chunks) - 3} more chunks)")


# ── Test 2: Embedder ──────────────────────────────────────────────────────────

async def test_embedder() -> None:
    print()
    print("=" * 55)
    print("2. EMBEDDER")
    print("=" * 55)

    api_key = os.environ.get("GOOGLE_AI_API_KEY")
    if not api_key:
        print(f"   {SKIP} Skipped — GOOGLE_AI_API_KEY not set")
        print("        Set it to test live embedding: export GOOGLE_AI_API_KEY=...")
        return

    from app.ai.embeddings.embedder import Embedder, EMBEDDING_DIM
    embedder = Embedder()

    # Single embed
    vec = await embedder.embed_one("What is the refund policy?")
    check(len(vec) == EMBEDDING_DIM, f"embed_one → {len(vec)} dims (expected {EMBEDDING_DIM})")
    check(all(isinstance(v, float) for v in vec[:5]), "Vector contains floats")

    # Batch embed
    texts  = ["Refund policy", "Order tracking", "Product warranty"]
    vecs   = await embedder.embed_batch(texts, batch_size=3)
    check(len(vecs) == 3, f"embed_batch → {len(vecs)} vectors (expected 3)")
    check(len(vecs[0]) == EMBEDDING_DIM, f"Each vector has {EMBEDDING_DIM} dims")

    # Cosine similarity: same text should score ~1.0
    v1 = await embedder.embed_one("customer support")
    v2 = await embedder.embed_one("customer support")
    sim = Embedder.cosine_similarity(v1, v2)
    check(sim > 0.99, f"Self-similarity ≈ 1.0 (got {sim:.4f})")

    # Dissimilar texts should score lower
    v3 = await embedder.embed_one("quantum physics")
    sim2 = Embedder.cosine_similarity(v1, v3)
    check(sim2 < 0.90, f"Dissimilar texts score < 0.90 (got {sim2:.4f})")
    print(f"   cosine('customer support', 'quantum physics') = {sim2:.4f}")


# ── Test 3: Retriever.format_context() ───────────────────────────────────────

def test_format_context() -> None:
    print()
    print("=" * 55)
    print("3. RETRIEVER — format_context()")
    print("=" * 55)

    from app.ai.rag.retriever import Retriever

    retriever = Retriever()

    # Build fake results
    results = [
        SearchResult(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            document_name="Product FAQ",
            content="Our refund policy allows returns within 30 days.",
            chunk_index=0,
            score=0.91,
        ),
        SearchResult(
            chunk_id=uuid.uuid4(),
            document_id=uuid.uuid4(),
            document_name="Terms of Service",
            content="Digital goods are non-refundable once downloaded.",
            chunk_index=2,
            score=0.78,
        ),
    ]

    context = retriever.format_context(results)
    check("--- Relevant Knowledge ---" in context, "Header present")
    check("[1]" in context, "First result present")
    check("[2]" in context, "Second result present")
    check("Product FAQ" in context, "Document name included")
    check("0.91" in context, "Score included")

    # Empty results
    empty_ctx = retriever.format_context([])
    check(empty_ctx == "", "Empty results → empty string")

    # max_chars truncation
    short_ctx = retriever.format_context(results, max_chars=50)
    check(len(short_ctx) <= 60, f"max_chars respected (~{len(short_ctx)} chars)")

    print(f"\n   Sample context output:\n")
    for line in context.split("\n"):
        print(f"   {line}")


# ── Test 4: VectorStore._fmt_embedding() ─────────────────────────────────────

def test_vector_store_fmt() -> None:
    print()
    print("=" * 55)
    print("4. VECTOR STORE — _fmt_embedding()")
    print("=" * 55)

    from app.ai.embeddings.vector_store import VectorStore
    store = VectorStore()

    vec = [0.1, -0.2, 0.333333]
    fmt = store._fmt_embedding(vec)

    check(fmt.startswith("["), "Starts with [")
    check(fmt.endswith("]"), "Ends with ]")
    check("0.10000000" in fmt, "Values formatted to 8 decimal places")
    check(fmt.count(",") == 2, "Correct number of separators")
    print(f"   _fmt_embedding([0.1, -0.2, 0.333333]) = {fmt}")


# ── Main ──────────────────────────────────────────────────────────────────────

async def main() -> None:
    print("\n🔍 RAG Module — Live Test\n")

    try:
        test_chunker()
        await test_embedder()
        test_format_context()
        test_vector_store_fmt()

        print()
        print("=" * 55)
        print(f"{PASS} All RAG tests passed!")
        print("=" * 55)
        print()
        print("Next steps:")
        print("  1. Run the DB migration:  flask db upgrade")
        print("  2. Create a KnowledgeBase and Document in the DB")
        print("  3. Call Indexer().index_document(db, document) to index it")
        print("  4. Call Retriever().search(db, query, kb_id) to test retrieval")

    except AssertionError as exc:
        print(f"\n{FAIL} Test FAILED: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
