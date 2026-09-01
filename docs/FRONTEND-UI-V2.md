# FRONTEND-UI-V2 — план фундаментальной и богатой доработки интерфейса

Цель: превратить рабочий UI v1.0 в **фундаментальный, богатый, профессиональный** продукт.
Принцип: каждое изменение — небольшое, проверяемое (`tsc`/`build` зелёные), деплоится.
Легенда: `[ ]` не начато · `[~]` в работе · `[x]` готово.

---

## UI-1. Визуальный фундамент (богатый базис)

**Цель**: единая типографика, глубина поверхностей, профессиональные карточки, иконки.

- [ ] **UI-1.1 Типографика**: Tailwind `theme.extend.fontSize` — роли (display/lg/base/sm/xs/caption), `fontWeight` (400/500/600/700), `lineHeight` (1.2/1.4/1.5/1.6). Применить во всех заголовках/тексте.
- [ ] **UI-1.2 Глубина поверхностей**: добавить `--surface-elevated` (между solid и sunken), `--shadow-elevated` (глубже card), градиентные акценты на ключевых кнопках. Обновить `tokens.css`.
- [ ] **UI-1.3 Карточка-компонент** `widgets/Card.tsx`: unified card (header/body/footer, padding variants, shadow). Заменить inline `rounded-md border ... shadow-card` на `<Card>`.
- [ ] **UI-1.4 Иконки**: добавить `lucide-react` иконки во все ключевые места (реестры, кнопки, табы, empty states). Единый размер (16/20/24) + цвет из токенов.
- [ ] **UI-1.5 Скелетоны** `widgets/Skeleton.tsx`: shimmer-заглушки вместо «Загрузка…» (table rows, cards, detail pages). CSS `@keyframes shimmer`.
- [ ] **UI-1.6 Тосты** `widgets/Toaster.tsx`: Radix Toast — success/error/info на мутациях (создание, переход, AI-run). Единая очередь.

## UI-2. Структура и навигация (фундаментальность)

**Цель**: enterprise-навигация, контекст, обзорная страница.

- [ ] **UI-2.1 Sidebar** `widgets/Sidebar.tsx`: collapsible левая панель (Реестры: Вакансии/Кандидаты/Отклики · Аналитика · Настройки). Иконки + активный state. Заменить таб-бар на sidebar (таб-бар → мобильный).
- [ ] **UI-2.2 Breadcrumbs** `widgets/Breadcrumbs.tsx`: контекст (Главная > Кандидаты > Иван Петров). На детальных страницах.
- [ ] **UI-2.3 PageHeader** `widgets/PageHeader.tsx`: заголовок + подзаголовок + actions + breadcrumb. Заменить inline `<h1>` в DetailLayout.
- [ ] **UI-2.4 Dashboard** `pages/DashboardPage.tsx`: обзорная главная — KPI-карточки (вакансий/кандидатов/откликов/найм%), последние отклики, график активности. Роут `/` → dashboard.
- [ ] **UI-2.5 Глобальный поиск** `widgets/CommandPalette.tsx`: Ctrl+K → поиск по кандидатам/вакансиям/откликам (через `POST /search`). Radix Dialog + keyboard.
- [ ] **UI-2.6 Уведомления** `widgets/NotificationBell.tsx`: SSE-лента (`/api/v1/events/stream`) — колокольчик с непрочитанными, dropdown со списком событий.

## UI-3. Качество данных (богатая подача)

**Цель**: профессиональные таблицы, формы, пустые состояния, диалоги.

- [ ] **UI-3.1 Empty states** `widgets/EmptyState.tsx`: иконка + заголовок + описание + CTA-кнопка. Заменить «Ничего не найдено» / «Нет откликов».
- [ ] **UI-3.2 Таблицы v2**: header sort (click → sort), row selection (checkbox), pagination UI (стрелки + page info), sticky header, column resize. Обновить `RegistryTable`.
- [ ] **UI-3.3 Формы v2**: field groups (fieldset + legend), inline validation (иконка + текст под полем), submit feedback (spinner в кнопке). Обновить все формы.
- [ ] **UI-3.4 Confirm dialog** `widgets/ConfirmDialog.tsx`: Radix AlertDialog для деструктивных действий (отклонить, удалить, отменить интервью).
- [ ] **UI-3.5 Copy feedback**: toast «Скопировано» при копировании поисковых строк (M4 паспорта).
- [ ] **UI-3.6 Badge improvements**: pill-бейджи с dot-индикатором (онлайн/офлайн статус), count-бейджи на табах (количество откликов/скринингов).

## UI-4. Микровзаимодействия (богатство деталей)

**Цель**: плавность, отзывчивость, визуальная обратная связь.

- [ ] **UI-4.1 Hover/focus**: единые `hover:` и `focus:` стили на всех кнопках/карточках/строках (transition + subtle bg/shadow change).
- [ ] **UI-4.2 Loading buttons**: spinner в кнопке во время async (создание, AI-run, переход). `widgets/LoadingButton.tsx`.
- [ ] **UI-4.3 Tab transitions**: плавный fade/slide при переключении табов (Radix Tabs + CSS `data-[state=...]`).
- [ ] **UI-4.4 Kanban DnD feedback**: подсветка drop-zone (border + bg), drag-ghost (opacity), snap animation.
- [ ] **UI-4.5 Chart tooltips**: richer ECharts tooltips (formatter с %, цветными точками, заголовком).
- [ ] **UI-4.6 Page transitions**: fade-in при навигации (TanStack Router `beforeLoad` + CSS class).

## UI-5. Профессиональные штрихи (фундаментальность)

**Цель**: продукт-уровень детализации.

- [ ] **UI-5.1 Favicon + page titles**: favicon.svg (Jugo logo), `useDocumentTitle` per route (TanStack Router).
- [ ] **UI-5.2 Footer**: версия, статус (backend /live), ссылки. В Layout.
- [ ] **UI-5.3 Error boundary** `widgets/ErrorBoundary.tsx`: graceful error page (иконка + сообщение + «перезагрузить») вместо white screen.
- [ ] **UI-5.4 Responsive**: mobile-friendly (sidebar → drawer, таблицы → карточки, формы → stacked). Breakpoints `sm/md/lg`.
- [ ] **UI-5.5 Accessibility**: ARIA labels на всех кнопках/табах/диалогах, focus-ring visible, keyboard nav (Tab/Enter/Escape), `prefers-reduced-motion`.
- [ ] **UI-5.6 Lazy-load echarts**: `React.lazy(() => import('echarts-for-react'))` + Suspense → echarts chunk грузится только на /analytics. Убирает 1MB из initial load.

---

## Порядок выполнения
UI-1 (фундамент) → UI-2 (структура) → UI-3 (данные) → UI-4 (детали) → UI-5 (штрихи).
Каждый шаг: реализация → `tsc`/`build` зелёные → коммит (AGENTLOG + чекбокс) → push → redeploy frontend.

## Зависимости
- UI-2.6 (уведомления) зависит от SSE (готов, G6).
- UI-2.5 (поиск) зависит от `POST /search` (готов, G3).
- UI-2.4 (dashboard) зависит от `/analytics/*` (готов, G5) + CRUD list counts.
- UI-5.6 (lazy echarts) требует Suspense + React.lazy — проверить совместимость с TanStack Router.
