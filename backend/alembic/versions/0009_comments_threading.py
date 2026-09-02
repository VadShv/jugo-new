"""comments threading + soft delete

Revision ID: 0009
Revises: 0008
Create Date: 2026-09-02

"""

from __future__ import annotations

from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE comment_threads "
        "ADD COLUMN IF NOT EXISTS application_id uuid, "
        "ADD COLUMN IF NOT EXISTS parent_id uuid REFERENCES comment_threads(id) ON DELETE CASCADE, "
        "ADD COLUMN IF NOT EXISTS updated_by uuid, "
        "ADD COLUMN IF NOT EXISTS deleted_at timestamptz"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_comment_threads_application "
        "ON comment_threads (application_id, created_at DESC)"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE comment_threads DROP COLUMN IF EXISTS deleted_at")
    op.execute("ALTER TABLE comment_threads DROP COLUMN IF EXISTS updated_by")
    op.execute("ALTER TABLE comment_threads DROP COLUMN IF EXISTS parent_id")
