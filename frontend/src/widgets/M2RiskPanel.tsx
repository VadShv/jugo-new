import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AIResultPanel } from '@/widgets/AIResultPanel'
import { useAiJob } from '@/shared/api/useAiJob'
import { RiskReportView } from '@/widgets/RiskReportView'
import { fetchApplications } from '@/entities/application/api'
import type { RiskReportOut } from '@/shared/api/types'

const selectClass =
  'rounded-lg border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 text-sm text-[var(--text-primary)] outline-none transition-colors focus:border-[var(--accent-blue)] focus:ring-2 focus:ring-[var(--accent-blue)]/30'

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
