import { useMemo, useState } from 'react'
import { type ColumnDef } from '@tanstack/react-table'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import { Bookmark, Plus } from 'lucide-react'
import { GlassTopBar } from '@/shared/ui/GlassTopBar'
import { GlassSearchField } from '@/shared/ui/GlassSearchField'
import { GlassSheet } from '@/shared/ui/GlassSheet'
import { RegistryTable } from '@/widgets/RegistryTable'
import {
  createCandidate,
  fetchCandidates,
  searchCandidates,
} from '@/entities/candidate/api'
import { useUiStore } from '@/app/store'
import { ApiError } from '@/shared/api/client'
import type { Candidate } from '@/shared/api/types'

function fullName(c: Candidate): string {
  return `${c.last_name} ${c.first_name}`.trim()
}

const createSchema = z.object({
  first_name: z.string().min(1, 'Введите имя'),
  last_name: z.string().min(1, 'Введите фамилию'),
  headline: z.string().optional(),
  grade: z.string().optional(),
  location: z.string().optional(),
  tags: z.string().optional(),
})
type CreateValues = z.infer<typeof createSchema>

function AddCandidateForm({ onSubmitted }: { onSubmitted: () => void }) {
  const queryClient = useQueryClient()
  const [error, setError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<CreateValues>({ resolver: zodResolver(createSchema) })

  const mutation = useMutation({
    mutationFn: (values: CreateValues) =>
      createCandidate({
        first_name: values.first_name,
        last_name: values.last_name,
        headline: values.headline || undefined,
        grade: values.grade || undefined,
        location: values.location || undefined,
        tags: values.tags
          ? values.tags.split(',').map((t) => t.trim()).filter(Boolean)
          : [],
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['candidates'] })
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
      <div className="grid grid-cols-2 gap-3">
        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-[var(--text-secondary)]">Фамилия</span>
          <input {...register('last_name')} className={inputClass} />
          {errors.last_name && (
            <span className="text-xs text-[var(--accent-red)]">{errors.last_name.message}</span>
          )}
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-[var(--text-secondary)]">Имя</span>
          <input {...register('first_name')} className={inputClass} />
          {errors.first_name && (
            <span className="text-xs text-[var(--accent-red)]">{errors.first_name.message}</span>
          )}
        </label>
      </div>
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium text-[var(--text-secondary)]">Должность</span>
        <input {...register('headline')} className={inputClass} />
      </label>
      <div className="grid grid-cols-2 gap-3">
        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-[var(--text-secondary)]">Грейд</span>
          <input {...register('grade')} className={inputClass} />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-[var(--text-secondary)]">Локация</span>
          <input {...register('location')} className={inputClass} />
        </label>
      </div>
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium text-[var(--text-secondary)]">Теги (через запятую)</span>
        <input {...register('tags')} className={inputClass} />
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

export default function CandidatesPage() {
  const [search, setSearch] = useState('')
  const [createOpen, setCreateOpen] = useState(false)
  const navigate = useNavigate()
  const savedView = useUiStore((state) => state.savedView)
  const setSavedView = useUiStore((state) => state.setSavedView)

  const columns = useMemo<ColumnDef<Candidate>[]>(
    () => [
      { id: 'full_name', header: 'ФИО', size: 200, cell: ({ row }) => fullName(row.original) },
      { id: 'headline', accessorKey: 'headline', header: 'Должность', size: 200, cell: ({ row }) => row.original.headline ?? '—' },
      { id: 'grade', accessorKey: 'grade', header: 'Грейд', size: 100, cell: ({ row }) => row.original.grade ?? '—' },
      { id: 'location', accessorKey: 'location', header: 'Локация', size: 140, cell: ({ row }) => row.original.location ?? '—' },
      { id: 'tags', accessorKey: 'tags', header: 'Теги', size: 220, cell: ({ row }) => row.original.tags.join(', ') || '—' },
    ],
    [],
  )

  const fetchPage = (args: { cursor?: string; search?: string; signal?: AbortSignal }) =>
    args.search
      ? searchCandidates({ q: args.search, cursor: args.cursor, signal: args.signal })
      : fetchCandidates(args)

  return (
    <div className="flex flex-col gap-3">
      <GlassTopBar
        title="Кандидаты"
        sticky={false}
        trailing={
          <>
            <GlassSearchField value={search} onChange={setSearch} placeholder="Поиск кандидатов" />
            <button
              type="button"
              onClick={() => setSavedView(search)}
              className="inline-flex items-center gap-1 rounded-pill border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 text-sm font-medium text-[var(--text-secondary)]"
            >
              <Bookmark size={16} /> Сохранить вид
            </button>
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

      {savedView != null && (
        <div className="text-xs text-[var(--text-tertiary)]">
          Сохранённый вид: «{savedView || '—all'}»
        </div>
      )}

      <RegistryTable
        columns={columns}
        fetchPage={fetchPage}
        queryKeyPrefix={['candidates']}
        search={search}
        onRowClick={(c) =>
          navigate({ to: '/candidates/$candidateId', params: { candidateId: c.id } })
        }
      />

      <GlassSheet open={createOpen} onOpenChange={setCreateOpen} title="Новый кандидат">
        <AddCandidateForm onSubmitted={() => setCreateOpen(false)} />
      </GlassSheet>
    </div>
  )
}
