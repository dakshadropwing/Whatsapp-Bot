"""
Unit tests for OllamaProvider.

These tests use httpx.MockTransport so they run WITHOUT a real Ollama server.
Run with:
    pytest tests/unit/ai/test_ollama_provider.py -v
"""
from __future__ import annotations

import json
import pytest
import httpx

from app.ai.providers.ollama_provider import OllamaProvider
from app.ai.providers.base_provider import CompletionRequest, Message


# ────────────────────────────────────────────────────────────────────────────
#  Helpers: fake HTTP responses
# ────────────────────────────────────────────────────────────────────────────

def _make_provider(transport: httpx.MockTransport) -> OllamaProvider:
    """Create an OllamaProvider that uses a mock HTTP transport."""
    provider = OllamaProvider(base_url="http://fake-ollama", model="llama3")
    # Swap the real client for a mock one
    provider._client = httpx.AsyncClient(
        base_url="http://fake-ollama",
        transport=transport,
    )
    return provider


def _chat_response(content: str, model: str = "llama3") -> bytes:
    """Build a fake /api/chat JSON response body."""
    body = {
        "model": model,
        "message": {"role": "assistant", "content": content},
        "done": True,
        "prompt_eval_count": 10,
        "eval_count": 20,
    }
    return json.dumps(body).encode()


def _stream_chunks(tokens: list[str], model: str = "llama3") -> bytes:
    """Build a fake streaming response (newline-delimited JSON)."""
    lines = []
    for i, token in enumerate(tokens):
        is_last = i == len(tokens) - 1
        chunk = {
            "model": model,
            "message": {"role": "assistant", "content": token},
            "done": is_last,
        }
        if is_last:
            chunk["eval_count"] = len(tokens)
        lines.append(json.dumps(chunk))
    return "\n".join(lines).encode()


def _embed_response(dims: int = 4) -> bytes:
    """Build a fake /api/embeddings response."""
    body = {"embedding": [0.1 * i for i in range(dims)]}
    return json.dumps(body).encode()


def _tags_response(models: list[str] = ("llama3",)) -> bytes:
    """Build a fake /api/tags response."""
    body = {"models": [{"name": m} for m in models]}
    return json.dumps(body).encode()


def _simple_request(text: str = "Hello!") -> CompletionRequest:
    return CompletionRequest(messages=[Message(role="user", content=text)])


# ────────────────────────────────────────────────────────────────────────────
#  Tests: _configure
# ────────────────────────────────────────────────────────────────────────────

class TestConfigure:
    def test_default_values(self):
        """Provider uses sensible defaults when no kwargs given."""
        p = OllamaProvider()
        assert p._base_url == "http://localhost:11434"
        assert p._model == "llama3"

    def test_custom_values(self):
        """Provider respects custom base_url and model."""
        p = OllamaProvider(base_url="http://myserver:9999", model="mistral")
        assert p._base_url == "http://myserver:9999"
        assert p._model == "mistral"

    def test_trailing_slash_stripped(self):
        """Trailing slash in base_url is removed."""
        p = OllamaProvider(base_url="http://localhost:11434/")
        assert p._base_url == "http://localhost:11434"


# ────────────────────────────────────────────────────────────────────────────
#  Tests: complete()
# ────────────────────────────────────────────────────────────────────────────

class TestComplete:
    @pytest.mark.asyncio
    async def test_returns_completion_response(self):
        """complete() returns a properly populated CompletionResponse."""
        transport = httpx.MockTransport(
            lambda req: httpx.Response(200, content=_chat_response("Hi there!"))
        )
        provider = _make_provider(transport)

        resp = await provider.complete(_simple_request("Hello"))

        assert resp.content == "Hi there!"
        assert resp.provider == "ollama"
        assert resp.model == "llama3"
        assert resp.input_tokens == 10
        assert resp.output_tokens == 20
        assert resp.total_tokens == 30
        assert resp.finish_reason == "stop"

    @pytest.mark.asyncio
    async def test_uses_model_override(self):
        """complete() sends the model override from the request."""
        sent_bodies = []

        def handler(req: httpx.Request) -> httpx.Response:
            sent_bodies.append(json.loads(req.content))
            return httpx.Response(200, content=_chat_response("ok", model="mistral"))

        provider = _make_provider(httpx.MockTransport(handler))
        request = CompletionRequest(
            messages=[Message(role="user", content="hi")],
            model="mistral",
        )
        await provider.complete(request)

        assert sent_bodies[0]["model"] == "mistral"

    @pytest.mark.asyncio
    async def test_raises_on_http_error(self):
        """complete() propagates HTTP errors."""
        transport = httpx.MockTransport(
            lambda req: httpx.Response(503, text="Service Unavailable")
        )
        provider = _make_provider(transport)

        with pytest.raises(httpx.HTTPStatusError):
            await provider.complete(_simple_request())


# ────────────────────────────────────────────────────────────────────────────
#  Tests: stream()
# ────────────────────────────────────────────────────────────────────────────

class TestStream:
    @pytest.mark.asyncio
    async def test_yields_tokens(self):
        """stream() yields each token fragment from the chunked response."""
        tokens = ["Hello", " world", "!"]
        transport = httpx.MockTransport(
            lambda req: httpx.Response(200, content=_stream_chunks(tokens))
        )
        provider = _make_provider(transport)

        collected = []
        async for token in provider.stream(_simple_request()):
            collected.append(token)

        assert collected == tokens

    @pytest.mark.asyncio
    async def test_skips_empty_tokens(self):
        """stream() skips chunks with empty content."""
        # The final 'done' chunk typically has empty content
        tokens = ["Hello", ""]
        transport = httpx.MockTransport(
            lambda req: httpx.Response(200, content=_stream_chunks(tokens))
        )
        provider = _make_provider(transport)

        collected = []
        async for token in provider.stream(_simple_request()):
            collected.append(token)

        # Empty string should not be yielded
        assert "" not in collected
        assert "Hello" in collected

    @pytest.mark.asyncio
    async def test_raises_on_http_error(self):
        """stream() propagates HTTP errors."""
        transport = httpx.MockTransport(
            lambda req: httpx.Response(500, text="Internal Server Error")
        )
        provider = _make_provider(transport)

        with pytest.raises(httpx.HTTPStatusError):
            async for _ in provider.stream(_simple_request()):
                pass


# ────────────────────────────────────────────────────────────────────────────
#  Tests: embed()
# ────────────────────────────────────────────────────────────────────────────

class TestEmbed:
    @pytest.mark.asyncio
    async def test_returns_vector(self):
        """embed() returns the embedding list from Ollama."""
        transport = httpx.MockTransport(
            lambda req: httpx.Response(200, content=_embed_response(dims=4))
        )
        provider = _make_provider(transport)

        vector = await provider.embed("hello world")

        assert isinstance(vector, list)
        assert len(vector) == 4
        assert all(isinstance(v, float) for v in vector)

    @pytest.mark.asyncio
    async def test_raises_on_empty_embedding(self):
        """embed() raises ValueError when Ollama returns an empty embedding."""
        transport = httpx.MockTransport(
            lambda req: httpx.Response(200, content=json.dumps({"embedding": []}).encode())
        )
        provider = _make_provider(transport)

        with pytest.raises(ValueError, match="empty embedding"):
            await provider.embed("hello")


# ────────────────────────────────────────────────────────────────────────────
#  Tests: health_check()
# ────────────────────────────────────────────────────────────────────────────

class TestHealthCheck:
    @pytest.mark.asyncio
    async def test_returns_true_when_healthy(self):
        transport = httpx.MockTransport(
            lambda req: httpx.Response(200, content=_tags_response(["llama3"]))
        )
        provider = _make_provider(transport)

        assert await provider.health_check() is True

    @pytest.mark.asyncio
    async def test_returns_false_on_connection_error(self):
        """health_check() returns False (not raises) when Ollama is unreachable."""
        def raise_connect_error(req):
            raise httpx.ConnectError("Connection refused")

        provider = _make_provider(httpx.MockTransport(raise_connect_error))

        assert await provider.health_check() is False

    @pytest.mark.asyncio
    async def test_returns_false_on_non_200(self):
        transport = httpx.MockTransport(
            lambda req: httpx.Response(503, text="down")
        )
        provider = _make_provider(transport)

        assert await provider.health_check() is False
