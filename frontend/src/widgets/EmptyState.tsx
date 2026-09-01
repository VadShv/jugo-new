import type { ReactNode } from 'react'
import type { LucideIcon } from 'lucide-react'

export interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description?: string
  action?: ReactNode
}

/** Professional empty state: icon in a circle + title + description + optional CTA. */
export function EmptyState({ icon: Icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center gap-3 py-12 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-[var(--surface-sunken)]">
        <Icon size={24} className="text-[var(--text-tertiary)]" />
      </div>
      <div>
        <p className="text-sm font-medium text-[var(--text-secondary)]">{title}</p>
        {description && (
          <p className="mt-1 text-xs text-[var(--text-tertiary)]">{description}</p>
        )}
      </div>
      {action && <div>{action}</div>}
    </div>
  )
}
