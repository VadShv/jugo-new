"""tasks table

Revision ID: 0010
Revises: 0009
Create Date: 2026-09-02

"""

from __future__ import annotations

from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None

TABLE = "tasks"


def upgrade() -> None:
    op.execute(
        f"""CREATE TABLE {TABLE} (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            application_id uuid NOT NULL,
            title text NOT NULL,
            description text,
            due_at timestamptz,
            assignee_id uuid,
            completed_at timestamptz,
            completed_by uuid,
            created_by uuid NOT NULL,
            created_at timestamptz DEFAULT now() NOT NULL,
            updated_at timestamptz DEFAULT now() NOT NULL
        )"""
    )
    op.execute(f"CREATE INDEX ix_{TABLE}_application ON {TABLE} (application_id, due_at)")
    op.execute(f"CREATE INDEX ix_{TABLE}_assignee ON {TABLE} (assignee_id, completed_at)")
    op.execute(f"ALTER TABLE {TABLE} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {TABLE} FORCE ROW LEVEL SECURITY")
    op.execute(
        f"CREATE POLICY tenant_isolation ON {TABLE} "
        "USING (tenant_id = current_setting('app.tenant_id', true)::uuid)"
    )


def downgrade() -> None:
    op.execute(f"DROP TABLE IF EXISTS {TABLE} CASCADE")
