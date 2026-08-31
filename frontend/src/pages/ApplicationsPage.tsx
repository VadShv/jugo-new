import { useMemo, useState, type ReactNode } from 'react'
import { type ColumnDef } from '@tanstack/react-table'
import * as Select from '@radix-ui/react-select'
import { ChevronDown } from 'lucide-react'
import { GlassTopBar } from '@/shared/ui/GlassTopBar'
import { GlassSearchField } from '@/shared/ui/GlassSearchField'
import { GlassSheet } from '@/shared/ui/GlassSheet'
import { StatusBadge } from '@/shared/ui/StatusBadge'
import { PipelineStageBar, type PipelineStage } from '@/shared/ui/PipelineStageBar'
import { RegistryTable } from '@/widgets/RegistryTable'
import { fetchApplications } from '@/entities/application/api'
import type { Application } from '@/shared/api/types'

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
        <Select.Icon>
          <ChevronDown size={14} />
        </Select.Icon>
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

function ApplicationDetail({ application }: { application: Application }) {
  return (
    <div className="flex flex-col gap-3 text-sm">
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
  )
}

export default function ApplicationsPage() {
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [selected, setSelected] = useState<Application | null>(null)

  const columns = useMemo<ColumnDef<Application>[]>(
    () => [
      {
        id: 'candidate_id',
        accessorKey: 'candidate_id',
        header: 'Кандидат',
        size: 140,
        cell: ({ row }) => (
          <span className="font-mono text-xs">{shortId(row.original.candidate_id)}</span>
        ),
      },
      {
        id: 'vacancy_id',
        accessorKey: 'vacancy_id',
        header: 'Вакансия',
        size: 140,
        cell: ({ row }) => (
          <span className="font-mono text-xs">{shortId(row.original.vacancy_id)}</span>
        ),
      },
      {
        id: 'status',
        accessorKey: 'status',
        header: 'Статус',
        size: 130,
        cell: ({ row }) => <StatusBadge status={row.original.status} />,
      },
      {
        id: 'updated_at',
        accessorKey: 'updated_at',
        header: 'Обновлено',
        size: 180,
        cell: ({ row }) => row.original.updated_at ?? '—',
      },
    ],
    [],
  )

  const renderHeader = (items: Application[]): ReactNode => {
    const counts: Record<string, number> = {}
    for (const item of items) counts[item.status] = (counts[item.status] ?? 0) + 1
    const stages: PipelineStage[] = STATUS_OPTIONS.filter((o) => o.value !== 'all').map(
      (o) => ({
        id: o.value,
        label: o.label,
        count: counts[o.value] ?? 0,
        accent: o.accent,
      }),
    )
    return <PipelineStageBar stages={stages} />
  }

  const fetchPage = (args: {
    cursor?: string
    search?: string
    signal?: AbortSignal
  }) =>
    fetchApplications({
      ...args,
      status: statusFilter === 'all' ? undefined : statusFilter,
    })

  return (
    <div className="flex flex-col gap-3">
      <GlassTopBar
        title="Отклики"
        sticky={false}
        trailing={
          <>
            <GlassSearchField
              value={search}
              onChange={setSearch}
              placeholder="Поиск откликов"
            />
            <StatusFilter value={statusFilter} onChange={setStatusFilter} />
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
        onOpenChange={(open) => {
          if (!open) setSelected(null)
        }}
        title="Отклик"
      >
        {selected && <ApplicationDetail application={selected} />}
      </GlassSheet>
    </div>
  )
}
