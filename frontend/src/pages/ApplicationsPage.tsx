import { useMemo, useState, type FormEvent, type ReactNode } from 'react'
import { type ColumnDef } from '@tanstack/react-table'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as Select from '@radix-ui/react-select'
import { ChevronDown, Plus } from 'lucide-react'
import { GlassTopBar } from '@/shared/ui/GlassTopBar'
import { GlassSearchField } from '@/shared/ui/GlassSearchField'
import { GlassSheet } from '@/shared/ui/GlassSheet'
import { StatusBadge } from '@/shared/ui/StatusBadge'
import { PipelineStageBar, type PipelineStage } from '@/shared/ui/PipelineStageBar'
import { RegistryTable } from '@/widgets/RegistryTable'
import {
  createApplication,
  fetchApplications,
  searchApplications,
  transitionApplication,
} from '@/entities/application/api'
import { fetchCandidates } from '@/entities/candidate/api'
import { fetchVacancies } from '@/entities/vacancy/api'
import { useDefaultStages } from '@/entities/funnel/api'
import { ApiError } from '@/shared/api/client'
import type { Application, Candidate, Vacancy } from '@/shared/api/types'

const STATUS_OPTIONS: { value: string; label: string; accent: string }[] = [
  { value: 'all', label: 'Все статусы', accent: 'var(--accent-blue)' },
  { value: 'new', label: 'Новый', accent: 'var(--accent-blue)' },
  { value: 'in_progress', label: 'В работе', accent: 'var(--accent-purple)' },
  { value: 'hired', label: 'Нанят', accent: 'var(--accent-green)' },
  { value: 'rejected', label: 'Отказ', accent: 'var(--accent-red)' },
  { value: 'withdrawn', label: 'Отозван', accent: 'var(--text-tertiary)' },
]

function shortId(id: string): string {
  return id.length > 8 ? `${id.slice(0, 8)}…` : id
}

function StatusFilter({
  value,
  onChange,
}: {
  value: string
  onChange: (value: string) => void
}) {
  return (
    <Select.Root value={value} onValueChange={onChange}>
      <Select.Trigger className="inline-flex items-center gap-1 rounded-pill border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 text-sm text-[var(--text-secondary)] outline-none">
        <Select.Value placeholder="Все статусы" />
        <Select.Icon><ChevronDown size={14} /></Select.Icon>
      </Select.Trigger>
      <Select.Portal>
        <Select.Content
          position="popper"
          sideOffset={4}
          className="glass glass--regular z-50 rounded-md p-1"
        >
          <Select.Viewport>
            {STATUS_OPTIONS.map((option) => (
              <Select.Item
                key={option.value}
                value={option.value}
                className="relative cursor-pointer rounded-sm px-2 py-1 text-sm text-[var(--text-primary)] outline-none data-[highlighted]:bg-[var(--surface-sunken)]"
              >
                <Select.ItemText>{option.label}</Select.ItemText>
              </Select.Item>
            ))}
          </Select.Viewport>
        </Select.Content>
      </Select.Portal>
    </Select.Root>
  )
}

const selectClass =
  'rounded-md border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[var(--accent-blue)]/40'

function useSelectData() {
  const candidates = useQuery({
    queryKey: ['candidates-select'],
    queryFn: ({ signal }) => fetchCandidates({ signal }),
  })
  const vacancies = useQuery({
    queryKey: ['vacancies-select'],
    queryFn: ({ signal }) => fetchVacancies({ signal }),
  })
  return { candidates: candidates.data?.items ?? [], vacancies: vacancies.data?.items ?? [] }
}

function AddApplicationForm({ onSubmitted }: { onSubmitted: () => void }) {
  const queryClient = useQueryClient()
  const { candidates, vacancies } = useSelectData()
  const { stages } = useDefaultStages()
  const [candidateId, setCandidateId] = useState('')
  const [vacancyId, setVacancyId] = useState('')
  const [stageId, setStageId] = useState('')
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: () =>
      createApplication({
        candidate_id: candidateId,
        vacancy_id: vacancyId,
        current_stage_id: stageId || undefined,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['applications'] })
      onSubmitted()
    },
    onError: (e) =>
      setError(e instanceof ApiError ? e.problem?.detail ?? e.message : 'Ошибка'),
  })

  const onSubmit = (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    if (!candidateId || !vacancyId) {
      setError('Выберите кандидата и вакансию')
      return
    }
    mutation.mutate()
  }

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-3">
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium text-[var(--text-secondary)]">Кандидат</span>
        <select value={candidateId} onChange={(e) => setCandidateId(e.target.value)} className={selectClass}>
          <option value="">— выберите —</option>
          {candidates.map((c: Candidate) => (
            <option key={c.id} value={c.id}>
              {c.last_name} {c.first_name}{c.headline ? ` — ${c.headline}` : ''}
            </option>
          ))}
        </select>
      </label>
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium text-[var(--text-secondary)]">Вакансия</span>
        <select value={vacancyId} onChange={(e) => setVacancyId(e.target.value)} className={selectClass}>
          <option value="">— выберите —</option>
          {vacancies.map((v: Vacancy) => (
            <option key={v.id} value={v.id}>{v.title}</option>
          ))}
        </select>
      </label>
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium text-[var(--text-secondary)]">Стадия</span>
        <select value={stageId} onChange={(e) => setStageId(e.target.value)} className={selectClass}>
          <option value="">— без стадии —</option>
          {stages.map((s) => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </select>
      </label>
      <button
        type="submit"
        disabled={mutation.isPending}
        className="self-start rounded-pill bg-[var(--accent-blue)] px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
      >
        Создать отклик
      </button>
      {error && <p className="text-sm text-[var(--accent-red)]">{error}</p>}
    </form>
  )
}

function ApplicationDetail({
  application,
  onTransitioned,
}: {
  application: Application
  onTransitioned: (status: string, stageId: string) => void
}) {
  const queryClient = useQueryClient()
  const { stages } = useDefaultStages()
  const [stageId, setStageId] = useState('')
  const [reason, setReason] = useState('')
  const [error, setError] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: () =>
      transitionApplication(application.id, {
        to_stage_id: stageId,
        reason: reason || undefined,
      }),
    onSuccess: (res) => {
      void queryClient.invalidateQueries({ queryKey: ['applications'] })
      onTransitioned(res.status, res.to_stage_id)
      setStageId('')
      setReason('')
    },
    onError: (e) =>
      setError(e instanceof ApiError ? e.problem?.detail ?? e.message : 'Ошибка'),
  })

  return (
    <div className="flex flex-col gap-4 text-sm">
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <span className="text-[var(--text-secondary)]">Статус</span>
          <StatusBadge status={application.status} />
        </div>
        <div className="flex items-center justify-between">
          <span className="text-[var(--text-secondary)]">Кандидат</span>
          <span className="font-mono text-xs">{application.candidate_id}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-[var(--text-secondary)]">Вакансия</span>
          <span className="font-mono text-xs">{application.vacancy_id}</span>
        </div>
        {application.screening_score != null && (
          <div className="flex items-center justify-between">
            <span className="text-[var(--text-secondary)]">Скрининг</span>
            <span>{Math.round(application.screening_score * 100)}%</span>
          </div>
        )}
        {application.risk_level && (
          <div className="flex items-center justify-between">
            <span className="text-[var(--text-secondary)]">Риск</span>
            <StatusBadge status={application.risk_level} />
          </div>
        )}
        <div className="flex items-center justify-between">
          <span className="text-[var(--text-secondary)]">Обновлено</span>
          <span>{application.updated_at ?? '—'}</span>
        </div>
      </div>

      <div className="border-t border-[var(--glass-border)] pt-3">
        <div className="mb-2 font-medium text-[var(--text-primary)]">Перевести по воронке</div>
        <div className="flex flex-col gap-2">
          <select value={stageId} onChange={(e) => setStageId(e.target.value)} className={selectClass}>
            <option value="">— выберите стадию —</option>
            {stages.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
          <input
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Причина (необязательно)"
            className={selectClass}
          />
          <button
            type="button"
            disabled={!stageId || mutation.isPending}
            onClick={() => { setError(null); mutation.mutate() }}
            className="self-start rounded-pill bg-[var(--accent-blue)] px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            Перевести
          </button>
          {error && <p className="text-sm text-[var(--accent-red)]">{error}</p>}
        </div>
      </div>
    </div>
  )
}

export default function ApplicationsPage() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [selected, setSelected] = useState<Application | null>(null)
  const [createOpen, setCreateOpen] = useState(false)

  const columns = useMemo<ColumnDef<Application>[]>(
    () => [
      { id: 'candidate_id', accessorKey: 'candidate_id', header: 'Кандидат', size: 140, cell: ({ row }) => <span className="font-mono text-xs">{shortId(row.original.candidate_id)}</span> },
      { id: 'vacancy_id', accessorKey: 'vacancy_id', header: 'Вакансия', size: 140, cell: ({ row }) => <span className="font-mono text-xs">{shortId(row.original.vacancy_id)}</span> },
      { id: 'status', accessorKey: 'status', header: 'Статус', size: 130, cell: ({ row }) => <StatusBadge status={row.original.status} /> },
      { id: 'updated_at', accessorKey: 'updated_at', header: 'Обновлено', size: 180, cell: ({ row }) => row.original.updated_at ?? '—' },
    ],
    [],
  )

  const renderHeader = (items: Application[]): ReactNode => {
    const counts: Record<string, number> = {}
    for (const item of items) counts[item.status] = (counts[item.status] ?? 0) + 1
    const stages: PipelineStage[] = STATUS_OPTIONS.filter((o) => o.value !== 'all').map(
      (o) => ({ id: o.value, label: o.label, count: counts[o.value] ?? 0, accent: o.accent }),
    )
    return <PipelineStageBar stages={stages} />
  }

  const fetchPage = (args: { cursor?: string; search?: string; signal?: AbortSignal }) =>
    args.search
      ? searchApplications({
          q: args.search,
          cursor: args.cursor,
          signal: args.signal,
          filters: statusFilter !== 'all' ? { status: statusFilter } : {},
        })
      : fetchApplications({
          cursor: args.cursor,
          signal: args.signal,
          status: statusFilter === 'all' ? undefined : statusFilter,
        })

  return (
    <div className="flex flex-col gap-3">
      <GlassTopBar
        title="Отклики"
        sticky={false}
        trailing={
          <>
            <GlassSearchField value={search} onChange={setSearch} placeholder="Поиск откликов" />
            <StatusFilter value={statusFilter} onChange={setStatusFilter} />
            <button
              type="button"
              onClick={() => setCreateOpen(true)}
              className="inline-flex items-center gap-1 rounded-pill bg-[var(--accent-blue)] px-3 py-2 text-sm font-medium text-white"
            >
              <Plus size={16} /> Создать
            </button>
          </>
        }
      />

      <RegistryTable
        columns={columns}
        fetchPage={fetchPage}
        queryKeyPrefix={['applications', statusFilter]}
        search={search}
        onRowClick={setSelected}
        renderHeader={renderHeader}
      />

      <GlassSheet
        open={selected !== null}
        onOpenChange={(open) => { if (!open) setSelected(null) }}
        title="Отклик"
      >
        {selected && (
          <ApplicationDetail
            application={selected}
            onTransitioned={(status, stageId) =>
              setSelected({ ...selected, status, current_stage_id: stageId })
            }
          />
        )}
      </GlassSheet>

      <GlassSheet open={createOpen} onOpenChange={setCreateOpen} title="Новый отклик">
        <AddApplicationForm onSubmitted={() => setCreateOpen(false)} />
      </GlassSheet>
    </div>
  )
}
