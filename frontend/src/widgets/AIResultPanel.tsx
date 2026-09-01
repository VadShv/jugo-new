import type { ReactNode } from 'react'
import type { AiJobStatus } from '@/shared/api/useAiJob'

export interface AIResultPanelProps {
  title: string
  description?: string
  status: AiJobStatus
  error?: string | null
  onRun: () => void
  /** Rendered when status === 'done'. */
  children?: ReactNode
}

/**
 * Presentational wrapper for an async AI action: a "Run" button + status states
 * (idle/running/error) + a slot for the result. Whitebox "Как получен?" is
 * rendered by the caller inside children when available.
 */
export function AIResultPanel({
  title,
  description,
  status,
  error,
  onRun,
  children,
}: AIResultPanelProps) {
  return (
    <section className="rounded-lg border border-[var(--glass-border)] bg-[var(--surface-solid)] p-4 shadow-card">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-[var(--text-primary)]">{title}</h3>
          {description && (
            <p className="text-xs text-[var(--text-tertiary)]">{description}</p>
          )}
        </div>
        <button
          type="button"
          onClick={onRun}
          disabled={status === 'running'}
          className="shrink-0 rounded-pill bg-[var(--accent-blue)] px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50"
        >
          {status === 'running' ? 'Выполняется…' : 'Запустить'}
        </button>
      </div>

      {status === 'idle' && (
        <p className="text-sm text-[var(--text-tertiary)]">
          Нажмите «Запустить», чтобы сгенерировать.
        </p>
      )}
      {status === 'running' && (
        <p className="text-sm text-[var(--text-secondary)]">Опрос результата…</p>
      )}
      {status === 'error' && (
        <p className="text-sm text-[var(--accent-red)]">
          {error ?? 'Ошибка'} (проверьте AI-ключ и воркер)
        </p>
      )}
      {status === 'done' && children}
    </section>
  )
}
