import { useMemo, useState } from 'react'
import { type ColumnDef } from '@tanstack/react-table'
import { Bookmark } from 'lucide-react'
import { GlassTopBar } from '@/shared/ui/GlassTopBar'
import { GlassSearchField } from '@/shared/ui/GlassSearchField'
import { GlassSheet } from '@/shared/ui/GlassSheet'
import { RegistryTable } from '@/widgets/RegistryTable'
import { fetchCandidates, searchCandidates } from '@/entities/candidate/api'
import { CandidateCard } from '@/entities/candidate/CandidateCard'
import { useUiStore } from '@/app/store'
import type { Candidate } from '@/shared/api/types'

function fullName(c: Candidate): string {
  return `${c.last_name} ${c.first_name}`.trim()
}

export default function CandidatesPage() {
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState<Candidate | null>(null)
  const savedView = useUiStore((state) => state.savedView)
  const setSavedView = useUiStore((state) => state.setSavedView)

  const columns = useMemo<ColumnDef<Candidate>[]>(
    () => [
      {
        id: 'full_name',
        header: 'ФИО',
        size: 200,
        cell: ({ row }) => fullName(row.original),
      },
      {
        id: 'headline',
        accessorKey: 'headline',
        header: 'Должность',
        size: 200,
        cell: ({ row }) => row.original.headline ?? '—',
      },
      {
        id: 'grade',
        accessorKey: 'grade',
        header: 'Грейд',
        size: 100,
        cell: ({ row }) => row.original.grade ?? '—',
      },
      {
        id: 'location',
        accessorKey: 'location',
        header: 'Локация',
        size: 140,
        cell: ({ row }) => row.original.location ?? '—',
      },
      {
        id: 'tags',
        accessorKey: 'tags',
        header: 'Теги',
        size: 220,
        cell: ({ row }) => row.original.tags.join(', ') || '—',
      },
    ],
    [],
  )

  const fetchPage = (args: {
    cursor?: string
    search?: string
    signal?: AbortSignal
  }) =>
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
            <GlassSearchField
              value={search}
              onChange={setSearch}
              placeholder="Поиск кандидатов"
            />
            <button
              type="button"
              onClick={() => setSavedView(search)}
              className="inline-flex items-center gap-1 rounded-pill border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 text-sm font-medium text-[var(--text-secondary)]"
            >
              <Bookmark size={16} /> Сохранить вид
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
        onRowClick={setSelected}
      />

      <GlassSheet
        open={selected !== null}
        onOpenChange={(open) => {
          if (!open) setSelected(null)
        }}
        title={selected ? fullName(selected) : undefined}
      >
        {selected && <CandidateCard candidate={selected} />}
      </GlassSheet>
    </div>
  )
}
