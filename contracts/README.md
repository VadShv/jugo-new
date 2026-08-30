# contracts/

Единый источник контрактов. Изменения — отдельным коммитом, обратно совместимые, с бампом `schema_version`.

- `openapi/` — снапшот OpenAPI 3.1 (генерируется из FastAPI, коммитится). Из него генерируется TS-клиент frontend и SDK.
- `events/v1/` — JSON Schema событий (конверт из ТЗ §4.3). Контрактные тесты в `backend/tests/contracts/` валидируют события из кода.
- `prompts/` — промпты (Jinja2) + golden sets. Перенесены в `backend/src/jugo/platform/ai/prompts/` и синхронизируются в БД миграциями.

Конверт события:
```json
{ "event_id": "uuid7", "event_type": "...", "schema_version": 1,
  "occurred_at": "ISO8601", "tenant_id": "uuid",
  "actor": { "type": "user|system|ai_agent|integration", "id": "..." },
  "aggregate": { "type": "...", "id": "uuid" }, "payload": {}, "trace_id": "..." }
```
