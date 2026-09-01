import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useParams } from '@tanstack/react-router'
import ReactECharts from 'echarts-for-react'
import type { EChartsOption } from 'echarts'
import { ArrowLeft } from 'lucide-react'
import { GlassTopBar } from '@/shared/ui/GlassTopBar'
import { StatusBadge } from '@/shared/ui/StatusBadge'
import { DetailLayout, type DetailTab } from '@/widgets/DetailLayout'
import { AIResultPanel } from '@/widgets/AIResultPanel'
import { useAiJob } from '@/shared/api/useAiJob'
import { KanbanBoard } from '@/widgets/KanbanBoard'
import { M4SearchMapPanel } from '@/widgets/M4SearchMapPanel'
import { fetchVacancy, updateVacancy } from '@/entities/vacancy/api'
import { fetchApplications, transitionApplication } from '@/entities/application/api'
import { useDefaultStages } from '@/entities/funnel/api'
import { fetchFunnel } from '@/entities/analytics/api'
import { buttonPrimaryClass, fieldClass, fieldLabelClass } from '@/shared/ui/field'
import type { Criterion, RequirementSetOut, Vacancy } from '@/shared/api/types'

const STATUS_LABEL: Record<string, string> = {
  new: 'Новый',
  in_progress: 'В работе',
  hired: 'Нанят',
  rejected: 'Отказ',
  withdrawn: 'Отозван',
}
const STATUS_ORDER = ['new', 'in_progress', 'hired', 'rejected', 'withdrawn']

function DescriptionTab({ vacancy }: { vacancy: Vacancy }) {
  return (
    <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
      <dt className="text-[var(--text-secondary)]">Статус</dt>
      <dd><StatusBadge status={vacancy.status} /></dd>
      <dt className="text-[var(--text-secondary)]">Фонд</dt>
      <dd>{vacancy.headcount}</dd>
      <dt className="text-[var(--text-secondary)]">Описание</dt>
      <dd className="col-span-2 whitespace-pre-wrap text-[var(--text-primary)]">
        {vacancy.description || '—'}
      </dd>
      <dt className="text-[var(--text-secondary)]">Создана</dt>
      <dd>{vacancy.created_at ?? '—'}</dd>
    </dl>
  )
}

function CriteriaTab({ vacancyId }: { vacancyId: string }) {
  const job = useAiJob<RequirementSetOut>({
    runPath: `/api/v1/screening/vacancies/${vacancyId}/requirements:generate`,
    pollPath: `/api/v1/screening/vacancies/${vacancyId}/requirements`,
  })
  return (
    <AIResultPanel
      title="Критерии отбора"
      description="ИИ-генерация критериев для этой вакансии"
      status={job.status}
      error={job.error}
      onRun={job.run}
    >
      {job.result && (
        <ul className="flex flex-col gap-2">
          {job.result.requirements.map((c: Criterion, i: number) => (
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
                <p className="mt-1 text-xs text-[var(--text-secondary)]">
                  {c.description}
                </p>
              )}
            </li>
          ))}
        </ul>
      )}
    </AIResultPanel>
  )
}

function FunnelTab({ vacancyId }: { vacancyId: string }) {
  const queryClient = useQueryClient()
  const { stages } = useDefaultStages()
  const { data, isLoading } = useQuery({
    queryKey: ['applications', 'vacancy', vacancyId],
    queryFn: ({ signal }) => fetchApplications({ vacancyId, signal }),
  })
  const transitionMut = useMutation({
    mutationFn: (args: { appId: string; stageId: string }) =>
      transitionApplication(args.appId, { to_stage_id: args.stageId }),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ['applications', 'vacancy', vacancyId] }),
  })

  if (isLoading) return <p className="text-sm text-[var(--text-tertiary)]">Загрузка…</p>
  if (stages.length === 0)
    return (
      <p className="text-sm text-[var(--text-tertiary)]">
        Нет стадий воронки — создайте пресет воронки.
      </p>
    )

  return (
    <KanbanBoard
      stages={stages}
      applications={data?.items ?? []}
      onTransition={(appId, stageId) => transitionMut.mutate({ appId, stageId })}
    />
  )
}

function AnalyticsTab({ vacancyId }: { vacancyId: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['analytics-funnel', vacancyId],
    queryFn: ({ signal }) => fetchFunnel(vacancyId, signal),
  })
  if (isLoading) return <p className="text-sm text-[var(--text-tertiary)]">Загрузка…</p>
  if (!data || data.total === 0)
    return <p className="text-sm text-[var(--text-tertiary)]">Нет откликов.</p>

  const option: EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: STATUS_ORDER.map((s) => STATUS_LABEL[s] ?? s) },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        type: 'bar',
        data: STATUS_ORDER.map((s) => data.by_status[s] ?? 0),
        itemStyle: { color: 'var(--accent-blue)' },
      },
    ],
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-md border border-[var(--glass-border)] bg-[var(--surface-solid)] p-3 shadow-card">
          <div className="text-xs text-[var(--text-tertiary)]">Всего</div>
          <div className="text-xl font-semibold">{data.total}</div>
        </div>
        <div className="rounded-md border border-[var(--glass-border)] bg-[var(--surface-solid)] p-3 shadow-card">
          <div className="text-xs text-[var(--text-tertiary)]">Найм</div>
          <div className="text-xl font-semibold">{Math.round(data.hired_rate * 100)}%</div>
        </div>
        <div className="rounded-md border border-[var(--glass-border)] bg-[var(--surface-solid)] p-3 shadow-card">
          <div className="text-xs text-[var(--text-tertiary)]">Отказ</div>
          <div className="text-xl font-semibold">{Math.round(data.reject_rate * 100)}%</div>
        </div>
      </div>
      <ReactECharts option={option} style={{ height: 280 }} />
    </div>
  )
}

function SettingsTab({ vacancy }: { vacancy: Vacancy }) {
  const queryClient = useQueryClient()
  const [title, setTitle] = useState(vacancy.title)
  const [description, setDescription] = useState(vacancy.description ?? '')
  const [status, setStatus] = useState(vacancy.status)
  const [headcount, setHeadcount] = useState(String(vacancy.headcount))
  const [saved, setSaved] = useState(false)

  const mut = useMutation({
    mutationFn: () =>
      updateVacancy(vacancy.id, {
        title,
        description: description || undefined,
        status,
        headcount: Number(headcount) || 1,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['vacancy', vacancy.id] })
      setSaved(true)
    },
  })

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        mut.mutate()
      }}
      className="flex max-w-md flex-col gap-3"
    >
      <label className="flex flex-col gap-1">
        <span className={fieldLabelClass}>Название</span>
        <input value={title} onChange={(e) => setTitle(e.target.value)} className={fieldClass} />
      </label>
      <label className="flex flex-col gap-1">
        <span className={fieldLabelClass}>Описание</span>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          className={fieldClass}
        />
      </label>
      <div className="grid grid-cols-2 gap-3">
        <label className="flex flex-col gap-1">
          <span className={fieldLabelClass}>Статус</span>
          <select value={status} onChange={(e) => setStatus(e.target.value)} className={fieldClass}>
            {['draft', 'open', 'paused', 'closed', 'on_hold'].map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1">
          <span className={fieldLabelClass}>Фонд</span>
          <input
            type="number"
            value={headcount}
            onChange={(e) => setHeadcount(e.target.value)}
            className={fieldClass}
          />
        </label>
      </div>
      <button type="submit" disabled={mut.isPending} className={buttonPrimaryClass}>
        Сохранить
      </button>
      {saved && <p className="text-sm text-[var(--accent-green)]">Сохранено</p>}
      {mut.isError && <p className="text-sm text-[var(--accent-red)]">Ошибка сохранения</p>}
    </form>
  )
}

export default function VacancyDetailPage() {
  const params = useParams({ strict: false }) as { vacancyId?: string }
  const vacancyId = params.vacancyId
  const navigate = useNavigate()
  const { data: vacancy, isLoading } = useQuery({
    queryKey: ['vacancy', vacancyId],
    enabled: !!vacancyId,
    queryFn: ({ signal }) => fetchVacancy(vacancyId as string, signal),
  })

  if (!vacancyId) return null
  if (isLoading) return <p className="text-sm text-[var(--text-tertiary)]">Загрузка…</p>
  if (!vacancy) return <p className="text-sm text-[var(--text-tertiary)]">Вакансия не найдена.</p>

  const tabs: DetailTab[] = [
    { value: 'description', label: 'Описание', content: <DescriptionTab vacancy={vacancy} /> },
    { value: 'criteria', label: 'Критерии', content: <CriteriaTab vacancyId={vacancyId} /> },
    { value: 'funnel', label: 'Воронка', content: <FunnelTab vacancyId={vacancyId} /> },
    { value: 'searchmap', label: 'Карта поиска', content: <M4SearchMapPanel vacancyId={vacancyId} /> },
    { value: 'analytics', label: 'Аналитика', content: <AnalyticsTab vacancyId={vacancyId} /> },
    { value: 'settings', label: 'Настройки', content: <SettingsTab vacancy={vacancy} /> },
  ]

  return (
    <div className="flex flex-col gap-3">
      <GlassTopBar
        title="Вакансия"
        sticky={false}
        trailing={
          <button
            type="button"
            onClick={() => navigate({ to: '/vacancies' })}
            className="inline-flex items-center gap-1 rounded-pill border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 text-sm text-[var(--text-secondary)]"
          >
            <ArrowLeft size={16} /> К списку
          </button>
        }
      />
      <DetailLayout
        title={vacancy.title}
        meta={
          <>
            <StatusBadge status={vacancy.status} />
            <span>· Фонд {vacancy.headcount}</span>
          </>
        }
        tabs={tabs}
      />
    </div>
  )
}
