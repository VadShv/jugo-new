"""reject reasons dictionary

Revision ID: 0011
Revises: 0010
Create Date: 2026-09-02

"""

from __future__ import annotations

from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None

TABLE = "reject_reasons"
TENANT = "00000000-0000-0000-0000-000000000001"

SEED = [
    ("no_match", "Не подходит по навыкам"),
    ("overqualified", "Квалификация превышает требования"),
    ("location", "Не подходит локация"),
    ("salary", "Зарплатные ожидания выше бюджета"),
    ("no_response", "Кандидат не вышел на связь"),
    ("failed_interview", "Не прошёл интервью"),
    ("duplicate", "Дубликат"),
    ("other", "Другое"),
]


def upgrade() -> None:
    op.execute(
        f"""CREATE TABLE {TABLE} (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            code text NOT NULL,
            label text NOT NULL,
            is_active boolean DEFAULT true,
            created_at timestamptz DEFAULT now() NOT NULL,
            UNIQUE (tenant_id, code)
        )"""
    )
    op.execute(f"ALTER TABLE {TABLE} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {TABLE} FORCE ROW LEVEL SECURITY")
    op.execute(
        f"CREATE POLICY tenant_isolation ON {TABLE} "
        "USING (tenant_id = current_setting('app.tenant_id', true)::uuid)"
    )
    for code, label in SEED:
        op.execute(
            f"INSERT INTO {TABLE} (tenant_id, code, label) "
            f"VALUES ('{TENANT}', '{code}', '{label}') "
            f"ON CONFLICT DO NOTHING"
        )


def downgrade() -> None:
    op.execute(f"DROP TABLE IF EXISTS {TABLE} CASCADE")
