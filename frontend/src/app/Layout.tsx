import { useState } from 'react'
import { Link, Outlet, useNavigate } from '@tanstack/react-router'
import {
  BarChart3,
  Briefcase,
  ClipboardList,
  LogOut,
  Menu,
  Moon,
  Sun,
  Users,
  type LucideIcon,
} from 'lucide-react'
import { GlassTopBar } from '@/shared/ui/GlassTopBar'
import { GlassSheet } from '@/shared/ui/GlassSheet'
import { Sidebar } from '@/widgets/Sidebar'
import { NotificationBell } from '@/widgets/NotificationBell'
import { useGlassCapability } from '@/shared/ui/glass'
import { useTheme } from '@/shared/ui/theme'
import { clearToken } from '@/shared/api/auth'

interface MobileNavItem {
  to: string
  label: string
  icon: LucideIcon
}

const MOBILE_NAV: MobileNavItem[] = [
  { to: '/applications', label: 'Отклики', icon: ClipboardList },
  { to: '/candidates', label: 'Кандидаты', icon: Users },
  { to: '/vacancies', label: 'Вакансии', icon: Briefcase },
  { to: '/analytics', label: 'Аналитика', icon: BarChart3 },
]

export function Layout() {
  useGlassCapability()
  const navigate = useNavigate()
  const { dark, toggle } = useTheme()
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  const logout = () => {
    clearToken()
    void navigate({ to: '/login' })
  }

  return (
    <div className="flex min-h-screen bg-[var(--surface-canvas)]">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <GlassTopBar
          title="ATS Jugo"
          leading={
            <button
              type="button"
              onClick={() => setMobileNavOpen(true)}
              aria-label="Меню"
              className="inline-flex items-center justify-center rounded-pill p-1.5 text-[var(--text-secondary)] hover:bg-[var(--surface-sunken)] md:hidden"
            >
              <Menu size={20} />
            </button>
          }
          trailing={
            <>
              <NotificationBell />
              <button
                type="button"
                onClick={toggle}
                aria-label="Переключить тему"
                className="inline-flex items-center justify-center rounded-pill px-2.5 py-1.5 text-[var(--text-secondary)] hover:bg-[var(--surface-sunken)]"
              >
                {dark ? <Sun size={16} /> : <Moon size={16} />}
              </button>
              <button
                type="button"
                onClick={logout}
                className="inline-flex items-center gap-1 rounded-pill px-3 py-1.5 text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--surface-sunken)]"
              >
                <LogOut size={16} /> Выйти
              </button>
            </>
          }
        />
        <main className="mx-auto w-full max-w-6xl animate-[fade-in_300ms_ease] px-4 py-5">
          <Outlet />
        </main>
        <footer className="border-t border-[var(--glass-border)] px-4 py-3 text-center text-caption text-[var(--text-tertiary)]">
          ATS Jugo v1.0 · FastAPI + React · cloud.ru
        </footer>
      </div>

      <GlassSheet
        open={mobileNavOpen}
        onOpenChange={setMobileNavOpen}
        title="Навигация"
      >
        <nav className="flex flex-col gap-1">
          {MOBILE_NAV.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.to}
                to={item.to}
                onClick={() => setMobileNavOpen(false)}
                className="flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm text-[var(--text-secondary)] hover:bg-[var(--surface-sunken)] hover:text-[var(--text-primary)]"
              >
                <Icon size={18} />
                {item.label}
              </Link>
            )
          })}
        </nav>
      </GlassSheet>
    </div>
  )
}
