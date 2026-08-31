import { useQuery } from '@tanstack/react-query'
import { request } from '@/shared/api/client'
import type { Page, Vacancy } from '@/shared/api/types'

export interface FetchArgs {
  cursor?: string
  search?: string
  signal?: AbortSignal
}

export interface SearchArgs {
  q: string
  cursor?: string
  signal?: AbortSignal
  filters?: Record<string, string>
}

function listPath(cursor?: string): string {
  const params = new URLSearchParams()
  if (cursor) params.set('cursor', cursor)
  params.set('limit', '50')
  return `/api/v1/vacancies?${params.toString()}`
}

export async function fetchVacancies({
  cursor,
  signal,
}: FetchArgs): Promise<Page<Vacancy>> {
  return request<Page<Vacancy>>(listPath(cursor), { signal })
}

export async function searchVacancies({
  q,
  cursor,
  signal,
  filters,
}: SearchArgs): Promise<Page<Vacancy>> {
  return request<Page<Vacancy>>('/api/v1/search/vacancies', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ q, cursor, filters: filters ?? {}, limit: 50 }),
    signal,
  })
}

export function useVacancies(search = '') {
  return useQuery({
    queryKey: ['vacancies', search],
    queryFn: ({ signal }) =>
      search ? searchVacancies({ q: search, signal }) : fetchVacancies({ signal }),
  })
}
