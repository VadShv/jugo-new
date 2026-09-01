import { useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { useInfiniteQuery } from '@tanstack/react-query'
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  type ColumnDef,
  type VisibilityState,
} from '@tanstack/react-table'
import { useVirtualizer } from '@tanstack/react-virtual'
import * as DropdownMenu from '@radix-ui/react-dropdown-menu'
import { SlidersHorizontal } from 'lucide-react'
import type { Page } from '@/shared/api/types'
import { cn } from '@/shared/ui/cn'

export interface RegistryTableProps<TData> {
  columns: ColumnDef<TData>[]
  fetchPage: (args: {
    cursor?: string
    search?: string
    signal?: AbortSignal
  }) => Promise<Page<TData>>
  queryKeyPrefix: readonly unknown[]
  search: string
  onRowClick?: (row: TData) => void
  renderHeader?: (items: TData[]) => ReactNode
  estimateRowHeight?: number
  className?: string
}

/**
 * Reusable registry: TanStack Table + virtualised rows, cursor pagination
 * (next_cursor) via useInfiniteQuery, column-visibility dropdown, and a
 * 250ms debounced search whose AbortSignal is forwarded to the fetcher.
 */
export function RegistryTable<TData>({
  columns,
  fetchPage,
  queryKeyPrefix,
  search,
  onRowClick,
  renderHeader,
  estimateRowHeight = 48,
  className,
}: RegistryTableProps<TData>) {
  const [debouncedSearch, setDebouncedSearch] = useState(search)
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({})

  useEffect(() => {
    const handle = window.setTimeout(() => setDebouncedSearch(search), 250)
    return () => window.clearTimeout(handle)
  }, [search])

  const query = useInfiniteQuery({
    queryKey: [...queryKeyPrefix, debouncedSearch],
    queryFn: ({ pageParam, signal }) =>
      fetchPage({ cursor: pageParam, search: debouncedSearch, signal }),
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage) =>
      lastPage.has_more ? (lastPage.next_cursor ?? undefined) : undefined,
  })

  const items = useMemo(
    () => query.data?.pages.flatMap((page) => page.items) ?? [],
    [query.data],
  )

  const table = useReactTable({
    data: items,
    columns,
    state: { columnVisibility },
    onColumnVisibilityChange: setColumnVisibility,
    getCoreRowModel: getCoreRowModel(),
  })

  const scrollRef = useRef<HTMLDivElement>(null)
  const rows = table.getRowModel().rows
  const rowVirtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => scrollRef.current,
    estimateSize: () => estimateRowHeight,
    overscan: 10,
  })

  const virtualItems = rowVirtualizer.getVirtualItems()
  const totalSize = rowVirtualizer.getTotalSize()

  return (
    <div className={cn('flex flex-col gap-2', className)}>
      {renderHeader?.(items)}

      <div className="flex items-center justify-between">
        <span className="text-xs text-[var(--text-tertiary)]">
          {query.isLoading
            ? 'Загрузка…'
            : `${items.length} записей`}
        </span>
        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            <button
              type="button"
              className="inline-flex items-center gap-1 rounded-pill border border-[var(--glass-border)] bg-[var(--surface-solid)] px-2.5 py-1 text-xs font-medium text-[var(--text-secondary)] hover:bg-[var(--surface-sunken)]"
            >
              <SlidersHorizontal size={14} /> Колонки
            </button>
          </DropdownMenu.Trigger>
          <DropdownMenu.Portal>
            <DropdownMenu.Content
              align="end"
              className="glass glass--regular z-50 rounded-md p-1"
            >
              {table.getAllLeafColumns().map((col) => (
                <DropdownMenu.Item
                  key={col.id}
                  onSelect={(event) => {
                    event.preventDefault()
                    col.toggleVisibility()
                  }}
                  className="flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1 text-sm text-[var(--text-primary)] outline-none hover:bg-[var(--surface-sunken)]"
                >
                  <input
                    type="checkbox"
                    checked={col.getIsVisible()}
                    readOnly
                    className="accent-[var(--accent-blue)]"
                  />
                  {typeof col.columnDef.header === 'string'
                    ? col.columnDef.header
                    : col.id}
                </DropdownMenu.Item>
              ))}
            </DropdownMenu.Content>
          </DropdownMenu.Portal>
        </DropdownMenu.Root>
      </div>

      <div
        ref={scrollRef}
        className="overflow-auto rounded-md border border-[var(--glass-border)] bg-[var(--surface-solid)] shadow-card"
        style={{ height: 560 }}
      >
        <div className="sticky top-0 z-10 flex border-b border-[var(--glass-border)] bg-[var(--surface-sunken)]">
          {table.getFlatHeaders().map((header) => (
            <div
              key={header.id}
              className="px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]"
              style={{ width: header.getSize() }}
            >
              {flexRender(
                header.column.columnDef.header,
                header.getContext(),
              ) as ReactNode}
            </div>
          ))}
        </div>

        {items.length === 0 && !query.isLoading ? (
          <div className="flex h-40 items-center justify-center text-sm text-[var(--text-tertiary)]">
            Ничего не найдено
          </div>
        ) : (
          <div style={{ height: totalSize, position: 'relative' }}>
            {virtualItems.map((virtualRow) => {
              const row = rows[virtualRow.index]
              return (
                <div
                  key={row.id}
                  data-index={virtualRow.index}
                  className={cn(
                    'absolute left-0 top-0 flex w-full cursor-pointer items-center border-b border-[var(--glass-border)] transition-colors hover:bg-[var(--surface-sunken)]',
                    virtualRow.index % 2 === 1 && 'row-zebra',
                  )}
                  style={{
                    transform: `translateY(${virtualRow.start}px)`,
                    height: estimateRowHeight,
                  }}
                  onClick={() => onRowClick?.(row.original)}
                >
                  {row.getVisibleCells().map((cell) => (
                    <div
                      key={cell.id}
                      className="truncate px-3 text-sm text-[var(--text-primary)]"
                      style={{ width: cell.column.getSize() }}
                    >
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      ) as ReactNode}
                    </div>
                  ))}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {query.hasNextPage && (
        <button
          type="button"
          onClick={() => void query.fetchNextPage()}
          disabled={query.isFetchingNextPage}
          className="self-center rounded-pill bg-[var(--accent-blue)] px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {query.isFetchingNextPage ? 'Загрузка…' : 'Загрузить ещё'}
        </button>
      )}
    </div>
  )
}
