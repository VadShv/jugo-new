# AGENTS.md — ATS Jugo (jugo-new)

Rules for AI agents and contributors in this monorepo.

## Stack
- Backend: FastAPI (Python 3.12) at `backend/`.
- Frontend: React 18 + TypeScript at `frontend/`.
- Contracts (events, OpenAPI, prompts) at `contracts/`.
- Infra (compose, Caddy) at `infra/`.

## Zones of work
- **Core** (`backend/src/jugo/core/`, `backend/src/jugo/platform/`, `contracts/`): changes require `core-change` label + architect review.
- **Module mX**: edit only `backend/src/jugo/modules/mX_*`, `frontend/src/modules/mX-*`, your tests, and your migrations (prefix `mX_`).
- **Frontend** feature-sliced: `shared/`, `entities/`, `features/`, `widgets/`, `pages/`, `modules/`.

## Boundaries (enforced by import-linter in CI)
- `modules/*` may import only `core/*/public.py` and `platform/*`. No module→module imports. Core does not import modules.
- No direct SQL to other modules' tables. Migrations are additive to your own tables only.

## Contracts are inviolable
Need a new event/facade field → open RFC-issue with a backward-compatible extension; change `contracts/` first in a separate commit; bump `schema_version`.

## Migrations
Alembic, names prefixed by area (`core_`, `m1_`…). Additive only. Never edit another module's tables.

## Definition of Done (per PR)
- `ruff` + `mypy strict` (backend), `eslint` + `tsc` (frontend), import-linter boundaries — all green.
- Unit tests on new code (≥80% of changed lines). Contract tests + golden prompt tests (if prompts changed) green.
- Update `module.yaml` + changelog. New behavior behind a feature flag, merged disabled.

## Feature flags
New functionality under `is_enabled("mX.feature")`; merge disabled; agents may merge often without risk.

## Security (Secure First)
- Secrets only in env/Vault, never in git. `.env` is gitignored.
- PII (contacts) encrypted AES-GCM; RLS by `tenant_id` on all tables; audit sensitive reads.
- AI never sees contacts directly; resume text passed as data (anti prompt-injection).
- 152-ФЗ: prod LLM = YandexGPT, embeddings self-hosted (TEI BGE-M3), DB on cloud.ru (RF). PII does not leave РФ.

## PR description
What changed, which events/facades affected, how to verify by hand.
