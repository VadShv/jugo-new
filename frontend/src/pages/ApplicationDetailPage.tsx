import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useParams } from '@tanstack/react-router'
import { ArrowLeft } from 'lucide-react'
import { GlassTopBar } from '@/shared/ui/GlassTopBar'
import { StatusBadge } from '@/shared/ui/StatusBadge'
import { DetailLayout, type DetailTab } from '@/widgets/DetailLayout'
import { AIResultPanel } from '@/widgets/AIResultPanel'
import { useAiJob } from '@/shared/api/useAiJob'
import { ScreeningResultView } from '@/widgets/ScreeningResultView'
import { RiskReportView } from '@/widgets/RiskReportView'
import {
  fetchApplication,
  transitionApplication,
} from '@/entities/application/api'
import { fetchCandidate } from '@/entities/candidate/api'
import { fetchVacancy } from '@/entities/vacancy/api'
import { useDefaultStages } from '@/entities/funnel/api'
import { fieldClass } from '@/shared/ui/field'
import type { RiskReportOut, ScreeningResultOut } from '@/shared/api/types'

function TimelineTab({ applicationId }: { applicationId: string }) {
  const queryClient = useQueryClient()
  const { data: app } = useQuery({
    queryKey: ['application', applicationId],
    queryFn: ({ signal }) => fetchApplication(applicationId, signal),
  })
  const { data: candidate } = useQuery({
    queryKey: ['candidate', app?.candidate_id],
    enabled: !!app,
    queryFn: ({ signal }) => fetchCandidate(app!.candidate_id, signal),
  })
  const { data: vacancy } = useQuery({
    queryKey: ['vacancy', app?.vacancy_id],
    enabled: !!app,
    queryFn: ({ signal }) => fetchVacancy(app!.vacancy_id, signal),
  })
  const { stages } = useDefaultStages()
  const [stageId, setStageId] = useState('')
  const [reason, setReason] = useState('')

  const transitionMut = useMutation({
    mutationFn: () =>
      transitionApplication(applicationId, {
        to_stage_id: stageId,
        reason: reason || undefined,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['application', applicationId] })
      void queryClient.invalidateQueries({ queryKey: ['applications'] })
      setStageId('')
      setReason('')
    },
  })

  if (!app) return <p className="text-sm text-[var(--text-tertiary)]">Загрузка…</p>

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-2 text-sm">
        <div className="flex items-center justify-between">
          <span className="text-[var(--text-secondary)]">Кандидат</span>
          <span className="text-[var(--text-primary)]">
            {candidate
              ? `${candidate.last_name} ${candidate.first_name}`
              : app.candidate_id}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-[var(--text-secondary)]">Вакансия</span>
          <span className="text-[var(--text-primary)]">
            {vacancy?.title ?? app.vacancy_id}
          </span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-[var(--text-secondary)]">Статус</span>
          <StatusBadge status={app.status} />
        </div>
        <div className="flex items-center justify-between">
          <span className="text-[var(--text-secondary)]">Обновлено</span>
          <span>{app.updated_at ?? '—'}</span>
        </div>
      </div>

      <div className="border-t border-[var(--glass-border)] pt-3">
        <div className="mb-2 font-medium text-[var(--text-primary)]">
          Перевести по воронке
        </div>
        <div className="flex flex-col gap-2">
          <select
            value={stageId}
            onChange={(e) => setStageId(e.target.value)}
            className={fieldClass}
          >
            <option value="">— выберите стадию —</option>
            {stages.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
          <input
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Причина (необязательно)"
            className={fieldClass}
          />
          <button
            type="button"
            disabled={!stageId || transitionMut.isPending}
            onClick={() => transitionMut.mutate()}
            className="self-start rounded-pill bg-[var(--accent-blue)] px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            Перевести
          </button>
          {transitionMut.isError && (
            <p className="text-sm text-[var(--accent-red)]">Ошибка перехода</p>
          )}
        </div>
      </div>
    </div>
  )
}

function ScreeningTab({ applicationId }: { applicationId: string }) {
  const job = useAiJob<ScreeningResultOut>({
    runPath: `/api/v1/screening/applications/${applicationId}:run`,
    pollPath: `/api/v1/screening/applications/${applicationId}`,
  })
  return (
    <AIResultPanel
      title="Скрининг"
      description="Оценка кандидата по критериям вакансии"
      status={job.status}
      error={job.error}
      onRun={job.run}
    >
      {job.result && <ScreeningResultView result={job.result} />}
    </AIResultPanel>
  )
}

function RiskTab({ applicationId }: { applicationId: string }) {
  const job = useAiJob<RiskReportOut>({
    runPath: `/api/v1/risk/applications/${applicationId}:run`,
    pollPath: `/api/v1/risk/applications/${applicationId}`,
  })
  return (
    <AIResultPanel
      title="Анализ рисков"
      description="ИИ-анализ резюме на предмет рисков"
      status={job.status}
      error={job.error}
      onRun={job.run}
    >
      {job.result && <RiskReportView report={job.result} />}
    </AIResultPanel>
  )
}

export default function ApplicationDetailPage() {
  const params = useParams({ strict: false }) as { applicationId?: string }
  const applicationId = params.applicationId
  const navigate = useNavigate()
  const { data: app, isLoading } = useQuery({
    queryKey: ['application', applicationId],
    enabled: !!applicationId,
    queryFn: ({ signal }) => fetchApplication(applicationId as string, signal),
  })

  if (!applicationId) return null
  if (isLoading) return <p className="text-sm text-[var(--text-tertiary)]">Загрузка…</p>
  if (!app)
    return <p className="text-sm text-[var(--text-tertiary)]">Отклик не найден.</p>

  const tabs: DetailTab[] = [
    { value: 'timeline', label: 'Таймлайн', content: <TimelineTab applicationId={applicationId} /> },
    { value: 'screening', label: 'Скрининг', content: <ScreeningTab applicationId={applicationId} /> },
    { value: 'risk', label: 'Риски', content: <RiskTab applicationId={applicationId} /> },
  ]

  return (
    <div className="flex flex-col gap-3">
      <GlassTopBar
        title="Отклик"
        sticky={false}
        trailing={
          <button
            type="button"
            onClick={() => navigate({ to: '/applications' })}
            className="inline-flex items-center gap-1 rounded-pill border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 text-sm text-[var(--text-secondary)]"
          >
            <ArrowLeft size={16} /> К списку
          </button>
        }
      />
      <DetailLayout
        title={`Отклик ${app.candidate_id.slice(0, 8)}`}
        meta={
          <>
            <StatusBadge status={app.status} />
            <span>· {app.vacancy_id.slice(0, 8)}</span>
          </>
        }
        tabs={tabs}
      />
    </div>
  )
}
