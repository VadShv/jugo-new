import { Search, X } from 'lucide-react'
import { cn } from './cn'

export interface GlassSearchFieldProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  className?: string
}

/**
 * Pill search field (40px) with a magnifier glyph and a clear button.
 * Uses glass-clear; switches to surface-sunken on focus.
 */
export function GlassSearchField({
  value,
  onChange,
  placeholder,
  className,
}: GlassSearchFieldProps) {
  return (
    <div
      className={cn(
        'glass glass--clear flex h-10 items-center gap-2 rounded-pill px-3',
        'focus-within:bg-[var(--surface-sunken)] focus-within:ring-2 focus-within:ring-[var(--accent-blue)]/40',
        className,
      )}
    >
      <Search size={16} className="shrink-0 text-[var(--text-tertiary)]" />
      <input
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className="h-full flex-1 bg-transparent text-sm text-[var(--text-primary)] outline-none placeholder:text-[var(--text-tertiary)]"
      />
      {value.length > 0 && (
        <button
          type="button"
          aria-label="Очистить"
          onClick={() => onChange('')}
          className="shrink-0 text-[var(--text-tertiary)] hover:text-[var(--text-primary)]"
        >
          <X size={16} />
        </button>
      )}
    </div>
  )
}
