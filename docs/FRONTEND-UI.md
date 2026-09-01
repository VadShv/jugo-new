# FRONTEND-UI — дизайн полностью рабочего UI ATS Jugo

Цель: полностью рабочий UI против реального бэкенда (Liquid Glass, feature-sliced, TanStack).
Принципы: стекло — только навигация; контент непрозрачный; анимация только transform/opacity;
AI-результаты — whitebox («Как получен?»); async AI через `POST :run → 202` + опрос GET.

Текущий фронт (P0): логин, 4 реестра (vacancies/candidates/applications/analytics) с поиском,
созданием, переходом, аналитикой. **Нет**: детальных страниц, UI модулей M1–M6, канбан-воронки,
карточки кандидата с вкладками. Этот дизайн закрывает пробел (P2-G10).

> AI-контент (скрининг/риски/вопросы/карта) появляется после добавления AI-ключа в `.env`.
> Без ключа UI работает (кнопки зовут API → 202), но результаты пустые/ошибка воркера.

---

## Информационная архитектура (роуты)

```
/login
/vacancies                       реестр (готов, G2-G4)
/vacancies/:vacancyId            ДЕТАЛЬ: Описание | Критерии(M1) | Воронка(канбан) | Карта поиска(M4) | Аналитика | Планировщик(M6) | Настройки
/candidates                      реестр (готов)
/candidates/:candidateId         ДЕТАЛЬ: Сводка | Резюме | Отклики | Оценка(M1) | Риски(M2) | Вопросы(M3)
/applications                    реестр (готов)
/applications/:applicationId     ДЕТАЛЬ: таймлайн | резюме | быстрые действия (переход/M1/M2/M3/M6) | вкладки результатов
/analytics                       дашборды (G5 + расширение G10.7)
```
Реестры: клик по строке → `navigate` на детальную страницу (вместо drawer). Drawer остаётся как
быстрый превью (опц.).

---

## Общие компоненты (shared/widgets)

- **`DetailLayout`** (`widgets/DetailLayout.tsx`): шапка (title + meta + actions) + Radix Tabs
  (Сводка/…) + `<Outlet/>`-подобный контент. Переиспользуется для candidate/vacancy/application.
- **`useAiJob`** (`shared/api/useAiJob.ts`): хук `run(endpoint, pollEndpoint, id)` → POST :run (202)
  → опрос GET каждые 2с до результата/таймаута (60с) → `{data, status: idle|running|done|error}`.
  Единый паттерн для M1/M2/M3/M4.
- **`AIResultPanel`** (`widgets/AIResultPanel.tsx`): обёртка — кнопка «Запустить», статусы
  (idle/running/пусто/ошибка), слот для рендера результата. Whitebox-ссылка «Как получен?» →
  раскрытие (модель/промпт/ai_run — когда будет `/ai/runs/{id}`).
- **`KanbanBoard`** (`widgets/KanbanBoard.tsx`): колонки по стадиям воронки, карточки-отклики,
  DnD (dnd-kit или native) → `POST /applications/{id}/transition`.
- **`ResumeViewer`**: текст `parsed_text` с подсветкой; список версий.

---

## Экраны

### Кандидат — `/candidates/:id`
Данные: `GET /candidates/{id}` (Candidate); отклики `GET /applications?candidate_id={id}`;
резюме `GET /candidates/{id}/resumes` (есть); загрузка `POST /candidates/{id}/resumes`.
- **Сводка**: ФИО, headline, grade, location, tags, current_company; факты (когда `candidate_facts`
  API — G9); контакты (заглушка до G11).
- **Резюме**: список версий + `ResumeViewer`; кнопка «Загрузить резюме» (multipart).
- **Отклики**: список откликов кандидата (vacancy title, status, stage) → клик на `/applications/:id`.
- **Оценка (M1)**: селектор вакансии (определяет application_id) → «Сгенерировать критерии»
  (`POST /screening/vacancies/{v}/requirements:generate` →202+опрос) + «Запустить скрининг»
  (`POST /screening/applications/{a}:run` →202+опрос `GET /screening/applications/{a}`) →
  таблица: критерий | балл | вес | доказательство | цитата; «Подтвердить/Оспорить»; «Как получен?».
- **Риски (M2)**: «Запустить анализ» (`POST /risk/applications/{a}:run` →202+опрос
  `GET /risk/applications/{a}`) → бейдж risk_level, список signals (code/severity/evidence/
  alternative_explanation/verification_question), top_risks.
- **Вопросы (M3)**: «Сгенерировать» (`POST /questions/vacancies/{v}:generate` →202+опрос
  `GET /questions/vacancies/{v}`) → карточки (block/question/probes/listen_for/red_flags),
  «Утвердить» (`POST /questions/sets/{id}:approve`).

### Вакансия — `/vacancies/:id`
Данные: `GET /vacancies/{id}`; стадии `useDefaultStages()`; отклики `GET /applications?vacancy_id={id}`;
карта `GET /search-map/vacancies/{id}`; интервью `GET /interviews/vacancies/{id}`; аналитика `GET /analytics/funnel/{id}`.
- **Описание**: title/status/headcount/description; «Редактировать» (PATCH).
- **Критерии (M1)**: «Сгенерировать критерии» → список критериев (вес/описание).
- **Воронка**: `KanbanBoard` — колонки = стадии пресета, карточки = отклики (candidate name),
  DnD → transition. Счётчики по стадиям.
- **Карта поиска (M4)**: «Сгенерировать карту» (`POST /search-map/vacancies/{id}:generate` →202+
  опрос) → доноры (по тирам, approve/reject), гипотезы, паспорта (platform/query/термы, «Копировать»).
- **Аналитика**: KPI (total/hired/reject) + bar по статусам (как на /analytics).
- **Планировщик (M6)**: список интервью; «Назначить» (слоты `GET /interviews/slots:suggest` →
  `POST /interviews`); перенос/отмена; обратная связь (`POST /interviews/{id}:feedback`).
- **Настройки**: статус/headcount/description → `PATCH /vacancies/{id}`.

### Отклик — `/applications/:id`
Данные: `GET /applications/{id}`; кандидат `GET /candidates/{c}`; вакансия `GET /vacancies/{v}`;
M1 `GET /screening/applications/{id}`; M2 `GET /risk/applications/{id}`; M6 `GET /interviews/vacancies/{v}`.
- Шапка: кандидат (имя) + вакансия (title) + StatusBadge.
- **Таймлайн**: история переходов (когда будет API stage_transitions; пока — текущая стадия/статус).
- **Быстрые действия**: переход (селектор стадии + причина); «Скрининг»/«Риски»/«Вопросы»/«Интервью».
- **Вкладки результатов**: Оценка(M1)/Риски(M2) — переиспользуют панели (run+poll).
- Резюме-вьюер кандидата.

### Аналитика — `/analytics` (расширение G10.7)
- Воронка-санкей (ECharts sankey: статусы → переходы), Портфель вакансий (таблица с конверсиями),
  Источники, ИИ-операции (таблица ai_runs), Здоровье. Селектор вакансии/периода.

---

## G10 — разбивка на шаги (порядок реализации)

- [ ] **G10.1** `DetailLayout` + `useAiJob` + `AIResultPanel`; детальная страница кандидата
  (роут `/candidates/:id`) с вкладками Сводка/Резюме/Отклики; реестр → navigate.
- [ ] **G10.2** M1-панель: генерация критериев + скрининг (run+poll) + таблица результата +
  Подтвердить/Оспорить; на кандидате (Оценка) и вакансии (Критерии).
- [ ] **G10.3** M2-панель: анализ рисков (run+poll) + signals + бейдж; на кандидате (Риски).
- [ ] **G10.4** M3-панель: генерация вопросов (run+poll) + карточки + утверждение; на кандидате (Вопросы).
- [ ] **G10.5** Детальная страница вакансии (Описание/Критерии/Воронка-канбан/Карта поиска(M4)/
  Аналитика/Планировщик(M6)/Настройки); `KanbanBoard` с DnD-переходом.
- [ ] **G10.6** Детальная страница отклика (таймлайн + быстрые действия + вкладки M1/M2 + M6).
- [ ] **G10.7** Аналитика: воронка-санкей, портфель вакансий, ИИ-операции; полировка (G13 частично).

Каждый шаг: реализация → `tsc`/`build` зелёные → коммит (обновление `AGENTLOG.MD` + чекбокс) →
push → redeploy frontend.

## Зависимости/заметки
- M1/M2 на кандидате требуют application_id → селектор вакансии (какой отклик оцениваем).
- `useAiJob` опрашивает GET каждые 2с; без AI-ключа воркер падает → статус error (UI показывает
  «ошибка воркера, проверьте AI-ключ»).
- Канбан DnD: `@dnd-kit/core` (добавить dep) или native HTML5 DnD.
- Имена кандидатов/вакансий в откликах: подгружать через `GET /candidates/{id}` и `GET /vacancies/{id}`
  (ApplicationOut не содержит имён) — кэш в TanStack Query.
