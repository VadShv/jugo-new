import type { ReactNode } from 'react'
import { cn } from '@/shared/ui/cn'

export interface CardProps {
  children: ReactNode
  className?: string
  header?: ReactNode
  footer?: ReactNode
  elevated?: boolean
}

/** Unified card: border + surface + shadow, optional header/footer. */
export function Card({ children, className, header, footer, elevated }: CardProps) {
  return (
    <div
      className={cn(
        'rounded-lg border border-[var(--glass-border)] bg-[var(--surface-solid)]',
        elevated ? 'shadow-elevated' : 'shadow-card',
        className,
      )}
    >
      {header && (
        <div className="border-b border-[var(--glass-border)] px-4 py-3">{header}</div>
      )}
      <div className="p-4">{children}</div>
      {footer && (
        <div className="border-t border-[var(--glass-border)] px-4 py-3">{footer}</div>
      )}
    </div>
  )
}
