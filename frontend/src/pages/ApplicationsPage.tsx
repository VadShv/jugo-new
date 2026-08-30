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
import type { Application, Stage } from '@/shared/api/types'

const STAGE_OPTIONS: { value: Stage | 'all'; label: string }[] = [
  { value: 'all', label: 'Все этапы' },
  { value: 'new', label: 'Новый' },
  { value: 'screening', label: 'Скрининг' },
  { value: 'interview', label: 'Интервью' },
  { value: 'offer', label: 'Оффер' },
  { value: 'rejected', label: 'Отказ' },
]

function StageFilter({
  value,
  onChange,
}: {
  value: string
  onChange: (value: string) => void
}) {
  return (
    <Select.Root value={value} onValueChange={onChange}>
      <Select.Trigger className="inline-flex items-center gap-1 rounded-pill border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 text-sm text-[var(--text-secondary)] outline-none">
        <Select.Value placeholder="Все этапы" />
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
            {STAGE_OPTIONS.map((option) => (
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
        <span className="text-[var(--text-secondary)]">Этап</span>
        <StatusBadge stage={application.stage} />
      </div>
      <div className="flex items-center justify-between">
        <span className="text-[var(--text-secondary)]">Кандидат</span>
        <span>{application.candidate_name ?? application.candidate_id}</span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-[var(--text-secondary)]">Вакансия</span>
        <span>{application.vacancy_title ?? application.vacancy_id}</span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-[var(--text-secondary)]">Обновлено</span>
        <span>{application.updated_at ?? '—'}</span>
      </div>
    </div>
  )
}

export default function ApplicationsPage() {
  const [search, setSearch] = useState('')
  const [stageFilter, setStageFilter] = useState('all')
  const [selected, setSelected] = useState<Application | null>(null)

  const columns = useMemo<ColumnDef<Application>[]>(
    () => [
      {
        id: 'candidate_name',
        accessorKey: 'candidate_name',
        header: 'Кандидат',
        size: 200,
        cell: ({ row }) => row.original.candidate_name ?? '—',
      },
      {
        id: 'vacancy_title',
        accessorKey: 'vacancy_title',
        header: 'Вакансия',
        size: 200,
        cell: ({ row }) => row.original.vacancy_title ?? '—',
      },
      {
        id: 'stage',
        accessorKey: 'stage',
        header: 'Этап',
        size: 120,
        cell: ({ row }) => <StatusBadge stage={row.original.stage} />,
      },
      {
        id: 'updated_at',
        accessorKey: 'updated_at',
        header: 'Обновлено',
        size: 140,
        cell: ({ row }) => row.original.updated_at ?? '—',
      },
    ],
    [],
  )

  const renderHeader = (items: Application[]): ReactNode => {
    const counts: Record<Stage, number> = {
      new: 0,
      screening: 0,
      interview: 0,
      offer: 0,
      rejected: 0,
    }
    for (const item of items) counts[item.stage] += 1
    const stages: PipelineStage[] = [
      { id: 'new', label: 'Новый', count: counts.new, accent: 'var(--accent-blue)' },
      { id: 'screening', label: 'Скрининг', count: counts.screening, accent: 'var(--accent-orange)' },
      { id: 'interview', label: 'Интервью', count: counts.interview, accent: 'var(--accent-purple)' },
      { id: 'offer', label: 'Оффер', count: counts.offer, accent: 'var(--accent-green)' },
      { id: 'rejected', label: 'Отказ', count: counts.rejected, accent: 'var(--accent-red)' },
    ]
    return <PipelineStageBar stages={stages} />
  }

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
            <StageFilter value={stageFilter} onChange={setStageFilter} />
          </>
        }
      />

      <RegistryTable
        columns={columns}
        fetchPage={fetchApplications}
        queryKeyPrefix={['applications']}
        search={search}
        onRowClick={setSelected}
        renderHeader={renderHeader}
      />

      <GlassSheet
        open={selected !== null}
        onOpenChange={(open) => {
          if (!open) setSelected(null)
        }}
        title={selected?.candidate_name ?? 'Отклик'}
      >
        {selected && <ApplicationDetail application={selected} />}
      </GlassSheet>
    </div>
  )
}
