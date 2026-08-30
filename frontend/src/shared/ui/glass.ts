import { useEffect, useState } from 'react'

export type GlassLevel = 'regular' | 'clear' | 'identity'

export interface GlassCapability {
  level: GlassLevel
}

function detectLevel(): GlassLevel {
  if (typeof window === 'undefined') return 'identity'

  let supportsBackdrop = false
  try {
    supportsBackdrop =
      CSS.supports('backdrop-filter', 'blur(1px)') ||
      CSS.supports('-webkit-backdrop-filter', 'blur(1px)')
  } catch {
    supportsBackdrop = false
  }
  if (!supportsBackdrop) return 'identity'

  let reduceTransparency = false
  try {
    reduceTransparency = window
      .matchMedia('(prefers-reduced-transparency: reduce)')
      .matches
  } catch {
    reduceTransparency = false
  }
  if (reduceTransparency) return 'identity'

  const cores = navigator.hardwareConcurrency ?? 8
  const memory =
    (navigator as Navigator & { deviceMemory?: number }).deviceMemory ?? 8
  if (cores <= 4 || memory <= 4) return 'identity'

  return 'regular'
}

/**
 * Detects the device's glass capability and mirrors the result onto the
 * <html> element via the `glass-identity` class so CSS can fall back to an
 * opaque surface. Animate only transform/opacity; glass uses
 * `contain: layout style paint` (see tokens.css).
 */
export function useGlassCapability(): GlassCapability {
  const [level] = useState<GlassLevel>(() => detectLevel())

  useEffect(() => {
    const root = document.documentElement
    root.classList.toggle('glass-identity', level === 'identity')
  }, [level])

  return { level }
}
