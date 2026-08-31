# PLAN-GAPS — подплан устранения пробелов ATS Jugo

Контекст: аудит 2026-08-31 (см. `AGENTLOG.MD`). Бэкенд — рабочее ядро + 6 модулей; фронтенд — скелет, не связанный с бэкендом. Цель подплана — закрыть пробелы по приоритетам P0→P1→P2.

Легенда чекбоксов: `[ ]` не начато · `[~]` в работе · `[x]` готово. Обновлять вместе с `AGENTLOG.MD`.

Мастер-план: `~/.kilo/plans/1787995165356-ats-jugo-new.md`.

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
- [ ] `platform/eventbus.py`: реальный `EventBusPublisher` (Redis `XADD`), `ConsumerBase` (consumer group + `XREADGROUP`, inbox/дедуп `processed_events`, ретраи, DLQ).
- [ ] `jobs/outbox_relay.py`: воркер, читающий `outbox_events` (FOR UPDATE SKIP LOCKED) → `XADD` → пометка отправленным.
- [ ] SSE: `GET /api/v1/events/stream` (heartbeat, Last-Event-ID, фильтр по правам).
- [ ] Контрактные тесты событий (`contracts/events/v1/*`).
- **Приёмка**: событие `application.stage.changed` доходит до SSE-клиента.

### G7. arq-воркер (асинхронные AI-задачи)
- [ ] `jobs/worker.py`: arq `WorkerSettings` с пулами ai/index/webhooks/analytics/scheduler.
- [ ] Хендлеры: `parse_resume`, `embed_candidate`, `screen_application`, `risk_analyze` (вынести синхронные вызовы из HTTP в очередь).
- [ ] Эндпоинты M1–M4: `POST ...:run` → `202 {ai_run_id}` + enqueue; результат через опрос/SSE.
- **Приёмка**: скрининг идёт в воркере, API не блокируется.
- **Зависимости**: G6.

### G8. Эмбеддинги + семантический поиск
- [ ] `platform/ai/embeddings.py`: вызвать TEI в потоке резюме (`resume_versions.embedding`).
- [ ] `domains/search/service.py`: слой 2 — pgvector HNSW cosine + RRF-fusion с FTS; `POST /search/candidates` поддерживает `mode=hybrid`.
- [ ] Переиндексация при обновлении резюме (index-воркер).
- **Приёмка**: семантический поиск находит по смыслу, гибрид ранжирует лучше FTS.
- **Зависимости**: G7.

### G9. LLM-структурирование профиля резюме
- [ ] Промпт `resume.parse.profile`; воркер `parse_resume`: extract text → LLM → `parsed_metadata` (skills, experience[], education[]).
- [ ] Авто-обновление `candidate_facts` из профиля (без перезаписи закреплённых).
- **Приёмка**: у резюме есть структурированный профиль, факты попадают в карточку.
- **Зависимости**: G7.

**Гейт P1**: события доставляются, AI-задачи асинхронны, семантический поиск и профиль резюме работают.

---

## P2 — UI модулей + харденинг

### G10. UI модулей M1–M6
- [ ] Карточка кандидата: вкладки Сводка/Резюме/Отклики/**Оценка(M1)**/**Риски(M2)**/**Вопросы(M3)** + правая колонка тред/контакты.
- [ ] M1: таблица критерий→балл→доказательство, Подтвердить/Оспорить, «Как получен?» (whitebox).
- [ ] M2: бейдж риска, сигналы, альтернативные объяснения, эскалация.
- [ ] M3: редактор вопросов (карточки, правки, утверждение), экспорт «Гайд».
- [ ] M4: вкладка вакансии «Карта поиска» (доноры по тирам, гипотезы, паспорта с строками).
- [ ] M6: вкладка «Планировщик» (слоты, создание/перенос/отмена, обратная связь).
- [ ] M5: дашборды (воронка-санкей, портфель, источники, ИИ-операции).
- **Приёмка**: каждый модуль имеет рабочий UI против своего API.

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
