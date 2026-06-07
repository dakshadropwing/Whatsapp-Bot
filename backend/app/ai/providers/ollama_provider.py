"""
Ollama provider — local LLM inference via the Ollama REST API.

Endpoints used:
  POST /api/chat        → chat completion (streaming & non-streaming)
  POST /api/embeddings  → text embeddings
  GET  /api/tags        → health / model list check
"""
from __future__ import annotations

import json
import logging
from typing import Any, AsyncIterator, Optional

import httpx

from app.ai.providers.base_provider import (
    BaseAIProvider,
    CompletionRequest,
    CompletionResponse,
    ToolCall,
)

logger = logging.getLogger(__name__)


class OllamaProvider(BaseAIProvider):
    """
    AI provider that talks to a locally-running Ollama instance.

    Configuration (passed via ProviderFactory / __init__ kwargs):
        base_url  (str)  – Ollama server URL, default: http://localhost:11434
        model     (str)  – Default model name, default: llama3
    """

    provider_name = "ollama"

    # ------------------------------------------------------------------ #
    #  Step 1 · Configure the HTTP client                                  #
    # ------------------------------------------------------------------ #

    def _configure(self, **kwargs: Any) -> None:
        """
        Initialise the underlying httpx.AsyncClient.

        We strip a trailing slash from base_url so all endpoint paths can
        start with '/' without accidentally creating double-slashes.
        """
        self._base_url: str = str(
            kwargs.get("base_url", "http://localhost:11434")
        ).rstrip("/")
        self._model: str = str(kwargs.get("model", "llama3"))

        # httpx.AsyncClient is reused across requests for connection pooling.
        self._client: httpx.AsyncClient = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(
                connect=10.0,   # seconds to establish TCP connection
                read=120.0,     # seconds to wait for a response body chunk
                write=30.0,     # seconds for sending request body
                pool=5.0,       # seconds waiting for a free connection slot
            ),
            headers={"Content-Type": "application/json"},
        )
        logger.info(
            "OllamaProvider configured — base_url=%s  model=%s",
            self._base_url,
            self._model,
        )

    # ------------------------------------------------------------------ #
    #  Internal helpers                                                    #
    # ------------------------------------------------------------------ #

    def _resolve_model(self, request_model: Optional[str]) -> str:
        """Return request-level model override, or the provider default."""
        return request_model or self._model

    @staticmethod
    def _messages_to_ollama(request: CompletionRequest) -> list[dict]:
        """
        Convert our internal Message dataclasses into the JSON array that
        Ollama's /api/chat endpoint expects:
          [{"role": "user"|"assistant"|"system", "content": "..."}]
        """
        return [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]

    @staticmethod
    def _build_options(request: CompletionRequest) -> dict:
        """
        Map CompletionRequest sampling params to Ollama's 'options' dict.
        Ollama uses the same names as llama.cpp / Modelfile.
        """
        opts: dict = {
            "temperature": request.temperature,
            "top_p": request.top_p,
        }
        # Only pass num_predict when the caller set a positive limit.
        if request.max_tokens and request.max_tokens > 0:
            opts["num_predict"] = request.max_tokens
        return opts

    # ------------------------------------------------------------------ #
    #  Step 2 · One-shot completion                                        #
    # ------------------------------------------------------------------ #

    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """
        POST /api/chat  (stream=false)

        Sends the full message history and waits for a complete response.
        Returns a CompletionResponse with token counts taken from Ollama's
        'prompt_eval_count' / 'eval_count' fields.
        """
        model = self._resolve_model(request.model)
        payload = {
            "model": model,
            "messages": self._messages_to_ollama(request),
            "stream": False,
            "options": self._build_options(request),
        }

        logger.debug("OllamaProvider.complete → model=%s", model)

        try:
            response = await self._client.post("/api/chat", json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Ollama HTTP error %s: %s", exc.response.status_code, exc.response.text
            )
            raise
        except httpx.RequestError as exc:
            logger.error("Ollama request failed: %s", exc)
            raise

        data = response.json()

        # Extract the assistant message content
        content: str = data.get("message", {}).get("content", "")

        # Token usage (Ollama may omit these; default to 0)
        input_tokens: int = data.get("prompt_eval_count", 0)
        output_tokens: int = data.get("eval_count", 0)
        finish_reason: str = "stop" if data.get("done", True) else "length"

        return CompletionResponse(
            content=content,
            model=data.get("model", model),
            provider=self.provider_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            finish_reason=finish_reason,
            raw_response=data,
        )

    # ------------------------------------------------------------------ #
    #  Step 3 · Streaming completion                                       #
    # ------------------------------------------------------------------ #

    async def stream(self, request: CompletionRequest) -> AsyncIterator[str]:
        """
        POST /api/chat  (stream=true)

        Ollama sends newline-delimited JSON objects while generating:
          {"message": {"content": "Hello"}, "done": false}
          ...
          {"message": {"content": ""}, "done": true, "eval_count": 42, ...}

        We yield each non-empty content fragment as a plain string token.
        """
        model = self._resolve_model(request.model)
        payload = {
            "model": model,
            "messages": self._messages_to_ollama(request),
            "stream": True,
            "options": self._build_options(request),
        }

        logger.debug("OllamaProvider.stream → model=%s", model)

        try:
            async with self._client.stream(
                "POST", "/api/chat", json=payload
            ) as response:
                response.raise_for_status()

                async for raw_line in response.aiter_lines():
                    # Skip blank lines (keep-alive)
                    if not raw_line.strip():
                        continue

                    try:
                        chunk = json.loads(raw_line)
                    except json.JSONDecodeError:
                        logger.warning(
                            "OllamaProvider: could not parse line: %s", raw_line
                        )
                        continue

                    token: str = chunk.get("message", {}).get("content", "")
                    if token:
                        yield token

                    # Ollama sets done=true on the final summary object
                    if chunk.get("done", False):
                        break

        except httpx.HTTPStatusError as exc:
            logger.error(
                "Ollama stream HTTP error %s: %s",
                exc.response.status_code,
                exc.response.text,
            )
            raise
        except httpx.RequestError as exc:
            logger.error("Ollama stream request failed: %s", exc)
            raise

    # ------------------------------------------------------------------ #
    #  Step 4 · Embeddings                                                 #
    # ------------------------------------------------------------------ #

    async def embed(self, text: str) -> list[float]:
        """
        POST /api/embeddings

        Uses a dedicated embedding model if configured (e.g. nomic-embed-text),
        otherwise falls back to the default chat model.

        Payload:  {"model": "...", "prompt": "<text>"}
        Response: {"embedding": [0.123, -0.456, ...]}
        """
        # Many users run a separate embedding model alongside their chat model.
        # Prefer a dedicated embedding model attribute if set; fall back to chat model.
        embed_model: str = getattr(self, "_embed_model", None) or self._model

        payload = {
            "model": embed_model,
            "prompt": text,
        }

        logger.debug("OllamaProvider.embed → model=%s", embed_model)

        try:
            response = await self._client.post("/api/embeddings", json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Ollama embed HTTP error %s: %s",
                exc.response.status_code,
                exc.response.text,
            )
            raise
        except httpx.RequestError as exc:
            logger.error("Ollama embed request failed: %s", exc)
            raise

        data = response.json()
        embedding: list[float] = data.get("embedding", [])

        if not embedding:
            raise ValueError(
                f"Ollama returned an empty embedding for model '{embed_model}'. "
                "Ensure the model supports embeddings (e.g. nomic-embed-text)."
            )

        return embedding

    # ------------------------------------------------------------------ #
    #  Step 5 · Health check                                               #
    # ------------------------------------------------------------------ #

    async def health_check(self) -> bool:
        """
        GET /api/tags

        Returns True if Ollama is reachable and responds with a 200 OK.
        The /api/tags endpoint lists locally available models — it's a
        lightweight, side-effect-free probe.
        """
        try:
            response = await self._client.get("/api/tags")
            is_healthy = response.status_code == 200
            if is_healthy:
                models = [m.get("name") for m in response.json().get("models", [])]
                logger.debug("Ollama healthy — available models: %s", models)
            else:
                logger.warning(
                    "Ollama health check returned HTTP %s", response.status_code
                )
            return is_healthy
        except (httpx.RequestError, httpx.HTTPStatusError) as exc:
            logger.warning("Ollama health check failed: %s", exc)
            return False

    # ------------------------------------------------------------------ #
    #  Clean-up                                                            #
    # ------------------------------------------------------------------ #

    async def aclose(self) -> None:
        """Close the underlying HTTP client and release connections."""
        await self._client.aclose()
