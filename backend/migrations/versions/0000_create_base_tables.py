"""
Alembic migration: Create core database tables.

Revision:  0000_create_base_tables
Created:   2026-06-09
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Alembic identifiers
revision = "0000_create_base_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. organizations ──────────────────────────────────────────────────
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("website", sa.String(500), nullable=True),
        sa.Column("logo_url", sa.String(1000), nullable=True),
        sa.Column("plan", sa.String(50), nullable=False, server_default="starter"),
        sa.Column("max_users", sa.Integer, nullable=False, server_default="10"),
        sa.Column("max_agents", sa.Integer, nullable=False, server_default="5"),
        sa.Column("max_conversations_per_month", sa.Integer, nullable=False, server_default="1000"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("settings", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_organizations_slug", "organizations", ["slug"])
    op.create_index("ix_organizations_is_active", "organizations", ["is_active"])
    op.create_index("ix_organizations_created_at", "organizations", ["created_at"])

    # ── 2. roles ──────────────────────────────────────────────────────────
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(50), unique=True, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    # ── 3. users ──────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("username", sa.String(150), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("avatar_url", sa.String(1000), nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_superadmin", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("email_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("mfa_enabled", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("mfa_secret", sa.String(255), nullable=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("last_login_at", sa.String(50), nullable=True),
        sa.Column("last_login_ip", sa.String(45), nullable=True),
        sa.Column("preferences", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_users_email_org", "users", ["email", "organization_id"], unique=True)
    op.create_index("ix_users_organization_id", "users", ["organization_id"])
    op.create_index("ix_users_role_id", "users", ["role_id"])
    op.create_index("ix_users_is_active", "users", ["is_active"])

    # ── 4. whatsapp_accounts ──────────────────────────────────────────────
    op.create_table(
        "whatsapp_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("phone_number_id", sa.String(50), nullable=False),
        sa.Column("waba_id", sa.String(50), nullable=False),
        sa.Column("access_token", sa.Text, nullable=False),
        sa.Column("verify_token", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    # ── 5. ai_agents ──────────────────────────────────────────────────────
    op.create_table(
        "ai_agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("role_type", sa.String(50), nullable=False, server_default="support"),
        sa.Column("system_prompt", sa.Text, nullable=False),
        sa.Column("provider", sa.String(50), nullable=False, server_default="gemini"),
        sa.Column("model_name", sa.String(100), nullable=False, server_default="gemini-2.5-flash"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )

    # ── 6. conversations ──────────────────────────────────────────────────
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("whatsapp_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("whatsapp_accounts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("contact_phone", sa.String(20), nullable=False),
        sa.Column("contact_name", sa.String(255), nullable=True),
        sa.Column("contact_wa_id", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("channel", sa.String(50), nullable=False, server_default="whatsapp"),
        sa.Column("assigned_agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_agents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("assigned_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("context", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("tags", postgresql.JSONB, nullable=False, server_default=sa.text("'[]'")),
        sa.Column("priority", sa.String(20), nullable=False, server_default="normal"),
        sa.Column("message_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_message_at", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_conversations_org_contact", "conversations", ["organization_id", "contact_phone"])
    op.create_index("ix_conversations_status", "conversations", ["status"])
    op.create_index("ix_conversations_org_status", "conversations", ["organization_id", "status"])
    op.create_index("ix_conversations_wa_account", "conversations", ["whatsapp_account_id"])
    op.create_index("ix_conversations_created_at", "conversations", ["created_at"])

    # ── 7. messages ───────────────────────────────────────────────────────
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("wa_message_id", sa.String(255), nullable=True),
        sa.Column("direction", sa.String(50), nullable=False),
        sa.Column("message_type", sa.String(50), nullable=False, server_default="text"),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("body", sa.Text, nullable=True),
        sa.Column("media_url", sa.String(2000), nullable=True),
        sa.Column("media_type", sa.String(100), nullable=True),
        sa.Column("media_size", sa.Integer, nullable=True),
        sa.Column("raw_payload", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("ai_generated", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("ai_session_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tokens_used", sa.Integer, nullable=True),
        sa.Column("processing_time_ms", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])
    op.create_index("ix_messages_wa_message_id", "messages", ["wa_message_id"])
    op.create_index("ix_messages_org_created", "messages", ["organization_id", "created_at"])
    op.create_index("ix_messages_direction", "messages", ["direction"])
    op.create_index("ix_messages_status", "messages", ["status"])

    # ── 8. ai_sessions ────────────────────────────────────────────────────
    op.create_table(
        "ai_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_agents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("session_metadata", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
    )


def downgrade() -> None:
    op.drop_table("ai_sessions")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("ai_agents")
    op.drop_table("whatsapp_accounts")
    op.drop_table("users")
    op.drop_table("roles")
    op.drop_table("organizations")
