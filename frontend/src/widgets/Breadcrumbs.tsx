import { Link } from '@tanstack/react-router'
import { ChevronRight } from 'lucide-react'

export interface BreadcrumbItem {
  label: string
  to?: string
}

export function Breadcrumbs({ items }: { items: BreadcrumbItem[] }) {
  return (
    <nav className="flex items-center gap-1 text-sm text-[var(--text-tertiary)]">
      {items.map((item, i) => (
        <span key={i} className="flex items-center gap-1">
          {i > 0 && <ChevronRight size={14} className="text-[var(--text-tertiary)]" />}
          {item.to ? (
            <Link
              to={item.to}
              className="transition-colors hover:text-[var(--text-primary)]"
            >
              {item.label}
            </Link>
          ) : (
            <span className="text-[var(--text-secondary)]">{item.label}</span>
          )}
        </span>
      ))}
    </nav>
  )
}
