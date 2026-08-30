"""m1 screening results + demo seed

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-30

"""
from __future__ import annotations

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

TENANT = "00000000-0000-0000-0000-000000000001"
PRESET = "00000000-0000-0000-0000-000000000010"
STAGES = [
    ("00000000-0000-0000-0000-000000000020", "Скрининг", 0, "screening"),
    ("00000000-0000-0000-0000-000000000021", "Интервью", 1, "interview"),
    ("00000000-0000-0000-0000-000000000022", "Оффер", 2, "offer"),
    ("00000000-0000-0000-0000-000000000023", "Найм", 3, "hired"),
]

M1_TABLE = "m1_screening_results"


def upgrade() -> None:
    op.execute(
        f"""CREATE TABLE {M1_TABLE} (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            application_id uuid NOT NULL,
            vacancy_id uuid NOT NULL,
            candidate_id uuid NOT NULL,
            requirement_set_id uuid,
            total_score double precision,
            recommendation text,
            confidence double precision,
            per_criterion jsonb,
            model text,
            prompt_version integer,
            ai_run_id uuid,
            status text DEFAULT 'completed',
            is_stale boolean DEFAULT false,
            created_at timestamptz DEFAULT now() NOT NULL,
            updated_at timestamptz DEFAULT now() NOT NULL
        )"""
    )
    op.execute(f"CREATE INDEX ix_{M1_TABLE}_application ON {M1_TABLE} (application_id)")
    op.execute(f"CREATE INDEX ix_{M1_TABLE}_vacancy ON {M1_TABLE} (vacancy_id)")
    op.execute(f"ALTER TABLE {M1_TABLE} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {M1_TABLE} FORCE ROW LEVEL SECURITY")
    op.execute(
        f"CREATE POLICY tenant_isolation ON {M1_TABLE} "
        "USING (tenant_id = current_setting('app.tenant_id')::uuid)"
    )

    op.execute(
        f"INSERT INTO tenants (id, name, slug, is_active) "
        f"VALUES ('{TENANT}', 'Demo', 'demo', true) ON CONFLICT (slug) DO NOTHING"
    )
    op.execute(
        f"INSERT INTO funnel_presets (id, tenant_id, name, is_default) "
        f"VALUES ('{PRESET}', '{TENANT}', 'Default', true) ON CONFLICT DO NOTHING"
    )
    for sid, name, order_index, stage_type in STAGES:
        op.execute(
            f"INSERT INTO funnel_stages "
            f"(id, tenant_id, preset_id, name, order_index, stage_type) "
            f"VALUES ('{sid}', '{TENANT}', '{PRESET}', '{name}', "
            f"{order_index}, '{stage_type}') ON CONFLICT DO NOTHING"
        )
    for task in ("m1.criteria.generate", "m1.screening.score"):
        op.execute(
            f"INSERT INTO ai_task_routes (tenant_id, task, provider, model) "
            f"VALUES ('{TENANT}', '{task}', 'openai', 'gpt-4o-mini') "
            f"ON CONFLICT DO NOTHING"
        )
    op.execute(
        f"INSERT INTO feature_flags (tenant_id, key, enabled) "
        f"VALUES ('{TENANT}', 'm1_screening', true) ON CONFLICT DO NOTHING"
    )


def downgrade() -> None:
    op.execute(f"DROP TABLE IF EXISTS {M1_TABLE} CASCADE")
