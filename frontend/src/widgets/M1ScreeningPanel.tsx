import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AIResultPanel } from '@/widgets/AIResultPanel'
import { useAiJob } from '@/shared/api/useAiJob'
import { ScreeningResultView } from '@/widgets/ScreeningResultView'
import { fetchApplications } from '@/entities/application/api'
import type { Criterion, RequirementSetOut, ScreeningResultOut } from '@/shared/api/types'

const selectClass =
  'rounded-lg border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 text-sm text-[var(--text-primary)] outline-none transition-colors focus:border-[var(--accent-blue)] focus:ring-2 focus:ring-[var(--accent-blue)]/30'

function CriteriaList({ req }: { req: RequirementSetOut }) {
  return (
    <ul className="flex flex-col gap-2">
      {req.requirements.map((c: Criterion, i: number) => (
        <li
          key={i}
          className="rounded-md border border-[var(--glass-border)] bg-[var(--surface-sunken)] p-3"
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-[var(--text-primary)]">
              {c.criterion}
            </span>
            <span className="text-xs text-[var(--text-tertiary)]">
              вес {c.weight.toFixed(2)}
            </span>
          </div>
          {c.description && (
            <p className="mt-1 text-xs text-[var(--text-secondary)]">{c.description}</p>
          )}
        </li>
      ))}
    </ul>
  )
}

export function M1ScreeningPanel({ candidateId }: { candidateId: string }) {
  const { data: appsData } = useQuery({
    queryKey: ['applications', 'candidate', candidateId],
    queryFn: ({ signal }) => fetchApplications({ candidateId, signal }),
  })
  const apps = appsData?.items ?? []
  const [appId, setAppId] = useState('')
  const app = apps.find((a) => a.id === appId)
  const vacancyId = app?.vacancy_id ?? ''

  const reqJob = useAiJob<RequirementSetOut>({
    runPath: `/api/v1/screening/vacancies/${vacancyId}/requirements:generate`,
    pollPath: `/api/v1/screening/vacancies/${vacancyId}/requirements`,
  })
  const screenJob = useAiJob<ScreeningResultOut>({
    runPath: `/api/v1/screening/applications/${appId}:run`,
    pollPath: `/api/v1/screening/applications/${appId}`,
  })

  return (
    <div className="flex flex-col gap-4">
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium text-[var(--text-secondary)]">
          Отклик (вакансия для оценки)
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
          У кандидата нет откликов — создайте отклик, чтобы запустить скрининг.
        </p>
      )}

      {appId && (
        <>
          <AIResultPanel
            title="Критерии отбора"
            description="ИИ-генерация критериев для вакансии"
            status={reqJob.status}
            error={reqJob.error}
            onRun={reqJob.run}
          >
            {reqJob.result && <CriteriaList req={reqJob.result} />}
          </AIResultPanel>

          <AIResultPanel
            title="Скрининг кандидата"
            description="Оценка по критериям на основе резюме"
            status={screenJob.status}
            error={screenJob.error}
            onRun={screenJob.run}
          >
            {screenJob.result && <ScreeningResultView result={screenJob.result} />}
          </AIResultPanel>
        </>
      )}
    </div>
  )
}
