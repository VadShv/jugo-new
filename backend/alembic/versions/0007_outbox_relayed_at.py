"""outbox relayed_at

Revision ID: 0007
Revises: 0006
Create Date: 2026-08-31

"""

from __future__ import annotations

from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE outbox_events ADD COLUMN relayed_at timestamptz")
    op.execute(
        "CREATE INDEX ix_outbox_events_unrelayed "
        "ON outbox_events (created_at) WHERE relayed_at IS NULL"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE outbox_events DROP COLUMN relayed_at")
