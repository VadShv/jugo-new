import { Link, useLocation } from '@tanstack/react-router'
import {
  BarChart3,
  Briefcase,
  ClipboardList,
  Users,
  type LucideIcon,
} from 'lucide-react'
import { cn } from '@/shared/ui/cn'

interface NavItem {
  to: string
  label: string
  icon: LucideIcon
}

interface NavSection {
  section: string
  items: NavItem[]
}

const NAV: NavSection[] = [
  {
    section: 'Реестры',
    items: [
      { to: '/applications', label: 'Отклики', icon: ClipboardList },
      { to: '/candidates', label: 'Кандидаты', icon: Users },
      { to: '/vacancies', label: 'Вакансии', icon: Briefcase },
    ],
  },
  {
    section: 'Аналитика',
    items: [{ to: '/analytics', label: 'Дашборды', icon: BarChart3 }],
  },
]

export function Sidebar() {
  const location = useLocation()
  const isActive = (to: string) => location.pathname.startsWith(to)

  return (
    <aside className="hidden w-56 shrink-0 flex-col gap-5 border-r border-[var(--glass-border)] bg-[var(--surface-solid)] p-3 md:flex">
      <Link
        to="/"
        className="flex items-center gap-2 px-2 py-1 text-lg font-semibold text-[var(--text-primary)]"
      >
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[var(--accent-blue)] text-white">
          <Briefcase size={18} />
        </div>
        ATS Jugo
      </Link>

      {NAV.map((group) => (
        <div key={group.section}>
          <div className="mb-1 px-2 text-caption font-medium uppercase tracking-wide text-[var(--text-tertiary)]">
            {group.section}
          </div>
          <nav className="flex flex-col gap-0.5">
            {group.items.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={cn(
                    'flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm transition-colors',
                    isActive(item.to)
                      ? 'bg-[var(--surface-sunken)] font-medium text-[var(--text-primary)]'
                      : 'text-[var(--text-secondary)] hover:bg-[var(--surface-sunken)] hover:text-[var(--text-primary)]',
                  )}
                >
                  <Icon size={18} className="shrink-0" />
                  {item.label}
                </Link>
              )
            })}
          </nav>
        </div>
      ))}
    </aside>
  )
}
