import { cva, type VariantProps } from 'class-variance-authority'
import type { Stage } from '@/shared/api/types'
import { cn } from './cn'

const STAGE_META: Record<Stage, { label: string; accent: string }> = {
  new: { label: 'Новый', accent: 'var(--accent-blue)' },
  screening: { label: 'Скрининг', accent: 'var(--accent-orange)' },
  interview: { label: 'Интервью', accent: 'var(--accent-purple)' },
  offer: { label: 'Оффер', accent: 'var(--accent-green)' },
  rejected: { label: 'Отказ', accent: 'var(--accent-red)' },
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
  stage: Stage
  className?: string
}

/**
 * Caption-sized stage badge. Background is the stage accent at 14% alpha,
 * foreground is the full accent. Stages: Новый / Скрининг / Интервью /
 * Оффер / Отказ.
 */
export function StatusBadge({ stage, size, className }: StatusBadgeProps) {
  const meta = STAGE_META[stage]
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
