# AGENTLOG — ATS Jugo (jugo-new)

Живой журнал работы. **Единый источник правды** о том, где мы остановились и что осталось.
Обновлять в конце каждого шага: добавить строку в «Хронологию» и сдвинуть «Текущая точка».

Мастер-план: `~/.kilo/plans/1787995165356-ats-jugo-new.md` (и копия в `.kilo/plans/`).
Подплан устранения пробелов: [`docs/PLAN-GAPS.md`](docs/PLAN-GAPS.md).

Статус-метки: ✅ готово · 🟡 частично/стаб · 🔴 отсутствует · 🚧 в работе · ⏭️ следующий

---

## Снимок состояния (2026-08-31)

- **Репо**: github.com/VadShv/jugo-new, ветка `main`, последний коммит `bbd70e3`.
- **Деплой**: cloud.ru `176.108.250.112:3025` (docker-compose, 6 контейнеров: postgres+pgvector, redis, minio, backend, frontend, caddy). Миграции 0001–0006 применены. Внешний порт 3025 **закрыт файрволом cloud.ru** — открыть в консоли.
- **Проверка качества**: backend `ruff` + `mypy strict` + `pytest` = 30 тестов зелёные; frontend `tsc --noEmit` + `vite build` зелёные.
- **E2E на деплое**: login → кандидат → вакансия → отклик → переход по воронке → аналитика — работает.
- **Секреты**: `~/.local/share/kilo/plans/jugo-new-secrets.md` (PAT, deploy host, RSA-ключ); SSH-ключ `~/.ssh/jugo_deploy`.

### Статус по областям
| Область | Статус | Где |
|---|---|---|
| Ядро CRUD (candidates/vacancies/applications/funnel) | ✅ | `backend/src/jugo/domains/` |
| Auth (демо login/me) + RBAC deny-by-default | 🟡 | `core/security.py`, `auth/router.py` |
| RLS (tenant_id + before_flush) | ✅ | `core/db.py` |
| Поиск FTS (слой 1) | ✅ | `domains/search/` |
| Семантический поиск (pgvector/HNSW) | 🔴 | эмбеддинги не подключены |
| AI Platform (LLM-шлюз, промпты, ai_runs) | ✅ | `platform/ai/` |
| M1 Скрининг | ✅ | `modules/m1_screening/` |
| M2 Риски | ✅ | `modules/m2_risk/` |
| M3 Вопросы | ✅ | `modules/m3_questions/` |
| M4 Карта поиска | ✅ | `modules/m4_searchmap/` |
| M5 Аналитика | ✅ | `modules/m5_analytics/` |
| M6 Планировщик | ✅ | `modules/m6_scheduler/` |
| EventBus (outbox→Streams+SSE) | 🔴 | `platform/eventbus.py` (no-op) |
| Воркеры (arq) | 🔴 | `jobs/` отсутствует |
| Резюме: text extraction | ✅ | `resumes/service.py` |
| Резюме: эмбеддинги + LLM-структурирование | 🔴 | — |
| Файлы S3 presigned | ✅ | `files/service.py` |
| PII AES-GCM, 2FA, API-ключи, OIDC | 🔴 | — |
| Идемпотентность, rate limit, вебхуки, дедуп | 🔴 | — |
| Frontend: дизайн-система Liquid Glass | ✅ | `frontend/src/shared/ui/` |
| Frontend: реестры (vacancies/candidates/applications/analytics) | ✅ | контракт выровнен (G2); поиск готов (G3); мутации — G4 |
| Frontend: логин/auth UI | ✅ | `pages/LoginPage.tsx`, `entities/auth/api.ts` |
| Frontend: мутации (создание/переход) | ✅ | G4: формы создания + переход по воронке |
| Frontend: UI модулей M1–M6 | 🔴 | нет |

---

## Текущая точка

**Аудит завершён (2026-08-31).** Бэкенд — рабочее ядро + 6 модулей (синхронные AI-вызовы). Фронтенд — качественный дизайн-скелет, **но не связан с бэкендом** (нет логина, контракт типов расходится, поиск/мутации/аналитика не привязаны, UI модулей нет).

**P0-G4 готов (2026-08-31).** Мутации: создание вакансии/кандидата/отклика + переход по воронке (с селектором стадий). Бэкенд: добавлен `GET /funnel/presets/{id}/stages`. `tsc`/`build` + backend `pytest` (30) зелёные.

**⏭️ Следующий шаг**: `docs/PLAN-GAPS.md` → **P0-G5** (аналитика → реальный API `/analytics/*` вместо мок-данных).

---

## Хронология

| Дата | Коммит | Что сделано |
|---|---|---|
| 2026-08-30 | `37c75e8` | Каркас монорепо: FastAPI core (CRUD, RLS, auth, search) + React Liquid Glass shell + docker-compose + CI + contracts. Деплой на cloud.ru, E2E (login/CRUD/transition). |
| 2026-08-30 | `76775ca` | fix: Dockerfile копирует alembic; `compose.deploy.yml` для 4GB ВМ. |
| 2026-08-30 | `fa42a5f` | feat(m1): AI-скрининг + LLM-шлюз с prompt registry. |
| 2026-08-30 | `d9084d1` | fix(m1): выравнивание под реальную схему 0001. |
| 2026-08-30 | `1ed1bdf` | fix(core): `SET LOCAL` интерполяция UUID (asyncpg) — починило 500 на авторизованных CRUD. |
| 2026-08-30 | `493b6e8` | fix(core): `before_flush` contextvar для tenant_id — починило INSERT. |
| 2026-08-30 | `507cef6` | feat(m2): AI-риски (детекторы + LLM + risk_level + денормализация). |
| 2026-08-30 | `070120d` | feat(m3): AI-вопросы (STAR/CARE + валидаторы + retry). |
| 2026-08-30 | `9dcd8fa` | feat(m4): Карта поиска (6-шаговый конвейер + билдер/валидатор). |
| 2026-08-30 | `8f68b47` | feat(m6): Планировщик (suggest_slots + CRUD + feedback). |
| 2026-08-30 | `bbd70e3` | feat(m5): Аналитика (витрины на лету). |
| 2026-08-31 | (аудит) | Полный аудит бэк/фронт; выявлены пробелы (см. `docs/PLAN-GAPS.md`). Коммитов нет. |
| 2026-08-31 | `de41a81` | docs: AGENTLOG.MD + docs/PLAN-GAPS.md (трекинг + подплан). |
| 2026-08-31 | (G1) | P0-G1: LoginPage + auth api + token storage + route guard + 401 redirect + logout. tsc/build зелёные. |
| 2026-08-31 | (G2) | P0-G2: типы/колонки/StatusBadge/PipelineStageBar выровнены под бэкенд; фильтр статусов привязан к ?status=. tsc/build зелёные. |
| 2026-08-31 | (G3) | P0-G3: поиск → POST /search/{entity}; реестры ветвят list/search. E2E q=Python → Иван Петров. tsc/build зелёные. |
| 2026-08-31 | (G4) | P0-G4: мутации (создание вакансии/кандидата/отклика + переход); бэкенд GET /funnel/presets/{id}/stages. tsc/build + pytest(30) зелёные. |

---

## Правила ведения
1. В конце каждого шага: добавить строку в «Хронологию» (дата + коммит + кратко), обновить «Снимок»/«Статус по областям», сдвинуть «Текущая точка» на следующий шаг.
2. Чекбоксы статуса задач — в `docs/PLAN-GAPS.md`.
3. Коммитить `AGENTLOG.MD` + `docs/PLAN-GAPS.md` вместе с кодом шага.
