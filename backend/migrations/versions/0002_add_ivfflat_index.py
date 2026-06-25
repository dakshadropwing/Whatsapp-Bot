"""
Alembic migration: Add IVFFlat ANN index on document_chunks.embedding.

Revision:  0002_add_ivfflat_index
Created:   2026-06-08

IMPORTANT: Run this migration ONLY after your document_chunks table has at
           least 1,000 rows. IVFFlat performs poorly on small datasets
           and may actually slow down small tables compared to a brute-force scan.

           The `lists` parameter (default: 100) should be approximately
           sqrt(number_of_rows). Adjust as your dataset grows.

Run after sufficient data is loaded:
    flask db upgrade           # Flask-Migrate
    # OR
    alembic upgrade head       # plain Alembic
"""
from __future__ import annotations

from alembic import op


revision = "0002_add_ivfflat_index"
down_revision = "0001_add_rag_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # IVFFlat index for fast approximate nearest-neighbor cosine search.
    # vector_cosine_ops = optimised for cosine similarity (<=> operator).
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_chunk_emb_ivfflat
        ON document_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_chunk_emb_ivfflat")
