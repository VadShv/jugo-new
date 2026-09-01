import { useMemo, useState } from 'react'
import { type ColumnDef } from '@tanstack/react-table'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import { ChevronRight, Plus } from 'lucide-react'
import { GlassTopBar } from '@/shared/ui/GlassTopBar'
import { GlassSearchField } from '@/shared/ui/GlassSearchField'
import { GlassSheet } from '@/shared/ui/GlassSheet'
import { StatusBadge } from '@/shared/ui/StatusBadge'
import { RegistryTable } from '@/widgets/RegistryTable'
import { useToast } from '@/widgets/Toaster'
import { useUiStore } from '@/app/store'
import {
  createVacancy,
  fetchVacancies,
  searchVacancies,
} from '@/entities/vacancy/api'
import { buttonPrimaryClass, fieldClass, fieldErrorClass, fieldLabelClass } from '@/shared/ui/field'
import { ApiError } from '@/shared/api/client'
import type { Vacancy } from '@/shared/api/types'

const createSchema = z.object({
  title: z.string().min(1, 'Введите название'),
  description: z.string().optional(),
})
type CreateValues = z.infer<typeof createSchema>

function AddVacancyForm({ onSubmitted }: { onSubmitted: () => void }) {
  const queryClient = useQueryClient()
  const { toast } = useToast()
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
      toast('success', 'Вакансия создана')
      onSubmitted()
    },
    onError: (e) => {
      const msg = e instanceof ApiError ? e.problem?.detail ?? e.message : 'Ошибка'
      setError(msg)
      toast('error', 'Ошибка создания', msg)
    },
  })

  const onSubmit = (values: CreateValues) => {
    setError(null)
    mutation.mutate(values)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-3">
      <label className="flex flex-col gap-1">
        <span className={fieldLabelClass}>Название</span>
        <input {...register('title')} className={fieldClass} />
        {errors.title && <span className={fieldErrorClass}>{errors.title.message}</span>}
      </label>
      <label className="flex flex-col gap-1">
        <span className={fieldLabelClass}>Описание</span>
        <textarea {...register('description')} rows={4} className={fieldClass} />
      </label>
      <button type="submit" disabled={isSubmitting} className={buttonPrimaryClass}>
        Создать
      </button>
      {error && <p className="text-sm text-[var(--accent-red)]">{error}</p>}
    </form>
  )
}

export default function VacanciesPage() {
  const [search, setSearch] = useState('')
  const [createOpen, setCreateOpen] = useState(false)
  const navigate = useNavigate()
  const setSelectedVacancy = useUiStore((s) => s.setSelectedVacancy)

  const columns = useMemo<ColumnDef<Vacancy>[]>(
    () => [
      { id: 'title', accessorKey: 'title', header: 'Вакансия', size: 260, cell: ({ row }) => row.original.title },
      { id: 'status', accessorKey: 'status', header: 'Статус', size: 130, cell: ({ row }) => <StatusBadge status={row.original.status} /> },
      { id: 'headcount', accessorKey: 'headcount', header: 'Фонд', size: 90, cell: ({ row }) => row.original.headcount },
      { id: 'created_at', accessorKey: 'created_at', header: 'Создана', size: 180, cell: ({ row }) => row.original.created_at ?? '—' },
      {
        id: 'detail',
        header: '',
        size: 50,
        cell: ({ row }) => (
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation()
              navigate({ to: '/vacancies/$vacancyId', params: { vacancyId: row.original.id } })
            }}
            className="text-[var(--text-tertiary)] hover:text-[var(--text-primary)]"
          >
            <ChevronRight size={16} />
          </button>
        ),
      },
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
        onRowClick={(v) => {
          setSelectedVacancy(v.id, v.title)
          navigate({ to: '/applications' })
        }}
      />

      <GlassSheet open={createOpen} onOpenChange={setCreateOpen} title="Новая вакансия">
        <AddVacancyForm onSubmitted={() => setCreateOpen(false)} />
      </GlassSheet>
    </div>
  )
}
