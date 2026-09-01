import { Outlet, useNavigate } from '@tanstack/react-router'
import { LogOut, Moon, Sun } from 'lucide-react'
import { GlassTopBar } from '@/shared/ui/GlassTopBar'
import { GlassTabBar } from '@/shared/ui/GlassTabBar'
import { useGlassCapability } from '@/shared/ui/glass'
import { useTheme } from '@/shared/ui/theme'
import { clearToken } from '@/shared/api/auth'

/**
 * App shell: a global glass top bar (brand + theme toggle + logout) + glass tab
 * bar + routed outlet. The glass capability hook mirrors the device fallback.
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
    <div className="min-h-screen bg-[var(--surface-canvas)]">
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
      <GlassTabBar />
      <main className="mx-auto max-w-6xl px-4 py-4">
        <Outlet />
      </main>
    </div>
  )
}
