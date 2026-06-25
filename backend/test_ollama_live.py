"""
Interactive live chat with OllamaProvider.

Run:
    python3 test_ollama_live.py
"""
import asyncio
import sys
import os
import types

# ── Bypass app/__init__.py (avoids needing Flask) ────────────────────────────
_fake_app = types.ModuleType("app")
_fake_app.__path__ = [os.path.join(os.path.dirname(__file__), "app")]
_fake_app.__package__ = "app"
sys.modules.setdefault("app", _fake_app)
# ─────────────────────────────────────────────────────────────────────────────

from app.ai.providers.ollama_provider import OllamaProvider
from app.ai.providers.base_provider import CompletionRequest, Message

BASE_URL = "http://localhost:11434"
MODEL    = "llama3.2:1b"


async def main():
    p = OllamaProvider(base_url=BASE_URL, model=MODEL)

    # Health check first
    if not await p.health_check():
        print("❌ Ollama is not running. Start it with: ollama serve")
        await p.aclose()
        return

    print(f"✅ Connected to Ollama  |  model: {MODEL}")
    print("   Type your prompt and press Enter. Type 'quit' to exit.\n")

    history: list[Message] = []   # keeps the full conversation

    while True:
        # ── Get user input ────────────────────────────────────────────────────
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        # ── Add to history and send ───────────────────────────────────────────
        history.append(Message(role="user", content=user_input))

        req = CompletionRequest(
            messages=history,
            temperature=0.7,
        )

        print(f"\nOllama ({MODEL}): ", end="", flush=True)

        # Stream the response token by token
        full_reply = ""
        async for token in p.stream(req):
            print(token, end="", flush=True)
            full_reply += token

        print("\n")  # newline after response

        # Add assistant reply to history so the next turn has context
        history.append(Message(role="assistant", content=full_reply))

    await p.aclose()


if __name__ == "__main__":
    asyncio.run(main())
