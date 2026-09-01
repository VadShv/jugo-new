# PLAN-GAPS — подплан устранения пробелов ATS Jugo

Контекст: аудит 2026-08-31 (см. `AGENTLOG.MD`). Бэкенд — рабочее ядро + 6 модулей; фронтенд — скелет, не связанный с бэкендом. Цель подплана — закрыть пробелы по приоритетам P0→P1→P2.

Легенда чекбоксов: `[ ]` не начато · `[~]` в работе · `[x]` готово. Обновлять вместе с `AGENTLOG.MD`.

Мастер-план: `~/.kilo/plans/1787995165356-ats-jugo-new.md`.

> **Переприоритизация (2026-09-01):** P0 готов ✅; P1 — G6, G7 готовы ✅, **G8/G9 отложены** (нужны AI-ключ и TEI, не видны в UI). Следующий приоритет — **P2-G10 (полностью рабочий UI)**, детальный дизайн в `docs/FRONTEND-UI.md`. Порядок выполнения: G10 → G13 (полировка) → G11/G12 (харденинг) → G8/G9 (AI-глубина, когда будет AI-ключ).

---

## P0 — сделать фронтенд рабочим (приоритет)

Цель: UI показывает реальные данные из бэкенда, логин работает, базовые мутации и поиск живые.

### G1. Экран логина + хранение токена
- [x] `frontend/src/pages/LoginPage.tsx`: форма (email, password, role) → `POST /api/v1/auth/login` → `localStorage['ats.token'] = access_token` → редирект `/vacancies`.
- [x] `frontend/src/entities/auth/api.ts`: `login(email, role)`, `fetchMe()`.
- [x] `frontend/src/app/router.ts`: добавить `/login` (public); guard на защищённых роутах — без токена редирект на `/login`.
- [x] `frontend/src/shared/api/client.ts`: при 401 — очистить токен + редирект `/login`.
- [x] Кнопка «Выйти» в `GlassTopBar` (очистка токена).
- **Приёмка**: логин → реестры грузят данные (200), без токена — редирект на логин.
- **Зависимости**: — .

### G2. Выровнять контракт фронт↔бэк
- [x] Типы `shared/api/types.ts` выровнены вручную под схемы бэкенда (Candidate first_name/last_name/headline; Vacancy title/description/status/headcount; Application candidate_id/vacancy_id/status). OpenAPI-codegen оставлен на харденинг.
- [x] Колонки реестров под реальные поля: CandidatesPage (ФИО=last_name+first_name, Должность=headline), VacanciesPage (title/status/headcount/created_at), ApplicationsPage (candidate_id/vacancy_id/status/updated_at).
- [x] `StatusBadge`/`PipelineStageBar` переведены на `application.status` (new/in_progress/hired/rejected/withdrawn) + fallback; фильтр статусов откликов привязан к `?status=`.
- **Приёмка**: во всех реестрах реальные данные отображаются без «—» (кроме действительно пустых полей).
- **Зависимости**: G1 (нужен токен для проверки).

### G3. Поиск → POST /search/{entity}
- [x] `frontend/src/entities/*/api.ts`: `searchCandidates/searchVacancies/searchApplications({q, cursor, signal, filters})` → `POST /api/v1/search/{entity}` (body `{q, cursor, filters, limit}`).
- [x] Реестры: при непустом `search` зовут `search*` вместо `fetch*`; при пустом — list (list-вызовы больше не шлют `?q=`).
- **Приёмка**: ввод текста → реальные результаты поиска (FTS).
- **Зависимости**: G2.

### G4. Мутации (создание + переход по воронке)
- [x] `VacanciesPage` AddVacancyForm → `POST /api/v1/vacancies` (title, description) + инвалидация кэша.
- [x] `CandidatesPage`: кнопка + форма создания кандидата → `POST /api/v1/candidates` (first_name, last_name, headline, grade, location, tags).
- [x] `ApplicationsPage`: создание отклика → `POST /api/v1/applications` (candidate_id, vacancy_id, current_stage_id) + переход → `POST /api/v1/applications/{id}/transition` (to_stage_id, reason) в карточке отклика.
- [x] Бэкенд: добавлен `GET /api/v1/funnel/presets/{id}/stages`; фронт: `useDefaultStages()` для селекторов стадий.
- **Приёмка**: создание + переход отражаются в реестре и аналитике.
- **Зависимости**: G2.

### G5. Аналитика → реальный API
- [x] `AnalyticsPage`: `GET /api/v1/analytics/funnel/{vacancy_id}` (выбор вакансии), `/analytics/sources`, `/analytics/ai`, `/analytics/recruiters` → ECharts/таблицы с реальными данными.
- [x] Селектор вакансии для воронки; KPI (всего/найм/отказ) + bar по статусам.

**Гейт P0**: [x] фронтенд полностью работает против бэкенда (логин → реестры → поиск → создание → переход → аналитика). Деплой обновлён.

---

## P1 — доработать бэкенд (асинхронность + AI-глубина)

### G6. EventBus: outbox-relay → Redis Streams + SSE
- [x] `platform/eventbus.py`: реальный `EventBusPublisher` (Redis `XADD`); `ConsumerBase` — базовый класс (consumer groups/XREADGROUP/inbox — в G7 для модульных консьюмеров).
- [x] `jobs/outbox_relay.py`: воркер, читающий `outbox_events` (FOR UPDATE SKIP LOCKED) → `XADD` в `jugo:events` → пометка `relayed_at`; запускается через lifespan.
- [x] SSE: `GET /api/v1/events/stream` (heartbeat, Last-Event-ID, фильтр по tenant; токен через `?token=` или Bearer). Миграция 0007 (`outbox_events.relayed_at`).
- [ ] Контрактные тесты событий (`contracts/events/v1/*`) — позже.
- **Приёмка**: событие `application.stage.changed` доходит до SSE-клиента.

### G7. arq-воркер (асинхронные AI-задачи)
- [x] `jobs/worker.py`: arq `WorkerSettings` с AI-функциями (generate_requirements, screen_application, analyze_risk, generate_questions, generate_search_map); единый пул (разделение пулов ai/index/webhooks/analytics/scheduler — позже). `jobs/queue.py` (enqueue). Сервис `worker` в compose.deploy.yml.
- [x] Хендлеры M1–M4 вынесены из HTTP в очередь (открывают сессию, set_tenant_context, вызывают сервис, commit/rollback). `parse_resume`/`embed_candidate` — G8/G9.
- [x] Эндпоинты M1–M4: `POST ...:run`/`:generate` → `202 {job_id}` + enqueue; результат через GET (опрос).
- **Приёмка**: скрининг идёт в воркере, API не блокируется.
- **Зависимости**: G6.

### G8. Эмбеддинги + семантический поиск ⏸️ отложено (нужен AI-ключ/TEI)
- [ ] `platform/ai/embeddings.py`: вызвать TEI в потоке резюме (`resume_versions.embedding`).
- [ ] `domains/search/service.py`: слой 2 — pgvector HNSW cosine + RRF-fusion с FTS; `POST /search/candidates` поддерживает `mode=hybrid`.
- [ ] Переиндексация при обновлении резюме (index-воркер).
- **Приёмка**: семантический поиск находит по смыслу, гибрид ранжирует лучше FTS.
- **Зависимости**: G7, AI-ключ.

### G9. LLM-структурирование профиля резюме ⏸️ отложено (нужен AI-ключ)
- [ ] Промпт `resume.parse.profile`; воркер `parse_resume`: extract text → LLM → `parsed_metadata` (skills, experience[], education[]).
- [ ] Авто-обновление `candidate_facts` из профиля (без перезаписи закреплённых).
- **Приёмка**: у резюме есть структурированный профиль, факты попадают в карточку.
- **Зависимости**: G7, AI-ключ.

**Гейт P1**: события доставляются, AI-задачи асинхронны, семантический поиск и профиль резюме работают.

---

## P2 — UI модулей + харденинг

### G10. UI модулей M1–M6 + детальные страницы (полностью рабочий UI)
Подробный дизайн и разбивка: [`docs/FRONTEND-UI.md`](FRONTEND-UI.md).
- [x] **G10.1** `DetailLayout` + `useAiJob` + `AIResultPanel`; детальная страница кандидата (`/candidates/$candidateId`) — Сводка/Резюме/Отклики; реестр → navigate.
- [x] **G10.2** M1-панель (критерии + скрининг run+poll + таблица) — кандидат (вкладка Оценка). Бэкенд: `GET /screening/vacancies/{id}/requirements`. Vacancy-Критерии — в G10.5; override (Подтвердить/Оспорить) — позже (нужен бэкенд-эндпоинт override).
- [x] **G10.3** M2-панель (риски run+poll + signals + бейдж risk_level) — кандидат (вкладка Риски).
- [x] **G10.4** M3-панель (вопросы run+poll + карточки STAR/CARE + утверждение) — кандидат (вкладка Вопросы).
- [x] **G10.5** Детальная страница вакансии: Описание / Критерии(M1) / Воронка-канбан DnD-переход / Карта поиска(M4) / Аналитика / Настройки(PATCH). Планировщик(M6) на вкладке вакансии — позже (G10.6/7).
- [x] **G10.6** Детальная страница отклика (`/applications/$applicationId`): Таймлайн (кандидат/вакансия/статус + переход по воронке) / Скрининг(M1 run+poll) / Риски(M2 run+poll). Реестр → navigate. M6 интервью на отклике — позже.
- [x] **G10.7** Аналитика: воронка-funnel (ECharts) + портфель вакансий (таблица с конверсиями) + источники/ИИ/рекрутёры. Полировка: @keyframes анимации GlassSheet, dark-mode toggle, code-split (manualChunks: app 301KB, echarts/tanstack/react отдельно).
- **Приёмка**: каждый модуль имеет рабочий UI против своего API; полный цикл найма проходим из UI.

### G11. Безопасность (Secure First)
- [ ] PII: AES-256-GCM контакты + HMAC; API `candidate:contacts:read` + аудит чтений.
- [ ] 2FA TOTP для админов; API-ключи со скоупами; OIDC/SSO (абстракция → реализация).
- [ ] Отдельная app-роль БД (не superuser) → RLS реально enforcing; CI negative-тест кросс-тенант.
- **Приёмка**: RLS enforced, контакты зашифрованы, 2FA работает.

### G12. Эксплуатационные доработки
- [ ] Идемпотентность `Idempotency-Key` (24ч); rate limiting (Redis sliding window); вебхуки (подписки+доставка+HMAC); дедупликация кандидатов (точная HMAC + нечёткая pg_trgm).
- **Приёмка**: повторные запросы идемпотентны, лимиты отвечают 429, вебхуки доставляются.

### G13. Полировка фронтенда
- [ ] `@keyframes fade-in/sheet-up/fade-out` в `tokens.css` (оживить анимации GlassSheet).
- [ ] Переключатель тёмной темы; code-splitting (lazy-роуты, manualChunks) — чанк <500KB.
- [ ] Empty/error/loading-состояния; тосты ошибок; доступность (фокус-ринг, контраст).
- **Приёмка**: Lighthouse ≥90, анимации плавные, dark mode работает.

**Гейт P2**: модули с UI, харденинг безопасности, полировка. → v1.0 по мастер-плану.

---

## Порядок выполнения
P0 (G1→G2→G3→G4→G5) → гейт P0 → P1 (G6→G7→G8→G9) → гейт P1 → P2 (G10→G11→G12→G13) → гейт P2 = v1.0.

Каждый шаг: реализация → `ruff`/`mypy`/`pytest` + `tsc`/`build` зелёные → коммит (с обновлением `AGENTLOG.MD` + этого файла) → push → redeploy (если бэк) → отметить чекбокс.
