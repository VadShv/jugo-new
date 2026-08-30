import { useQuery } from '@tanstack/react-query'
import { request } from '@/shared/api/client'
import type { Candidate, Page } from '@/shared/api/types'

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
  return `/api/v1/candidates${qs ? `?${qs}` : ''}`
}

export async function fetchCandidates({
  cursor,
  search,
  signal,
}: FetchArgs): Promise<Page<Candidate>> {
  return request<Page<Candidate>>(buildPath(cursor, search), { signal })
}

export function useCandidates(search = '') {
  return useQuery({
    queryKey: ['candidates', search],
    queryFn: ({ signal }) => fetchCandidates({ search, signal }),
  })
}
