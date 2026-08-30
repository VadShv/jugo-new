import * as React from 'react'
import { cn } from './cn'

export interface GlassTopBarProps {
  leading?: React.ReactNode
  title?: React.ReactNode
  trailing?: React.ReactNode
  sticky?: boolean
  className?: string
}

/**
 * Sticky 56px translucent top bar (navigation layer). Glass regular with
 * backdrop-filter blur(16px) saturate(180%), a top-edge highlight via ::before,
 * an @supports fallback to opaque, and `contain: layout style paint`.
 */
export function GlassTopBar({
  leading,
  title,
  trailing,
  sticky = true,
  className,
}: GlassTopBarProps) {
  return (
    <header
      className={cn(
        'glass glass--regular flex h-14 w-full items-center gap-3 border-b px-4',
        sticky ? 'sticky top-0 z-40' : 'relative z-40',
        className,
      )}
    >
      {leading != null && (
        <div className="flex shrink-0 items-center">{leading}</div>
      )}
      {title != null && (
        <div className="min-w-0 flex-1 truncate text-base font-semibold text-[var(--text-on-glass)]">
          {title}
        </div>
      )}
      {trailing != null && (
        <div className="flex shrink-0 items-center gap-2">{trailing}</div>
      )}
    </header>
  )
}
