"""m2 risk reports

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-30

"""

from __future__ import annotations

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

M2_TABLE = "m2_risk_reports"


def upgrade() -> None:
    op.execute(
        f"""CREATE TABLE {M2_TABLE} (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            application_id uuid NOT NULL,
            candidate_id uuid NOT NULL,
            vacancy_id uuid NOT NULL,
            risk_level text,
            signals jsonb,
            top_risks jsonb,
            summary text,
            model text,
            prompt_version integer,
            ai_run_id uuid,
            status text DEFAULT 'completed',
            created_at timestamptz DEFAULT now() NOT NULL,
            updated_at timestamptz DEFAULT now() NOT NULL
        )"""
    )
    op.execute(f"CREATE INDEX ix_{M2_TABLE}_application ON {M2_TABLE} (application_id)")
    op.execute(f"CREATE INDEX ix_{M2_TABLE}_candidate ON {M2_TABLE} (candidate_id)")
    op.execute(f"ALTER TABLE {M2_TABLE} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {M2_TABLE} FORCE ROW LEVEL SECURITY")
    op.execute(
        f"CREATE POLICY tenant_isolation ON {M2_TABLE} "
        "USING (tenant_id = current_setting('app.tenant_id')::uuid)"
    )


def downgrade() -> None:
    op.execute(f"DROP TABLE IF EXISTS {M2_TABLE} CASCADE")
