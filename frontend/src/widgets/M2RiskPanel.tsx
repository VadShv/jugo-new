import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AIResultPanel } from '@/widgets/AIResultPanel'
import { useAiJob } from '@/shared/api/useAiJob'
import { StatusBadge } from '@/shared/ui/StatusBadge'
import { fetchApplications } from '@/entities/application/api'
import type { RiskReportOut, RiskSignal } from '@/shared/api/types'

const selectClass =
  'rounded-lg border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 text-sm text-[var(--text-primary)] outline-none transition-colors focus:border-[var(--accent-blue)] focus:ring-2 focus:ring-[var(--accent-blue)]/30'

function SignalCard({ signal }: { signal: RiskSignal }) {
  return (
    <div className="rounded-md border border-[var(--glass-border)] bg-[var(--surface-sunken)] p-3">
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-mono text-xs font-medium text-[var(--text-primary)]">
          {signal.code}
        </span>
        <StatusBadge status={signal.severity} />
        <span className="text-xs text-[var(--text-tertiary)]">
          уверенность {Math.round(signal.confidence * 100)}%
        </span>
      </div>
      {signal.evidence && (
        <p className="mt-2 text-sm text-[var(--text-primary)]">{signal.evidence}</p>
      )}
      {signal.alternative_explanation && (
        <p className="mt-1 text-xs text-[var(--text-secondary)]">
          <span className="font-medium">Альтернатива:</span>{' '}
          {signal.alternative_explanation}
        </p>
      )}
      {signal.verification_question && (
        <p className="mt-1 text-xs text-[var(--text-secondary)]">
          <span className="font-medium">Уточнить:</span>{' '}
          {signal.verification_question}
        </p>
      )}
    </div>
  )
}

function RiskReportView({ report }: { report: RiskReportOut }) {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center gap-3">
        {report.risk_level && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-[var(--text-tertiary)]">Уровень риска</span>
            <StatusBadge status={report.risk_level} size="md" />
          </div>
        )}
        {report.top_risks.length > 0 && (
          <div className="flex flex-wrap items-center gap-1">
            <span className="text-xs text-[var(--text-tertiary)]">Топ-риски:</span>
            {report.top_risks.map((r) => (
              <span
                key={r}
                className="rounded-pill bg-[var(--surface-sunken)] px-2 py-0.5 font-mono text-xs text-[var(--text-secondary)]"
              >
                {r}
              </span>
            ))}
          </div>
        )}
      </div>
      {report.summary && (
        <p className="text-sm text-[var(--text-primary)]">{report.summary}</p>
      )}
      <div className="flex flex-col gap-2">
        {report.signals.map((s, i) => (
          <SignalCard key={i} signal={s} />
        ))}
      </div>
      {report.model && (
        <p className="text-xs text-[var(--text-tertiary)]">
          Модель: {report.model} · whitebox (ai_runs)
        </p>
      )}
    </div>
  )
}

export function M2RiskPanel({ candidateId }: { candidateId: string }) {
  const { data: appsData } = useQuery({
    queryKey: ['applications', 'candidate', candidateId],
    queryFn: ({ signal }) => fetchApplications({ candidateId, signal }),
  })
  const apps = appsData?.items ?? []
  const [appId, setAppId] = useState('')

  const riskJob = useAiJob<RiskReportOut>({
    runPath: `/api/v1/risk/applications/${appId}:run`,
    pollPath: `/api/v1/risk/applications/${appId}`,
  })

  return (
    <div className="flex flex-col gap-4">
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium text-[var(--text-secondary)]">
          Отклик (для анализа рисков)
        </span>
        <select
          value={appId}
          onChange={(e) => setAppId(e.target.value)}
          className={selectClass}
          disabled={apps.length === 0}
        >
          <option value="">— выберите отклик —</option>
          {apps.map((a) => (
            <option key={a.id} value={a.id}>
              {a.vacancy_id} · {a.status}
            </option>
          ))}
        </select>
      </label>

      {apps.length === 0 && (
        <p className="text-sm text-[var(--text-tertiary)]">
          У кандидата нет откликов — создайте отклик для анализа рисков.
        </p>
      )}

      {appId && (
        <AIResultPanel
          title="Анализ рисков"
          description="ИИ-анализ резюме на предмет рисков (несоответствия, пробелы, скачки)"
          status={riskJob.status}
          error={riskJob.error}
          onRun={riskJob.run}
        >
          {riskJob.result && <RiskReportView report={riskJob.result} />}
        </AIResultPanel>
      )}
    </div>
  )
}
