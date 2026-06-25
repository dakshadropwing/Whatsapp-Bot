"""
Health check script to verify platform dependencies.
Checks Database connection, Redis connection, and AI Key configurations.
"""
from __future__ import annotations

import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.factory import create_app
from app.extensions import db
from app.core.config.settings import get_settings


def check_health() -> bool:
    print("🏥 Running platform health check...")
    settings = get_settings()
    all_healthy = True

    # ── 1. Check Database ────────────────────────────────────────────────
    try:
        app = create_app()
        with app.app_context():
            # Run simple query
            db.session.execute(db.text("SELECT 1"))
            print("   ✅ Database: Connected successfully")
    except Exception as exc:
        print(f"   ❌ Database: Connection failed ({exc})")
        all_healthy = False

    # ── 2. Check Redis ───────────────────────────────────────────────────
    try:
        import redis
        r = redis.Redis.from_url(settings.REDIS_URL, socket_timeout=3)
        r.ping()
        print("   ✅ Redis: Connected successfully")
    except Exception as exc:
        print(f"   ❌ Redis: Connection failed ({exc})")
        all_healthy = False

    # ── 3. Check AI Provider Key Configuration ──────────────────────────
    ai_provider = settings.DEFAULT_AI_PROVIDER
    print(f"   ℹ️  Default AI Provider: {ai_provider}")
    
    if ai_provider == "gemini":
        key = settings.GOOGLE_AI_API_KEY
        if key and not key.startswith("AIza"):
            print("   ⚠️  Gemini: API Key is configured but might be invalid (should start with AIza)")
        elif key:
            print("   ✅ Gemini: API Key configured")
        else:
            print("   ❌ Gemini: GOOGLE_AI_API_KEY is missing in .env")
            all_healthy = False
    elif ai_provider == "ollama":
        url = settings.OLLAMA_BASE_URL
        print(f"   ℹ️  Ollama Server URL: {url}")
        # Test connection to Ollama if needed
        import httpx
        try:
            resp = httpx.get(f"{url}/api/tags", timeout=3)
            if resp.status_code == 200:
                print("   ✅ Ollama: Connected to local server successfully")
            else:
                print(f"   ⚠️  Ollama: Server responded with status {resp.status_code}")
        except Exception as exc:
            print(f"   ⚠️  Ollama: Could not connect to local server ({exc})")

    # ── 4. Encryption master key ────────────────────────────────────────
    enc_key = settings.ENCRYPTION_MASTER_KEY
    if enc_key and len(enc_key) > 0:
        print("   ✅ Encryption: ENCRYPTION_MASTER_KEY configured")
    else:
        print("   ❌ Encryption: ENCRYPTION_MASTER_KEY is missing in .env")
        all_healthy = False

    if all_healthy:
        print("\n🎉 All critical platform checks passed successfully!")
    else:
        print("\n❌ Platform health checks failed. Check configuration details above.")

    return all_healthy


if __name__ == "__main__":
    success = check_health()
    sys.exit(0 if success else 1)
