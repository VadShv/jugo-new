import { Link, useLocation } from '@tanstack/react-router'
import { cn } from './cn'

const TABS = [
  { label: 'Вакансии', to: '/vacancies' },
  { label: 'Кандидаты', to: '/candidates' },
  { label: 'Отклики', to: '/applications' },
  { label: 'Аналитика', to: '/analytics' },
] as const

/**
 * Glass tab bar with 5 tabs (Вакансии / Кандидаты / Отклики / Аналитика / Ещё).
 * Active tab uses accent-blue; respects safe-area insets.
 */
export function GlassTabBar() {
  const location = useLocation()

  return (
    <nav
      className="glass glass--regular sticky top-14 z-30 flex items-center gap-1 px-2"
      style={{ paddingTop: 'env(safe-area-inset-top, 0px)' }}
    >
      {TABS.map((tab) => {
        const active = location.pathname.startsWith(tab.to)
        return (
          <Link
            key={tab.to}
            to={tab.to}
            className={cn(
              'flex-1 rounded-pill px-3 py-2 text-center text-sm font-medium transition-colors',
              active
                ? 'bg-[var(--accent-blue)] text-white'
                : 'text-[var(--text-secondary)] hover:bg-[var(--surface-sunken)]',
            )}
          >
            {tab.label}
          </Link>
        )
      })}
      <button
        type="button"
        className="flex-1 rounded-pill px-3 py-2 text-center text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--surface-sunken)]"
      >
        Ещё
      </button>
    </nav>
  )
}
