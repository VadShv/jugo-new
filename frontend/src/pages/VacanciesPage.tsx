import { useMemo, useState } from 'react'
import { type ColumnDef } from '@tanstack/react-table'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Plus } from 'lucide-react'
import { GlassTopBar } from '@/shared/ui/GlassTopBar'
import { GlassSearchField } from '@/shared/ui/GlassSearchField'
import { GlassSheet } from '@/shared/ui/GlassSheet'
import { RegistryTable } from '@/widgets/RegistryTable'
import { fetchVacancies } from '@/entities/vacancy/api'
import type { Vacancy } from '@/shared/api/types'

const createSchema = z.object({
  title: z.string().min(1, 'Введите название'),
  department: z.string().optional(),
})
type CreateValues = z.infer<typeof createSchema>

function AddVacancyForm({ onSubmitted }: { onSubmitted: () => void }) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateValues>({ resolver: zodResolver(createSchema) })

  const onSubmit = (values: CreateValues) => {
    console.log('create vacancy', values)
    onSubmitted()
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="flex flex-col gap-3"
    >
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium text-[var(--text-secondary)]">
          Название
        </span>
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
        <span className="font-medium text-[var(--text-secondary)]">
          Подразделение
        </span>
        <input
          {...register('department')}
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
      <dt className="text-[var(--text-secondary)]">Подразделение</dt>
      <dd>{vacancy.department ?? '—'}</dd>
      <dt className="text-[var(--text-secondary)]">Статус</dt>
      <dd>{vacancy.status ?? '—'}</dd>
      <dt className="text-[var(--text-secondary)]">Локация</dt>
      <dd>{vacancy.location ?? '—'}</dd>
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
        size: 240,
        cell: ({ row }) => row.original.title,
      },
      {
        id: 'department',
        accessorKey: 'department',
        header: 'Подразделение',
        size: 180,
        cell: ({ row }) => row.original.department ?? '—',
      },
      {
        id: 'status',
        accessorKey: 'status',
        header: 'Статус',
        size: 120,
        cell: ({ row }) => row.original.status ?? '—',
      },
      {
        id: 'location',
        accessorKey: 'location',
        header: 'Локация',
        size: 140,
        cell: ({ row }) => row.original.location ?? '—',
      },
      {
        id: 'created_at',
        accessorKey: 'created_at',
        header: 'Создана',
        size: 140,
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
