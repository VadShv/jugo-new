import { cn } from './cn'

export interface SegmentedOption {
  label: string
  value: string
}

export interface GlassSegmentedControlProps {
  options: SegmentedOption[]
  value: string
  onChange: (value: string) => void
  className?: string
}

/**
 * Pill segmented control with a sliding indicator (translateX only).
 */
export function GlassSegmentedControl({
  options,
  value,
  onChange,
  className,
}: GlassSegmentedControlProps) {
  const index = Math.max(
    0,
    options.findIndex((option) => option.value === value),
  )

  return (
    <div
      className={cn(
        'relative inline-flex rounded-pill bg-[var(--surface-sunken)] p-1',
        className,
      )}
    >
      <div
        className="absolute inset-y-1 left-1 rounded-pill bg-[var(--surface-solid)] shadow-card transition-transform"
        style={{
          width: `calc((100% - 0.5rem) / ${options.length})`,
          transform: `translateX(${index * 100}%)`,
          transitionTimingFunction: 'var(--ease-spring)',
          transitionDuration: 'var(--dur-base)',
        }}
      />
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onChange(option.value)}
          className={cn(
            'relative z-10 flex-1 rounded-pill px-3 py-1 text-sm font-medium transition-colors',
            value === option.value
              ? 'text-[var(--text-primary)]'
              : 'text-[var(--text-secondary)]',
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  )
}
