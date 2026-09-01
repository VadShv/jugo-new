import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from './cn'

const STATUS_META: Record<string, { label: string; accent: string }> = {
  new: { label: 'Новый', accent: 'var(--accent-blue)' },
  in_progress: { label: 'В работе', accent: 'var(--accent-purple)' },
  screening: { label: 'Скрининг', accent: 'var(--accent-orange)' },
  interview: { label: 'Интервью', accent: 'var(--accent-teal)' },
  offer: { label: 'Оффер', accent: 'var(--accent-green)' },
  hired: { label: 'Нанят', accent: 'var(--accent-green)' },
  rejected: { label: 'Отказ', accent: 'var(--accent-red)' },
  withdrawn: { label: 'Отозван', accent: 'var(--text-tertiary)' },
  draft: { label: 'Черновик', accent: 'var(--text-tertiary)' },
  open: { label: 'Открыта', accent: 'var(--accent-blue)' },
  paused: { label: 'Пауза', accent: 'var(--accent-orange)' },
  closed: { label: 'Закрыта', accent: 'var(--text-tertiary)' },
  on_hold: { label: 'On hold', accent: 'var(--accent-orange)' },
  low: { label: 'Низкий', accent: 'var(--accent-green)' },
  medium: { label: 'Средний', accent: 'var(--accent-orange)' },
  high: { label: 'Высокий', accent: 'var(--accent-red)' },
}

const badge = cva(
  'inline-flex items-center rounded-pill text-xs font-medium tabular-nums',
  {
    variants: {
      size: { sm: 'px-2 py-0.5', md: 'px-2.5 py-1' },
    },
    defaultVariants: { size: 'sm' },
  },
)

export interface StatusBadgeProps extends VariantProps<typeof badge> {
  status: string
  className?: string
}

/**
 * Caption-sized status badge. Background is the status accent at 14% alpha,
 * foreground is the full accent. Covers application + vacancy statuses with a
 * fallback (grey, raw label) for unknown values.
 */
export function StatusBadge({ status, size, className }: StatusBadgeProps) {
  const meta = STATUS_META[status] ?? {
    label: status,
    accent: 'var(--text-tertiary)',
  }
  return (
    <span
      className={cn(badge({ size }), className)}
      style={{
        backgroundColor: `color-mix(in srgb, ${meta.accent} 14%, transparent)`,
        color: meta.accent,
      }}
    >
      {meta.label}
    </span>
  )
}
