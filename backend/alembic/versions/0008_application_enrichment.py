"""application enrichment + optimistic locking

Revision ID: 0008
Revises: 0007
Create Date: 2026-09-01

"""

from __future__ import annotations

from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE applications
            ADD COLUMN version integer NOT NULL DEFAULT 1,
            ADD COLUMN stage_entered_at timestamptz,
            ADD COLUMN next_action_at timestamptz,
            ADD COLUMN owner_id uuid,
            ADD COLUMN salary_expectation text,
            ADD COLUMN rejection_reason_code text,
            ADD COLUMN rejection_comment text
        """
    )
    op.execute("CREATE INDEX ix_applications_owner ON applications (owner_id)")


def downgrade() -> None:
    op.execute("ALTER TABLE applications DROP COLUMN IF EXISTS rejection_comment")
    op.execute("ALTER TABLE applications DROP COLUMN IF EXISTS rejection_reason_code")
    op.execute("ALTER TABLE applications DROP COLUMN IF EXISTS salary_expectation")
    op.execute("ALTER TABLE applications DROP COLUMN IF EXISTS owner_id")
    op.execute("ALTER TABLE applications DROP COLUMN IF EXISTS next_action_at")
    op.execute("ALTER TABLE applications DROP COLUMN IF EXISTS stage_entered_at")
    op.execute("ALTER TABLE applications DROP COLUMN IF EXISTS version")
