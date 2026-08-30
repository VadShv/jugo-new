import { Outlet } from '@tanstack/react-router'
import { GlassTopBar } from '@/shared/ui/GlassTopBar'
import { GlassTabBar } from '@/shared/ui/GlassTabBar'
import { useGlassCapability } from '@/shared/ui/glass'

/**
 * App shell: a global glass top bar (brand) + glass tab bar + routed outlet.
 * The glass capability hook mirrors the device fallback onto <html>.
 */
export function Layout() {
  useGlassCapability()

  return (
    <div className="min-h-screen bg-[var(--surface-canvas)]">
      <GlassTopBar title="ATS Jugo" />
      <GlassTabBar />
      <main className="mx-auto max-w-6xl px-4 py-4">
        <Outlet />
      </main>
    </div>
  )
}
