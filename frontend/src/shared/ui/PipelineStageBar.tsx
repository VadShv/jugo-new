import { cn } from './cn'

export interface PipelineStage {
  id: string
  label: string
  count: number
  accent?: string
}

export interface PipelineStageBarProps {
  stages: PipelineStage[]
  className?: string
}

/**
 * Horizontally scrollable pipeline capsules with counts. Each capsule is
 * tinted with its accent at 12% alpha.
 */
export function PipelineStageBar({ stages, className }: PipelineStageBarProps) {
  return (
    <div className={cn('flex gap-2 overflow-x-auto pb-1', className)}>
      {stages.map((stage) => {
        const accent = stage.accent ?? 'var(--accent-blue)'
        return (
          <div
            key={stage.id}
            className="flex shrink-0 items-center gap-2 rounded-pill px-3 py-1.5 text-sm"
            style={{
              backgroundColor: `color-mix(in srgb, ${accent} 12%, transparent)`,
            }}
          >
            <span className="font-medium text-[var(--text-primary)]">
              {stage.label}
            </span>
            <span className="rounded-pill bg-[var(--surface-solid)] px-1.5 text-xs tabular-nums text-[var(--text-secondary)]">
              {stage.count}
            </span>
          </div>
        )
      })}
    </div>
  )
}
