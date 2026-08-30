"""m4 search maps

Revision ID: 0005
Revises: 0004
Create Date: 2026-08-30

"""

from __future__ import annotations

from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None

M4_TABLE = "m4_search_maps"


def upgrade() -> None:
    op.execute(
        f"""CREATE TABLE {M4_TABLE} (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            vacancy_id uuid NOT NULL,
            version_no integer NOT NULL DEFAULT 1,
            status text NOT NULL DEFAULT 'draft',
            role_ontology jsonb,
            donors jsonb,
            hypotheses jsonb,
            anti_map jsonb,
            term_pool jsonb,
            query_passports jsonb,
            justifications jsonb,
            model text,
            prompt_version integer,
            created_at timestamptz DEFAULT now() NOT NULL,
            updated_at timestamptz DEFAULT now() NOT NULL
        )"""
    )
    op.execute(f"CREATE INDEX ix_{M4_TABLE}_vacancy ON {M4_TABLE} (vacancy_id, version_no DESC)")
    op.execute(f"ALTER TABLE {M4_TABLE} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {M4_TABLE} FORCE ROW LEVEL SECURITY")
    op.execute(
        f"CREATE POLICY tenant_isolation ON {M4_TABLE} "
        "USING (tenant_id = current_setting('app.tenant_id')::uuid)"
    )


def downgrade() -> None:
    op.execute(f"DROP TABLE IF EXISTS {M4_TABLE} CASCADE")
