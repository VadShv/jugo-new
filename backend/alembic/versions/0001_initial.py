"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-30 00:00:00.000000

"""
from __future__ import annotations

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

DOMAIN_TABLES = [
    "tenant_members",
    "candidates",
    "candidate_contacts",
    "candidate_facts",
    "resume_sources",
    "resume_versions",
    "vacancies",
    "vacancy_requirement_sets",
    "funnel_presets",
    "funnel_stages",
    "applications",
    "stage_transitions",
    "hm_decisions",
    "outbox_events",
    "audit_log",
    "ai_runs",
    "prompts",
    "ai_task_routes",
    "feature_flags",
    "search_synonyms",
    "webhook_subscriptions",
    "comment_threads",
    "merge_log",
    "consents",
]


def _rls(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
    op.execute(
        f"CREATE POLICY tenant_isolation ON {table} "
        f"USING (tenant_id = current_setting('app.tenant_id')::uuid)"
    )


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS ltree")
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.execute(
        """
        CREATE TABLE tenants (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            name text NOT NULL,
            slug text NOT NULL UNIQUE,
            is_active boolean NOT NULL DEFAULT true,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE users (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            email text NOT NULL UNIQUE,
            password_hash text NOT NULL,
            full_name text,
            is_active boolean NOT NULL DEFAULT true,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE roles (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            name text NOT NULL UNIQUE,
            description text,
            created_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE permissions (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            code text NOT NULL UNIQUE,
            description text,
            created_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE role_permissions (
            role_id uuid NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
            permission_id uuid NOT NULL REFERENCES permissions(id)
                ON DELETE CASCADE,
            PRIMARY KEY (role_id, permission_id)
        )
        """
    )

    op.execute(
        """
        CREATE TABLE tenant_members (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            role_id uuid NOT NULL REFERENCES roles(id),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE candidates (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            first_name text NOT NULL,
            last_name text NOT NULL,
            headline text,
            current_company text,
            grade text,
            location text,
            tags text[] NOT NULL DEFAULT '{}',
            is_blacklisted boolean NOT NULL DEFAULT false,
            search_vector tsvector GENERATED ALWAYS AS (
                to_tsvector('russian',
                    coalesce(last_name, '') || ' ' ||
                    coalesce(first_name, '') || ' ' ||
                    coalesce(headline, '') || ' ' ||
                    coalesce(current_company, '')
                )
            ) STORED,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX candidates_search_vector_gin ON candidates "
        "USING gin (search_vector)"
    )
    op.execute(
        "CREATE INDEX candidates_name_trgm ON candidates "
        "USING gin (last_name gin_trgm_ops, first_name gin_trgm_ops)"
    )
    op.execute(
        "CREATE INDEX candidates_tenant_updated_idx ON candidates "
        "(tenant_id, updated_at DESC)"
    )

    op.execute(
        """
        CREATE TABLE candidate_contacts (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            candidate_id uuid NOT NULL,
            kind text NOT NULL,
            value_encrypted bytea,
            value_hash text NOT NULL,
            is_primary boolean NOT NULL DEFAULT false,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, kind, value_hash)
        )
        """
    )

    op.execute(
        """
        CREATE TABLE candidate_facts (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            candidate_id uuid NOT NULL,
            fact_type text NOT NULL,
            value jsonb,
            confidence real,
            source text,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE resume_sources (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            candidate_id uuid NOT NULL,
            source_type text NOT NULL DEFAULT 'upload',
            source_url text,
            original_filename text,
            mime_type text,
            size_bytes integer,
            status text NOT NULL DEFAULT 'pending',
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE resume_versions (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            resume_source_id uuid NOT NULL,
            version integer NOT NULL DEFAULT 1,
            parsed_text text,
            embedding vector(1024),
            parsed_metadata jsonb,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX resume_versions_embedding_hnsw ON resume_versions "
        "USING hnsw (embedding vector_cosine_ops)"
    )

    op.execute(
        """
        CREATE TABLE vacancies (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            title text NOT NULL,
            description text,
            status text NOT NULL DEFAULT 'draft',
            headcount integer NOT NULL DEFAULT 1,
            recruiter_id uuid,
            hiring_manager_id uuid,
            search_vector tsvector GENERATED ALWAYS AS (
                to_tsvector('russian',
                    coalesce(title, '') || ' ' || coalesce(description, '')
                )
            ) STORED,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        "CREATE INDEX vacancies_search_vector_gin ON vacancies "
        "USING gin (search_vector)"
    )
    op.execute(
        "CREATE INDEX vacancies_tenant_updated_idx ON vacancies "
        "(tenant_id, updated_at DESC)"
    )

    op.execute(
        """
        CREATE TABLE vacancy_requirement_sets (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            vacancy_id uuid NOT NULL,
            name text NOT NULL,
            requirements jsonb NOT NULL DEFAULT '[]',
            is_active boolean NOT NULL DEFAULT true,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE funnel_presets (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            name text NOT NULL,
            description text,
            is_default boolean NOT NULL DEFAULT false,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE funnel_stages (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            preset_id uuid,
            vacancy_id uuid,
            name text NOT NULL,
            order_index integer NOT NULL DEFAULT 0,
            stage_type text NOT NULL DEFAULT 'screening',
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CHECK (
                (preset_id IS NOT NULL AND vacancy_id IS NULL)
                OR (preset_id IS NULL AND vacancy_id IS NOT NULL)
            )
        )
        """
    )

    op.execute(
        """
        CREATE TABLE applications (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            candidate_id uuid NOT NULL,
            vacancy_id uuid NOT NULL,
            current_stage_id uuid,
            origin text NOT NULL DEFAULT 'manual',
            status text NOT NULL DEFAULT 'new',
            screening_score real,
            risk_level text,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE stage_transitions (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            application_id uuid NOT NULL,
            from_stage_id uuid,
            to_stage_id uuid NOT NULL,
            reason text,
            actor_id uuid,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE hm_decisions (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            application_id uuid NOT NULL,
            decision text NOT NULL,
            comment text,
            actor_id uuid,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE outbox_events (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            event_type text NOT NULL,
            aggregate_type text NOT NULL,
            aggregate_id uuid NOT NULL,
            payload jsonb NOT NULL DEFAULT '{}',
            actor_id uuid,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE audit_log (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            actor_id uuid,
            action text NOT NULL,
            entity_type text NOT NULL,
            entity_id uuid NOT NULL,
            before jsonb,
            after jsonb,
            ip text,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE ai_runs (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            task text NOT NULL,
            provider text,
            model text,
            prompt_version text,
            input_payload jsonb,
            output jsonb,
            latency_ms integer,
            status text NOT NULL DEFAULT 'ok',
            error text,
            actor_id uuid,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE prompts (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            task text NOT NULL,
            version text NOT NULL,
            template text NOT NULL,
            is_active boolean NOT NULL DEFAULT true,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE ai_task_routes (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            task text NOT NULL,
            provider text NOT NULL,
            model text NOT NULL,
            prompt_version text,
            config jsonb,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE feature_flags (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            key text NOT NULL,
            enabled boolean NOT NULL DEFAULT false,
            config jsonb,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (tenant_id, key)
        )
        """
    )

    op.execute(
        """
        CREATE TABLE search_synonyms (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            term text NOT NULL,
            synonyms text[] NOT NULL DEFAULT '{}',
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE webhook_subscriptions (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            target_url text NOT NULL,
            event_types text[] NOT NULL DEFAULT '{}',
            secret text,
            is_active boolean NOT NULL DEFAULT true,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE comment_threads (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            entity_type text NOT NULL,
            entity_id uuid NOT NULL,
            parent_id uuid,
            body text NOT NULL,
            author_id uuid,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE merge_log (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            entity_type text NOT NULL,
            source_id uuid NOT NULL,
            target_id uuid NOT NULL,
            actor_id uuid,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    op.execute(
        """
        CREATE TABLE consents (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id uuid NOT NULL DEFAULT
                current_setting('app.tenant_id')::uuid,
            candidate_id uuid NOT NULL,
            consent_type text NOT NULL,
            granted boolean NOT NULL DEFAULT true,
            granted_at timestamptz,
            expires_at timestamptz,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )

    for table in DOMAIN_TABLES:
        _rls(table)


def downgrade() -> None:
    for table in reversed(DOMAIN_TABLES):
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE")

    op.execute("DROP TABLE IF EXISTS role_permissions CASCADE")
    op.execute("DROP TABLE IF EXISTS permissions CASCADE")
    op.execute("DROP TABLE IF EXISTS roles CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")
    op.execute("DROP TABLE IF EXISTS tenants CASCADE")

    op.execute("DROP EXTENSION IF EXISTS pgcrypto")
    op.execute("DROP EXTENSION IF EXISTS ltree")
    op.execute("DROP EXTENSION IF EXISTS vector")
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
