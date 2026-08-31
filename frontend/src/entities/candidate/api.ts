import { useQuery } from '@tanstack/react-query'
import { request } from '@/shared/api/client'
import type { Candidate, Page } from '@/shared/api/types'

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

export interface CandidateCreatePayload {
  first_name: string
  last_name: string
  headline?: string
  current_company?: string
  grade?: string
  location?: string
  tags?: string[]
}

function listPath(cursor?: string): string {
  const params = new URLSearchParams()
  if (cursor) params.set('cursor', cursor)
  params.set('limit', '50')
  return `/api/v1/candidates?${params.toString()}`
}

export async function fetchCandidates({
  cursor,
  signal,
}: FetchArgs): Promise<Page<Candidate>> {
  return request<Page<Candidate>>(listPath(cursor), { signal })
}

export async function searchCandidates({
  q,
  cursor,
  signal,
  filters,
}: SearchArgs): Promise<Page<Candidate>> {
  return request<Page<Candidate>>('/api/v1/search/candidates', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ q, cursor, filters: filters ?? {}, limit: 50 }),
    signal,
  })
}

export async function createCandidate(
  payload: CandidateCreatePayload,
): Promise<Candidate> {
  return request<Candidate>('/api/v1/candidates', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function useCandidates(search = '') {
  return useQuery({
    queryKey: ['candidates', search],
    queryFn: ({ signal }) =>
      search
        ? searchCandidates({ q: search, signal })
        : fetchCandidates({ signal }),
  })
}
