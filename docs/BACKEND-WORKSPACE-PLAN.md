# BACKEND-WORKSPACE-PLAN — доработка бэкенда под workspace-спецификацию

Контекст: `jugo-huntflow-like-workspace-spec.md` описывает 3-панельный workspace рекрутёра.
Бэкенд уже имеет: CRUD вакансий/кандидатов/откликов, transition, RLS, audit, outbox/SSE,
AI-модули M1–M6, аналитику. **Не хватает**: activity timeline, комментарии, задачи,
структурированный отказ, workspace-агрегат, optimistic locking, bulk ops, enrichment-поля.

План: 8 фаз, каждая — миграция + модель + схема + сервис + роутер + тесты.
Порядок: B1 → B8. Каждая фаза: ruff/mypy/pytest зелёные → коммит → push → migrate на deploе.

---

## B1. Application enrichment + optimistic locking

**Цель**: добавить поля, необходимые workspace, + version для конфликт-детекции.

### Миграция 0008
```sql
ALTER TABLE applications
  ADD COLUMN version integer NOT NULL DEFAULT 1,
  ADD COLUMN stage_entered_at timestamptz,
  ADD COLUMN next_action_at timestamptz,
  ADD COLUMN owner_id uuid,
  ADD COLUMN salary_expectation text,
  ADD COLUMN rejection_reason_code text,
  ADD COLUMN rejection_comment text;
```

### Изменения
- `applications/models.py`: добавить поля.
- `applications/schemas.py`: `ApplicationOut` отдаёт новые поля; `ApplicationUpdate` принимает `owner_id`, `salary_expectation`, `next_action_at`.
- `applications/service.py`:
  - `transition()`: при переходе — `stage_entered_at = now()`, `version += 1`. Проверять `version` из payload (optimistic locking): если не совпадает → 409 Conflict.
  - `update()`: `version += 1` при PATCH.
- `funnel/service.py`: `transition()` — установить `stage_entered_at`, инкремент `version`, проверка `version`.
- **Приёмка**: transition с неверным version → 409; stage_entered_at устанавливается; новые поля в API.

---

## B2. Activity timeline

**Цель**: `GET /applications/{id}/activities` — единая хронологическая лента.

### Без миграции (использует существующие таблицы)
Объединяет данные из:
- `stage_transitions` (переходы по воронке)
- `audit_log` (действия: create, update, reject, AI-run)
- `comment_threads` (комментарии — после B3)
- `outbox_events` (системные события)

### Новый файл
- `domains/activities/service.py`: `list_activities(session, application_id, limit, cursor)` — UNION-запрос из `stage_transitions` + `audit_log` (WHERE entity_id = application_id), отсортированный по `created_at DESC`, курсорная пагинация.
- `domains/activities/schemas.py`: `ActivityOut` — `{id, type, actor_id, description, metadata jsonb, created_at}`.
- `domains/activities/router.py`: `GET /applications/{application_id}/activities` → `list[ActivityOut]` (permission `application:read`).

### Типы activity
- `stage_changed` — из stage_transitions (from → to, reason)
- `created` — из audit_log (action=application.created)
- `updated` — из audit_log (action=application.updated)
- `screening_completed` — из audit_log (action=m1.screening.run)
- `risk_completed` — из audit_log (action=m2.risk.run)
- `comment_created` — из comment_threads (после B3)
- `interview_scheduled` — из audit_log (action=m6.interview.create)

### Приёмка
`GET /applications/{id}/activities` → хронологический список событий с типами и описаниями.

---

## B3. Comments

**Цель**: `POST/GET /applications/{id}/comments` — комментарии на application.

### Миграция 0009
```sql
ALTER TABLE comment_threads
  ADD COLUMN parent_id uuid REFERENCES comment_threads(id) ON DELETE CASCADE,
  ADD COLUMN updated_by uuid,
  ADD COLUMN deleted_at timestamptz;
CREATE INDEX ix_comment_threads_application ON comment_threads (application_id, created_at DESC);
```

### Изменения
- `domains/comments/models.py`: `Comment` (пересоздать модель поверх `comment_threads`): id, tenant_id, application_id, author_id, parent_id (nullable, для тредов), body, is_private, deleted_at, created_at, updated_at.
- `domains/comments/schemas.py`: `CommentCreate` (body, parent_id?, is_private?), `CommentOut` (с author_id, children?).
- `domains/comments/service.py`: `create()`, `list()` (дерево или плоский с parent_id), `update()`, `soft_delete()`.
- `domains/comments/router.py`:
  - `POST /applications/{application_id}/comments` → 201, CommentOut
  - `GET /applications/{application_id}/comments` → list[CommentOut]
  - `PATCH /comments/{id}` → CommentOut (только автор)
  - `DELETE /comments/{id}` → 204 (soft delete, только автор)
- RBAC: `comment:write` (recruiter/admin), `comment:read` (recruiter/HM/admin). `is_private` комментарии недоступны HM (`comment:read_internal`).
- Audit: `comment.created/updated/deleted` в audit_log.
- Outbox: `comment.created` event.

### Приёмка
Создание комментария → GET возвращает список; приватные недоступны HM; soft delete.

---

## B4. Tasks

**Цель**: `POST/GET/PATCH /applications/{id}/tasks` — задачи на application.

### Миграция 0010
```sql
CREATE TABLE tasks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL DEFAULT current_setting('app.tenant_id')::uuid,
  application_id uuid NOT NULL,
  title text NOT NULL,
  description text,
  due_at timestamptz,
  assignee_id uuid,
  completed_at timestamptz,
  completed_by uuid,
  created_by uuid NOT NULL,
  created_at timestamptz DEFAULT now() NOT NULL,
  updated_at timestamptz DEFAULT now() NOT NULL
);
CREATE INDEX ix_tasks_application ON tasks (application_id, due_at);
CREATE INDEX ix_tasks_assignee ON tasks (assignee_id, completed_at);
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON tasks USING (tenant_id = current_setting('app.tenant_id', true)::uuid);
```

### Изменения
- `domains/tasks/models.py`: `Task` (TenantMixin + Base).
- `domains/tasks/schemas.py`: `TaskCreate` (title, description?, due_at?, assignee_id?), `TaskUpdate` (completed?), `TaskOut`.
- `domains/tasks/service.py`: `create()`, `list()` (by application, by assignee, incomplete first), `complete()`, `uncomplete()`.
- `domains/tasks/router.py`:
  - `POST /applications/{application_id}/tasks` → 201
  - `GET /applications/{application_id}/tasks` → list[TaskOut]
  - `PATCH /tasks/{id}` → TaskOut (mark complete/incomplete)
  - `GET /tasks?assignee_id=&status=incomplete` → list[TaskOut] (для глобального списка задач)
- RBAC: `task:write` (recruiter/admin), `task:read` (recruiter/HM/admin).
- Audit + outbox: `task.created/completed`.

### Приёмка
Создание задачи → GET возвращает; complete → completed_at устанавливается; фильтр incomplete.

---

## B5. Structured reject

**Цель**: `POST /applications/{id}/reject` — отказ со структурированной причиной.

### Миграция 0011
```sql
CREATE TABLE reject_reasons (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id uuid NOT NULL DEFAULT current_setting('app.tenant_id')::uuid,
  code text NOT NULL,
  label text NOT NULL,
  is_active boolean DEFAULT true,
  created_at timestamptz DEFAULT now() NOT NULL,
  UNIQUE (tenant_id, code)
);
ALTER TABLE reject_reasons ENABLE ROW LEVEL SECURITY;
ALTER TABLE reject_reasons FORCE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON reject_reasons USING (tenant_id = current_setting('app.tenant_id', true)::uuid);
-- Seed
INSERT INTO reject_reasons (tenant_id, code, label) VALUES
  ('00000000-0000-0000-0000-000000000001', 'no_match', 'Не подходит по навыкам'),
  ('00000000-0000-0000-0000-000000000001', 'overqualified', 'Квалификация превышает требования'),
  ('00000000-0000-0000-0000-000000000001', 'location', 'Не подходит локация'),
  ('00000000-0000-0000-0000-000000000001', 'salary', 'Зарплатные ожидания выше бюджета'),
  ('00000000-0000-0000-0000-000000000001', 'no_response', 'Кандидат не вышел на связь'),
  ('00000000-0000-0000-0000-000000000001', 'failed_interview', 'Не прошёл интервью'),
  ('00000000-0000-0000-0000-000000000001', 'duplicate', 'Дубликат'),
  ('00000000-0000-0000-0000-000000000001', 'other', 'Другое');
```

### Изменения
- `domains/applications/models.py`: `RejectReason` (TenantMixin + Base, table `reject_reasons`).
- `domains/applications/schemas.py`: `RejectRequest` (reason_code, comment?), `RejectReasonOut`.
- `domains/applications/service.py`: `reject(session, application_id, reason_code, comment, actor)` — устанавливает `status='rejected'`, `rejection_reason_code`, `rejection_comment`, переход на стадию «Отказ» (если есть), `version += 1`, audit + outbox `application.rejected`.
- `domains/applications/router.py`:
  - `POST /applications/{id}/reject` → ApplicationOut (permission `application:write`)
  - `POST /applications/{id}/restore` → ApplicationOut (восстановление из rejected)
  - `GET /dictionaries/reject-reasons` → list[RejectReasonOut] (permission `application:read`)
- **Приёмка**: reject с reason_code → status=rejected + reason сохранён; restore → status=active; GET reject-reasons → список.

---

## B6. Workspace aggregate

**Цель**: `GET /vacancies/{id}/workspace` — всё для workspace в одном запросе.

### Без миграции (агрегация существующих данных)
Объединяет:
- Vacancy (title, status, headcount, description)
- Stages (funnel_stages для вакансии или пресета)
- Counters per stage (COUNT applications GROUP BY current_stage_id)
- Counters summary (total, new, active, rejected, hired)
- Applications (первая страница, 50 записей, с candidate names)

### Новый файл
- `domains/workspace/service.py`: `get_workspace(session, vacancy_id)` → `WorkspaceOut`.
  - Загружает vacancy.
  - Загружает stages (from preset or vacancy-specific).
  - Считает counters: `SELECT current_stage_id, COUNT(*) FROM applications WHERE vacancy_id = :v GROUP BY current_stage_id`.
  - Считает summary: `SELECT status, COUNT(*) FROM applications WHERE vacancy_id = :v GROUP BY status`.
  - Загружает applications (first page) с JOIN candidates для имён.
- `domains/workspace/schemas.py`: `WorkspaceOut` — `{vacancy: VacancyOut, stages: list[StageWithCount], summary: {total, new, active, rejected, hired}, applications: Page[ApplicationWithCandidate]}`.
  - `ApplicationWithCandidate` — Application + candidate_name + candidate_headline.
- `domains/workspace/router.py`: `GET /vacancies/{vacancy_id}/workspace` → WorkspaceOut (permission `vacancy:read`).

### Приёмка
Один запрос возвращает всё для 3-панельного workspace: вакансию, стадии со счётчиками, первые 50 откликов с именами кандидатов.

---

## B7. Bulk operations

**Цель**: массовые действия над applications.

### Без миграции (использует существующие endpoints)
- `POST /applications/bulk/transition` — body: `{application_ids: uuid[], to_stage_id: uuid, reason?: string}` → `{success: uuid[], failed: {id, error}[]}`. Последовательно вызывает `transition()` для каждого.
- `POST /applications/bulk/reject` — body: `{application_ids: uuid[], reason_code: string, comment?: string}` → результат.
- RBAC: `application:write` (recruiter/admin).
- Audit: одно событие `bulk.transition` / `bulk.reject` + индивидуальные events.

### Приёмка
Массовый переход 5 откликов → все переходят, возвращается результат success/failed.

---

## B8. Vacancy counters + enrichment

**Цель**: vacancy response включает счётчики + health-score данные.

### Без миграции (вычисляемые поля)
- `vacancies/schemas.py`: `VacancyOut` добавляет `counters: {responses, active, new, hired, rejected}` и `health: {status: green|yellow|red, days_open, last_activity_at}`.
- `vacancies/service.py`: `get()` и `list()` — вычисляют counters (подзапросы или JOIN). Health: green если active > 0 и last_activity < 3 дней; yellow если active = 0 или last_activity 3-7 дней; red если last_activity > 7 дней или no applications.
- **Оптимизация**: counters вычисляются одним `SELECT status, COUNT(*) FROM applications WHERE vacancy_id IN (...) GROUP BY vacancy_id, status` для list (batch).

### Приёмка
`GET /vacancies` → каждая вакансия с counters + health; `GET /vacancies/{id}` → то же.

---

## Порядок реализации
B1 (enrichment + locking) → B2 (activity timeline) → B3 (comments) → B4 (tasks) → B5 (reject) → B6 (workspace aggregate) → B7 (bulk ops) → B8 (vacancy counters).

## Зависимости
- B2 зависит от B1 (stage_entered_at для timeline).
- B3 зависит от B1 (application_id для комментариев).
- B5 зависит от B1 (rejection_reason_code field).
- B6 зависит от B1, B5 (enriched application + reject).
- B7 зависит от B5 (bulk reject).
- B8 зависит от B1 (counters используют status).

## Оценка
8 фаз, каждая — 1 миграция (кроме B2/B6/B7/B8 без миграций) + модель + схема + сервис + роутер + тесты.
После B1–B8 бэкенд полностью поддерживает workspace-спецификацию.
