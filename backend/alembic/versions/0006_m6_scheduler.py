"""m6 scheduler

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-30

"""

from __future__ import annotations

from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None

INTERVIEWS = "m6_interviews"
SLOTS = "m6_availability_slots"


def upgrade() -> None:
    op.execute(
        f"""CREATE TABLE {INTERVIEWS} (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            application_id uuid NOT NULL,
            vacancy_id uuid NOT NULL,
            candidate_id uuid NOT NULL,
            scheduled_at timestamptz NOT NULL,
            duration_min integer NOT NULL DEFAULT 60,
            status text NOT NULL DEFAULT 'scheduled',
            location text,
            organizer_id uuid,
            feedback_decision text,
            feedback_notes text,
            feedback_per_question jsonb,
            cancel_reason text,
            created_at timestamptz DEFAULT now() NOT NULL,
            updated_at timestamptz DEFAULT now() NOT NULL
        )"""
    )
    op.execute(f"CREATE INDEX ix_{INTERVIEWS}_application ON {INTERVIEWS} (application_id)")
    op.execute(f"CREATE INDEX ix_{INTERVIEWS}_vacancy ON {INTERVIEWS} (vacancy_id, scheduled_at)")

    op.execute(
        f"""CREATE TABLE {SLOTS} (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            user_id uuid NOT NULL,
            day_of_week integer NOT NULL,
            start_time text NOT NULL,
            end_time text NOT NULL,
            is_block boolean NOT NULL DEFAULT false,
            created_at timestamptz DEFAULT now() NOT NULL,
            updated_at timestamptz DEFAULT now() NOT NULL
        )"""
    )
    op.execute(f"CREATE INDEX ix_{SLOTS}_user ON {SLOTS} (user_id)")

    for table in (INTERVIEWS, SLOTS):
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY tenant_isolation ON {table} "
            "USING (tenant_id = current_setting('app.tenant_id')::uuid)"
        )


def downgrade() -> None:
    op.execute(f"DROP TABLE IF EXISTS {SLOTS} CASCADE")
    op.execute(f"DROP TABLE IF EXISTS {INTERVIEWS} CASCADE")
