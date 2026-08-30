import { useQuery } from '@tanstack/react-query'
import { request } from '@/shared/api/client'
import type { Page, Vacancy } from '@/shared/api/types'

export interface FetchArgs {
  cursor?: string
  search?: string
  signal?: AbortSignal
}

function buildPath(cursor?: string, search?: string): string {
  const params = new URLSearchParams()
  if (cursor) params.set('cursor', cursor)
  if (search) params.set('q', search)
  params.set('limit', '50')
  const qs = params.toString()
  return `/api/v1/vacancies${qs ? `?${qs}` : ''}`
}

export async function fetchVacancies({
  cursor,
  search,
  signal,
}: FetchArgs): Promise<Page<Vacancy>> {
  return request<Page<Vacancy>>(buildPath(cursor, search), { signal })
}

export function useVacancies(search = '') {
  return useQuery({
    queryKey: ['vacancies', search],
    queryFn: ({ signal }) => fetchVacancies({ search, signal }),
  })
}
