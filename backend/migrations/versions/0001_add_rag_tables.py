"""
Alembic migration: Add RAG tables (knowledge_bases, documents, document_chunks).

Revision:  0001_add_rag_tables
Created:   2026-06-08

Prerequisites:
    PostgreSQL pgvector extension must be installed on the server:
        CREATE EXTENSION IF NOT EXISTS vector;

    Python package:
        pip install pgvector  (already in requirements.txt)

Run:
    cd /Users/dakshabordekar/Whatsapp-Bot/backend
    flask db upgrade                  # if using Flask-Migrate
    # OR
    alembic upgrade head              # if using plain Alembic

Notes:
    - The IVFFlat ANN index for fast cosine search is commented out.
      Create it AFTER loading at least 1,000 rows for good performance:

      CREATE INDEX ix_chunk_emb_ivfflat
        ON document_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100);

      Use the second migration file (0002_add_ivfflat_index.py) for this.
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# Alembic identifiers
revision = "0001_add_rag_tables"
down_revision = None    # Set this to the last existing migration revision ID
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Enable pgvector extension ─────────────────────────────────────────
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # ── 1. knowledge_bases ────────────────────────────────────────────────
    op.create_table(
        "knowledge_bases",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name",        sa.String(255), nullable=False),
        sa.Column("description", sa.Text,        nullable=True),
        sa.Column("is_active",   sa.Boolean,     nullable=False, server_default="true"),
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
    op.create_index("ix_kb_org_id",   "knowledge_bases", ["organization_id"])
    op.create_index(
        "ix_kb_org_name", "knowledge_bases",
        ["organization_id", "name"], unique=True,
    )
    op.create_index("ix_kb_is_active", "knowledge_bases", ["is_active"])

    # ── 2. documents ──────────────────────────────────────────────────────
    op.create_table(
        "documents",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "knowledge_base_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("knowledge_bases.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name",           sa.String(512), nullable=False),
        sa.Column("source_type",    sa.String(50),  nullable=False, server_default="text"),
        sa.Column("source_url",     sa.Text,        nullable=True),
        sa.Column("raw_text",       sa.Text,        nullable=True),
        sa.Column("file_size_bytes",sa.BigInteger,  nullable=True),
        sa.Column("status",         sa.String(20),  nullable=False, server_default="pending"),
        sa.Column("error_message",  sa.Text,        nullable=True),
        sa.Column("chunk_count",    sa.Integer,     nullable=False, server_default="0"),
        sa.Column(
            "doc_metadata",
            postgresql.JSONB,
            nullable=False,
            server_default="'{}'",
        ),
        # Soft-delete
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
    op.create_index("ix_doc_kb_id",     "documents", ["knowledge_base_id"])
    op.create_index("ix_doc_status",    "documents", ["status"])
    op.create_index("ix_doc_kb_status", "documents", ["knowledge_base_id", "status"])
    op.create_index("ix_doc_deleted_at","documents", ["deleted_at"])

    # ── 3. document_chunks ────────────────────────────────────────────────
    op.create_table(
        "document_chunks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("content",     sa.Text,    nullable=False),
        sa.Column("token_count", sa.Integer, nullable=False, server_default="0"),
        # pgvector column — 768-dim float32 (text-embedding-004)
        sa.Column(
            "embedding",
            sa.Text,    # Alembic doesn't know Vector type; we alter after create
            nullable=True,
        ),
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

    # Convert the embedding column to pgvector type after table creation
    op.execute(
        "ALTER TABLE document_chunks "
        "ALTER COLUMN embedding TYPE vector(768) "
        "USING embedding::vector(768)"
    )

    op.create_index("ix_chunk_doc_id",  "document_chunks", ["document_id"])
    op.create_index("ix_chunk_doc_idx", "document_chunks", ["document_id", "chunk_index"])

    # NOTE: IVFFlat ANN index — create AFTER loading 1000+ rows.
    # Use migration 0002_add_ivfflat_index.py for this.


def downgrade() -> None:
    op.drop_table("document_chunks")
    op.drop_table("documents")
    op.drop_table("knowledge_bases")
    # Note: we intentionally do NOT drop the vector extension in downgrade
    # because other tables might be using it.
