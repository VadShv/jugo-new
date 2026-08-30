"""m3 question sets

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-30

"""

from __future__ import annotations

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None

M3_TABLE = "m3_question_sets"


def upgrade() -> None:
    op.execute(
        f"""CREATE TABLE {M3_TABLE} (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            vacancy_id uuid NOT NULL,
            application_id uuid,
            version_no integer NOT NULL DEFAULT 1,
            status text NOT NULL DEFAULT 'draft',
            origin text NOT NULL DEFAULT 'ai',
            manual_edited boolean NOT NULL DEFAULT false,
            questions jsonb NOT NULL DEFAULT '[]',
            model text,
            prompt_version integer,
            ai_run_id uuid,
            created_at timestamptz DEFAULT now() NOT NULL,
            updated_at timestamptz DEFAULT now() NOT NULL
        )"""
    )
    op.execute(f"CREATE INDEX ix_{M3_TABLE}_vacancy ON {M3_TABLE} (vacancy_id, version_no DESC)")
    op.execute(f"CREATE INDEX ix_{M3_TABLE}_application ON {M3_TABLE} (application_id)")
    op.execute(f"ALTER TABLE {M3_TABLE} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {M3_TABLE} FORCE ROW LEVEL SECURITY")
    op.execute(
        f"CREATE POLICY tenant_isolation ON {M3_TABLE} "
        "USING (tenant_id = current_setting('app.tenant_id')::uuid)"
    )


def downgrade() -> None:
    op.execute(f"DROP TABLE IF EXISTS {M3_TABLE} CASCADE")
