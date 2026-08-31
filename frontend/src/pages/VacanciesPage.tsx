import { useMemo, useState } from 'react'
import { type ColumnDef } from '@tanstack/react-table'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Plus } from 'lucide-react'
import { GlassTopBar } from '@/shared/ui/GlassTopBar'
import { GlassSearchField } from '@/shared/ui/GlassSearchField'
import { GlassSheet } from '@/shared/ui/GlassSheet'
import { StatusBadge } from '@/shared/ui/StatusBadge'
import { RegistryTable } from '@/widgets/RegistryTable'
import { fetchVacancies } from '@/entities/vacancy/api'
import type { Vacancy } from '@/shared/api/types'

const createSchema = z.object({
  title: z.string().min(1, 'Введите название'),
  description: z.string().optional(),
})
type CreateValues = z.infer<typeof createSchema>

function AddVacancyForm({ onSubmitted }: { onSubmitted: () => void }) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateValues>({ resolver: zodResolver(createSchema) })

  const onSubmit = (values: CreateValues) => {
    // G4: POST /api/v1/vacancies
    console.log('create vacancy', values)
    onSubmitted()
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-3">
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium text-[var(--text-secondary)]">Название</span>
        <input
          {...register('title')}
          className="rounded-md border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 outline-none focus:ring-2 focus:ring-[var(--accent-blue)]/40"
        />
        {errors.title && (
          <span className="text-xs text-[var(--accent-red)]">
            {errors.title.message}
          </span>
        )}
      </label>
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium text-[var(--text-secondary)]">Описание</span>
        <textarea
          {...register('description')}
          rows={4}
          className="rounded-md border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 outline-none focus:ring-2 focus:ring-[var(--accent-blue)]/40"
        />
      </label>
      <button
        type="submit"
        className="self-start rounded-pill bg-[var(--accent-blue)] px-4 py-2 text-sm font-medium text-white"
      >
        Создать
      </button>
    </form>
  )
}

function VacancyDetail({ vacancy }: { vacancy: Vacancy }) {
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

export default function VacanciesPage() {
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState<Vacancy | null>(null)
  const [createOpen, setCreateOpen] = useState(false)

  const columns = useMemo<ColumnDef<Vacancy>[]>(
    () => [
      {
        id: 'title',
        accessorKey: 'title',
        header: 'Вакансия',
        size: 260,
        cell: ({ row }) => row.original.title,
      },
      {
        id: 'status',
        accessorKey: 'status',
        header: 'Статус',
        size: 130,
        cell: ({ row }) => <StatusBadge status={row.original.status} />,
      },
      {
        id: 'headcount',
        accessorKey: 'headcount',
        header: 'Фонд',
        size: 90,
        cell: ({ row }) => row.original.headcount,
      },
      {
        id: 'created_at',
        accessorKey: 'created_at',
        header: 'Создана',
        size: 180,
        cell: ({ row }) => row.original.created_at ?? '—',
      },
    ],
    [],
  )

  return (
    <div className="flex flex-col gap-3">
      <GlassTopBar
        title="Вакансии"
        sticky={false}
        trailing={
          <>
            <GlassSearchField
              value={search}
              onChange={setSearch}
              placeholder="Поиск вакансий"
            />
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
        fetchPage={fetchVacancies}
        queryKeyPrefix={['vacancies']}
        search={search}
        onRowClick={setSelected}
      />

      <GlassSheet
        open={selected !== null}
        onOpenChange={(open) => {
          if (!open) setSelected(null)
        }}
        title={selected?.title}
      >
        {selected && <VacancyDetail vacancy={selected} />}
      </GlassSheet>

      <GlassSheet
        open={createOpen}
        onOpenChange={setCreateOpen}
        title="Новая вакансия"
      >
        <AddVacancyForm onSubmitted={() => setCreateOpen(false)} />
      </GlassSheet>
    </div>
  )
}
