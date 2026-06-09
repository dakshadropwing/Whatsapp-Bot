"""
Alembic migration: Add tickets and endpoint_configs tables.

Revision:  0003_add_tickets_and_endpoint_configs
Created:   2026-06-09
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Alembic identifiers
revision = "0003_add_tickets_and_endpoint_configs"
down_revision = "0002_add_ivfflat_index"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── 1. tickets ────────────────────────────────────────────────────────
    op.create_table(
        "tickets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conversations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "priority",
            sa.Enum("LOW", "MEDIUM", "HIGH", "URGENT", name="ticketpriority"),
            nullable=False,
            server_default="MEDIUM",
        ),
        sa.Column(
            "status",
            sa.Enum("OPEN", "IN_PROGRESS", "WAITING_ON_CUSTOMER", "RESOLVED", "CLOSED", name="ticketstatus"),
            nullable=False,
            server_default="OPEN",
        ),
        sa.Column(
            "assigned_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("contact_phone", sa.String(20), nullable=True),
        sa.Column("contact_name", sa.String(255), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_tickets_org_status", "tickets", ["organization_id", "status"])
    op.create_index("ix_tickets_org_priority", "tickets", ["organization_id", "priority"])
    op.create_index("ix_tickets_conversation", "tickets", ["conversation_id"])
    op.create_index("ix_tickets_created_at", "tickets", ["created_at"])

    # ── 2. endpoint_configs ───────────────────────────────────────────────
    op.create_table(
        "endpoint_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("url", sa.String(2048), nullable=False),
        sa.Column("method", sa.String(10), nullable=False, server_default="POST"),
        sa.Column("headers", postgresql.JSONB, nullable=False, server_default="'{}'"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index(
        "ix_endpoint_configs_org_name",
        "endpoint_configs",
        ["organization_id", "name"],
        unique=True,
    )
    op.create_index("ix_endpoint_configs_org_active", "endpoint_configs", ["organization_id", "is_active"])


def downgrade() -> None:
    op.drop_table("endpoint_configs")
    op.drop_table("tickets")
    # Drop types if needed, though they can remain in DB.
    op.execute("DROP TYPE IF EXISTS ticketpriority")
    op.execute("DROP TYPE IF EXISTS ticketstatus")
