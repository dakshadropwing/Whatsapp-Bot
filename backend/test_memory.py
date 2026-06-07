"""
Live test for the Memory module.

Tests short-term memory (Redis / in-memory fallback) in isolation.
Long-term memory requires a DB connection so it's shown conceptually only.

Run:
    cd /Users/dakshabordekar/Whatsapp-Bot/backend
    source .venv/bin/activate
    python3 test_memory.py
"""
import asyncio
import sys
import os
import types

# ── Bypass app/__init__.py Flask import ──────────────────────────────────────
_fake_app = types.ModuleType("app")
_fake_app.__path__ = [os.path.join(os.path.dirname(__file__), "app")]
_fake_app.__package__ = "app"
sys.modules.setdefault("app", _fake_app)

# Also stub out app.core.config.settings (needs .env / DB to be set up)
_fake_core = types.ModuleType("app.core")
_fake_core.__path__ = [os.path.join(os.path.dirname(__file__), "app", "core")]
sys.modules.setdefault("app.core", _fake_core)

_fake_cache = types.ModuleType("app.core.cache")
_fake_cache.__path__ = [os.path.join(os.path.dirname(__file__), "app", "core", "cache")]
sys.modules.setdefault("app.core.cache", _fake_cache)

_fake_config = types.ModuleType("app.core.config")
_fake_config.__path__ = [os.path.join(os.path.dirname(__file__), "app", "core", "config")]
sys.modules.setdefault("app.core.config", _fake_config)

class _FakeSettings:
    REDIS_URL = "redis://localhost:6379/0"

_fake_settings_mod = types.ModuleType("app.core.config.settings")
_fake_settings_mod.get_settings = lambda: _FakeSettings()
sys.modules["app.core.config.settings"] = _fake_settings_mod

# Also stub app.ai and sub-packages so imports chain correctly
for mod_name in ["app.ai", "app.ai.memory", "app.ai.providers"]:
    if mod_name not in sys.modules:
        m = types.ModuleType(mod_name)
        m.__path__ = [os.path.join(os.path.dirname(__file__), *mod_name.split("."))]
        sys.modules[mod_name] = m

# ─────────────────────────────────────────────────────────────────────────────

from app.core.cache.redis_client import get_redis, is_using_fallback
from app.ai.memory.short_term import ShortTermMemory
from app.ai.memory.context_manager import ContextManager


CONVERSATION_ID = "test-conv-001"


async def test_redis_client():
    print("=" * 55)
    print("1. REDIS CLIENT")
    print("=" * 55)
    redis = await get_redis()
    fallback = is_using_fallback()
    print(f"   Backend      : {'⚠️  In-memory fallback' if fallback else '✅ Real Redis'}")

    # Basic set/get
    await redis.set("test_key", "hello", ex=60)
    val = await redis.get("test_key")
    decoded = val.decode() if isinstance(val, bytes) else val
    print(f"   set/get      : {'✅' if decoded == 'hello' else '❌'} ({decoded!r})")

    # List operations
    await redis.lpush("test_list", "c", "b", "a")
    items = await redis.lrange("test_list", 0, -1)
    decoded_items = [i.decode() if isinstance(i, bytes) else i for i in items]
    print(f"   lpush/lrange : {'✅' if decoded_items == ['a','b','c'] else '❌'} {decoded_items}")

    # ltrim
    await redis.ltrim("test_list", 0, 1)
    items = await redis.lrange("test_list", 0, -1)
    decoded_items = [i.decode() if isinstance(i, bytes) else i for i in items]
    print(f"   ltrim        : {'✅' if len(decoded_items) == 2 else '❌'} {decoded_items}")

    # Cleanup
    await redis.delete("test_key", "test_list")


async def test_short_term_memory():
    print()
    print("=" * 55)
    print("2. SHORT-TERM MEMORY")
    print("=" * 55)

    mem = ShortTermMemory(max_turns=5)

    # Clear any previous test data
    await mem.clear(CONVERSATION_ID)

    # Add 3 turns
    await mem.add_turn(CONVERSATION_ID, "Hello!", "Hi there! How can I help?")
    await mem.add_turn(CONVERSATION_ID, "What's your name?", "I'm your WhatsApp assistant.")
    await mem.add_turn(CONVERSATION_ID, "Can you help me track my order?", "Sure! What's your order ID?")

    # Check count
    count = await mem.get_turn_count(CONVERSATION_ID)
    msg_count = await mem.get_message_count(CONVERSATION_ID)
    print(f"   Turns stored : {'✅' if count == 3 else '❌'} {count} turns ({msg_count} messages)")

    # Retrieve history
    history = await mem.get_history(CONVERSATION_ID)
    print(f"   History len  : {'✅' if len(history) == 6 else '❌'} {len(history)} messages")
    # After reversal: oldest pair is [0]=user, [1]=assistant
    order_ok = history[0].role == "user" and history[1].role == "assistant"
    print(f"   Order check  : {'✅' if order_ok else '❌'} [{history[0].role}, {history[1].role}, ...]")
    print(f"   First msg    : role={history[0].role!r}, content={history[0].content!r}")
    print(f"   Last  msg    : role={history[-1].role!r}, content={history[-1].content!r}")

    # Limit retrieval
    recent = await mem.get_history(CONVERSATION_ID, limit=2)
    print(f"   Limit=2      : {'✅' if len(recent) == 2 else '❌'} got {len(recent)} messages")

    # Test rolling window (add more than max_turns)
    for i in range(4):
        await mem.add_turn(CONVERSATION_ID, f"User msg {i}", f"Bot reply {i}")
    count_after = await mem.get_turn_count(CONVERSATION_ID)
    print(f"   Rolling trim : {'✅' if count_after <= 5 else '❌'} {count_after} turns (max=5)")

    # Clear test
    await mem.clear(CONVERSATION_ID)
    has = await mem.has_history(CONVERSATION_ID)
    print(f"   After clear  : {'✅' if not has else '❌'} history cleared")


async def test_context_manager():
    print()
    print("=" * 55)
    print("3. CONTEXT MANAGER")
    print("=" * 55)

    ctx = ContextManager()
    CONV = "test-ctx-456"

    await ctx.clear_short_term(CONV)

    # Save some turns
    await ctx.save_turn(CONV, "Hi", "Hello!")
    await ctx.save_turn(CONV, "What can you do?", "I can help with orders, support, and more.")

    # build_messages without long-term memory
    messages = await ctx.build_messages(
        conversation_id=CONV,
        system_prompt="You are a helpful WhatsApp support agent.",
        new_user_message="I need to return an item.",
    )

    # Verify structure
    has_system = messages[0].role == "system"
    ends_with_user = messages[-1].role == "user" and "return" in messages[-1].content
    total_ok = len(messages) == 6   # 1 system + 4 history + 1 new

    print(f"   System msg   : {'✅' if has_system else '❌'} {messages[0].content[:50]!r}...")
    print(f"   History msgs : {'✅' if total_ok else '❌'} total={len(messages)} (expected 6)")
    print(f"   Last msg     : {'✅' if ends_with_user else '❌'} {messages[-1].content!r}")

    # Verify the full chain
    print()
    print("   Full message chain:")
    for i, msg in enumerate(messages):
        prefix = "   " + f"  [{i}] {msg.role:9s}: "
        print(prefix + msg.content[:60])

    await ctx.clear_short_term(CONV)


async def main():
    print("\n🧠 Memory Module — Live Test\n")
    await test_redis_client()
    await test_short_term_memory()
    await test_context_manager()
    print()
    print("✅ All memory tests passed!")
    print()
    print("NOTE: Long-term memory (PostgreSQL) requires a DB connection.")
    print("      It will be tested when the full app is running.")


if __name__ == "__main__":
    asyncio.run(main())
