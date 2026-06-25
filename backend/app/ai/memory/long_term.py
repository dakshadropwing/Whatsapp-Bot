"""
Long-Term Memory — PostgreSQL JSONB-backed contact profile.

Stores persistent facts about a contact that survive across conversations.
Uses the existing `conversations.context` JSONB column — no new migration needed.

Profile structure (stored inside context JSONB):
{
  "memory": {
    "user_name":    "Daksha",
    "language":     "en",
    "preferences":  {"notifications": true, "tone": "friendly"},
    "key_facts":    ["is a developer", "prefers Python"],
    "last_intent":  "support",
    "total_turns":  42,
    "last_seen":    "2026-06-07T15:00:00Z"
  }
}

The "memory" key is namespaced inside `context` to avoid collisions with
other data stored there by the rest of the application.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ── Key inside the JSONB context column ──────────────────────────────────────
_MEMORY_KEY = "memory"


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class LongTermMemory:
    """
    Reads and writes persistent contact facts using the Conversation.context
    JSONB column in PostgreSQL.

    This class is intentionally database-agnostic in its interface — it
    receives a `db_session` on each call so it can be used both inside
    Flask app context (sync) and from async tasks with a passed session.

    For now, all methods are synchronous (matching Flask-SQLAlchemy usage).
    They can be easily made async if you switch to full async SQLAlchemy.
    """

    # ── Read ──────────────────────────────────────────────────────────────────

    def get_profile(self, conversation, db_session=None) -> dict:
        """
        Load the memory profile from a Conversation ORM object.

        Args:
            conversation: a Conversation SQLAlchemy model instance
            db_session: optional — not needed if conversation is already loaded

        Returns:
            dict with keys: user_name, language, preferences, key_facts,
                            last_intent, total_turns, last_seen
        """
        context: dict = conversation.context or {}
        return context.get(_MEMORY_KEY, {})

    def get_profile_by_id(
        self, conversation_id: str, db_session
    ) -> dict:
        """
        Load the memory profile by conversation UUID (performs a DB query).

        Args:
            conversation_id: string UUID of the conversation
            db_session: active SQLAlchemy session

        Returns:
            dict profile, or empty dict if conversation not found
        """
        from app.models.conversation import Conversation
        import uuid

        try:
            convo = db_session.query(Conversation).filter_by(
                id=uuid.UUID(conversation_id)
            ).first()
            if not convo:
                logger.warning(
                    "LongTermMemory: conversation %s not found", conversation_id
                )
                return {}
            return self.get_profile(convo)
        except Exception as exc:
            logger.error("LongTermMemory.get_profile_by_id error: %s", exc)
            return {}

    # ── Write ─────────────────────────────────────────────────────────────────

    def update_fact(
        self,
        conversation,
        key: str,
        value: Any,
        db_session,
    ) -> None:
        """
        Upsert a single fact into the contact's memory profile.

        Example:
            memory.update_fact(convo, "user_name", "Daksha", db)
            memory.update_fact(convo, "last_intent", "support", db)

        Args:
            conversation: Conversation ORM instance
            key: fact name (e.g. "user_name", "language")
            value: fact value (any JSON-serialisable type)
            db_session: active SQLAlchemy session (needed to flush)
        """
        context: dict = dict(conversation.context or {})
        profile: dict = dict(context.get(_MEMORY_KEY, {}))

        profile[key] = value
        profile["last_seen"] = _utcnow_iso()
        context[_MEMORY_KEY] = profile

        # SQLAlchemy JSONB mutation tracking — reassign the whole dict
        conversation.context = context
        db_session.add(conversation)
        db_session.flush()

        logger.debug(
            "LongTermMemory: updated fact '%s' for conversation=%s",
            key,
            conversation.id,
        )

    def append_key_fact(
        self,
        conversation,
        fact: str,
        db_session,
        max_facts: int = 20,
    ) -> None:
        """
        Append a free-text fact to the 'key_facts' list (e.g. "prefers Python").

        Duplicate facts are ignored. List is capped at max_facts entries.
        """
        context: dict = dict(conversation.context or {})
        profile: dict = dict(context.get(_MEMORY_KEY, {}))

        facts: list = list(profile.get("key_facts", []))
        if fact not in facts:
            facts.append(fact)
            if len(facts) > max_facts:
                facts = facts[-max_facts:]   # keep most recent
            profile["key_facts"] = facts
            profile["last_seen"] = _utcnow_iso()
            context[_MEMORY_KEY] = profile
            conversation.context = context
            db_session.add(conversation)
            db_session.flush()

    def increment_turn_count(self, conversation, db_session) -> int:
        """Increment total_turns counter. Returns the new count."""
        context: dict = dict(conversation.context or {})
        profile: dict = dict(context.get(_MEMORY_KEY, {}))

        new_count = profile.get("total_turns", 0) + 1
        profile["total_turns"] = new_count
        profile["last_seen"] = _utcnow_iso()
        context[_MEMORY_KEY] = profile
        conversation.context = context
        db_session.add(conversation)
        db_session.flush()

        return new_count

    # ── Summary (for system prompt injection) ────────────────────────────────

    def get_summary(self, conversation) -> str:
        """
        Build a concise text summary of the profile to inject into the
        AI system prompt.

        Example output:
            "User info: name=Daksha, language=en.
             Known facts: is a developer, prefers Python.
             Last intent: support. Total conversations: 42."

        Returns empty string if no profile exists yet.
        """
        profile = self.get_profile(conversation)
        if not profile:
            return ""

        parts: list[str] = []

        # Basic identity
        identity_parts = []
        if profile.get("user_name"):
            identity_parts.append(f"name={profile['user_name']}")
        if profile.get("language"):
            identity_parts.append(f"language={profile['language']}")
        if identity_parts:
            parts.append("User info: " + ", ".join(identity_parts) + ".")

        # Preferences
        prefs = profile.get("preferences", {})
        if prefs:
            pref_str = ", ".join(f"{k}={v}" for k, v in prefs.items())
            parts.append(f"Preferences: {pref_str}.")

        # Key facts
        facts = profile.get("key_facts", [])
        if facts:
            parts.append("Known facts: " + "; ".join(facts) + ".")

        # Last intent
        if profile.get("last_intent"):
            parts.append(f"Last intent: {profile['last_intent']}.")

        # Engagement stats
        if profile.get("total_turns"):
            parts.append(f"Total conversation turns: {profile['total_turns']}.")

        return " ".join(parts)

    # ── Clear ─────────────────────────────────────────────────────────────────

    def reset(self, conversation, db_session) -> None:
        """Remove the entire memory profile for this conversation's contact."""
        context: dict = dict(conversation.context or {})
        context.pop(_MEMORY_KEY, None)
        conversation.context = context
        db_session.add(conversation)
        db_session.flush()
        logger.debug(
            "LongTermMemory: reset profile for conversation=%s", conversation.id
        )
