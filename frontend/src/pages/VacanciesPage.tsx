import { useMemo, useState } from 'react'
import { type ColumnDef } from '@tanstack/react-table'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import { GlassTopBar } from '@/shared/ui/GlassTopBar'
import { GlassSearchField } from '@/shared/ui/GlassSearchField'
import { GlassSheet } from '@/shared/ui/GlassSheet'
import { StatusBadge } from '@/shared/ui/StatusBadge'
import { RegistryTable } from '@/widgets/RegistryTable'
import {
  createVacancy,
  fetchVacancies,
  searchVacancies,
} from '@/entities/vacancy/api'
import { ApiError } from '@/shared/api/client'
import type { Vacancy } from '@/shared/api/types'

const createSchema = z.object({
  title: z.string().min(1, 'Введите название'),
  description: z.string().optional(),
})
type CreateValues = z.infer<typeof createSchema>

function AddVacancyForm({ onSubmitted }: { onSubmitted: () => void }) {
  const queryClient = useQueryClient()
  const [error, setError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateValues>({ resolver: zodResolver(createSchema) })

  const mutation = useMutation({
    mutationFn: (values: CreateValues) =>
      createVacancy({ title: values.title, description: values.description }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['vacancies'] })
      onSubmitted()
    },
    onError: (e) =>
      setError(e instanceof ApiError ? e.problem?.detail ?? e.message : 'Ошибка'),
  })

  const onSubmit = (values: CreateValues) => {
    setError(null)
    mutation.mutate(values)
  }

  const inputClass =
    'rounded-md border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 outline-none focus:ring-2 focus:ring-[var(--accent-blue)]/40'

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-3">
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium text-[var(--text-secondary)]">Название</span>
        <input {...register('title')} className={inputClass} />
        {errors.title && (
          <span className="text-xs text-[var(--accent-red)]">
            {errors.title.message}
          </span>
        )}
      </label>
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium text-[var(--text-secondary)]">Описание</span>
        <textarea {...register('description')} rows={4} className={inputClass} />
      </label>
      <button
        type="submit"
        disabled={isSubmitting}
        className="self-start rounded-pill bg-[var(--accent-blue)] px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
      >
        Создать
      </button>
      {error && <p className="text-sm text-[var(--accent-red)]">{error}</p>}
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
      { id: 'title', accessorKey: 'title', header: 'Вакансия', size: 260, cell: ({ row }) => row.original.title },
      { id: 'status', accessorKey: 'status', header: 'Статус', size: 130, cell: ({ row }) => <StatusBadge status={row.original.status} /> },
      { id: 'headcount', accessorKey: 'headcount', header: 'Фонд', size: 90, cell: ({ row }) => row.original.headcount },
      { id: 'created_at', accessorKey: 'created_at', header: 'Создана', size: 180, cell: ({ row }) => row.original.created_at ?? '—' },
    ],
    [],
  )

  const fetchPage = (args: { cursor?: string; search?: string; signal?: AbortSignal }) =>
    args.search
      ? searchVacancies({ q: args.search, cursor: args.cursor, signal: args.signal })
      : fetchVacancies(args)

  return (
    <div className="flex flex-col gap-3">
      <GlassTopBar
        title="Вакансии"
        sticky={false}
        trailing={
          <>
            <GlassSearchField value={search} onChange={setSearch} placeholder="Поиск вакансий" />
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
        queryKeyPrefix={['vacancies']}
        search={search}
        onRowClick={setSelected}
      />

      <GlassSheet
        open={selected !== null}
        onOpenChange={(open) => { if (!open) setSelected(null) }}
        title={selected?.title}
      >
        {selected && <VacancyDetail vacancy={selected} />}
      </GlassSheet>

      <GlassSheet open={createOpen} onOpenChange={setCreateOpen} title="Новая вакансия">
        <AddVacancyForm onSubmitted={() => setCreateOpen(false)} />
      </GlassSheet>
    </div>
  )
}
