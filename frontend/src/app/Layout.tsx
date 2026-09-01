import { Outlet, useNavigate } from '@tanstack/react-router'
import { LogOut, Moon, Sun } from 'lucide-react'
import { GlassTopBar } from '@/shared/ui/GlassTopBar'
import { Sidebar } from '@/widgets/Sidebar'
import { useGlassCapability } from '@/shared/ui/glass'
import { useTheme } from '@/shared/ui/theme'
import { clearToken } from '@/shared/api/auth'

/**
 * App shell: sidebar (enterprise navigation) + glass top bar (theme/logout) +
 * routed outlet. The glass capability hook mirrors the device fallback.
 */
export function Layout() {
  useGlassCapability()
  const navigate = useNavigate()
  const { dark, toggle } = useTheme()

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
          trailing={
            <>
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
    </div>
  )
}
