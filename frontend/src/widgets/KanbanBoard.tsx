import { useState } from 'react'
import { StatusBadge } from '@/shared/ui/StatusBadge'
import type { Application, FunnelStage } from '@/shared/api/types'

export interface KanbanBoardProps {
  stages: FunnelStage[]
  applications: Application[]
  onTransition: (applicationId: string, toStageId: string) => void
}

/**
 * Kanban board with native HTML5 drag-and-drop. Columns = funnel stages,
 * cards = applications. Dropping a card onto a column triggers a transition.
 */
export function KanbanBoard({ stages, applications, onTransition }: KanbanBoardProps) {
  const [dragId, setDragId] = useState<string | null>(null)
  const [overStage, setOverStage] = useState<string | null>(null)

  const byStage = (stageId: string) =>
    applications.filter((a) => a.current_stage_id === stageId)

  return (
    <div className="flex gap-3 overflow-x-auto pb-2">
      {stages.map((stage) => {
        const apps = byStage(stage.id)
        return (
          <div
            key={stage.id}
            onDragOver={(e) => {
              e.preventDefault()
              setOverStage(stage.id)
            }}
            onDragLeave={() => setOverStage((s) => (s === stage.id ? null : s))}
            onDrop={() => {
              if (dragId) onTransition(dragId, stage.id)
              setDragId(null)
              setOverStage(null)
            }}
            className={`flex w-60 shrink-0 flex-col rounded-lg border bg-[var(--surface-sunken)] transition-colors ${
              overStage === stage.id
                ? 'border-[var(--accent-blue)]'
                : 'border-[var(--glass-border)]'
            }`}
          >
            <div className="flex items-center justify-between border-b border-[var(--glass-border)] px-3 py-2">
              <span className="text-sm font-medium text-[var(--text-primary)]">
                {stage.name}
              </span>
              <span className="rounded-pill bg-[var(--surface-solid)] px-1.5 text-xs text-[var(--text-tertiary)]">
                {apps.length}
              </span>
            </div>
            <div className="flex min-h-[80px] flex-col gap-2 p-2">
              {apps.map((app) => (
                <div
                  key={app.id}
                  draggable
                  onDragStart={() => setDragId(app.id)}
                  className="cursor-grab rounded-md border border-[var(--glass-border)] bg-[var(--surface-solid)] p-2 shadow-card active:cursor-grabbing"
                >
                  <div className="font-mono text-xs text-[var(--text-secondary)]">
                    {app.candidate_id.slice(0, 8)}
                  </div>
                  <div className="mt-1">
                    <StatusBadge status={app.status} />
                  </div>
                </div>
              ))}
              {apps.length === 0 && (
                <div className="py-2 text-center text-xs text-[var(--text-tertiary)]">
                  пусто
                </div>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}
