# ATS Jugo (jugo-new)

Applicant Tracking System — **AI-Native · White Box · Secure First · User Friendly**.
Backend: FastAPI (Python 3.12) · Frontend: React 18 (TS) · PostgreSQL 16 (+pgvector, pg_trgm, ltree) · Redis 7 · S3-совместимое хранилище.

## Structure
```
backend/    FastAPI modular monolith (core + platform + modules M1–M6)
frontend/   React SPA (feature-sliced, Liquid Glass design system)
contracts/  events (JSON Schema), OpenAPI snapshot, prompts + golden
infra/      docker-compose (dev/prod), Caddyfile
docs/       specs (ТЗ), ADR
```

## Dev
```bash
cp infra/.env.example .env
docker compose -f infra/docker-compose.dev.yml up -d
# backend API: http://localhost:8000  (health: /live /ready)
# frontend UI: http://localhost:5173
```

## Deploy (cloud.ru, ВМ 176.108.250.112, edge :3025)
```bash
ssh -i ~/.ssh/jugo_deploy user1@176.108.250.112
# on VM: clone, set .env, then:
docker compose -f infra/compose.prod.yml up -d
```

See `docs/specs/` for full ТЗ and `AGENTS.md` for contributor rules.
