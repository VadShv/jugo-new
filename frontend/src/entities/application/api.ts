import { useQuery } from '@tanstack/react-query'
import { request } from '@/shared/api/client'
import type { Application, Page } from '@/shared/api/types'

export interface FetchArgs {
  cursor?: string
  search?: string
  signal?: AbortSignal
  status?: string
}

export interface SearchArgs {
  q: string
  cursor?: string
  signal?: AbortSignal
  filters?: Record<string, string>
}

function listPath(cursor?: string, status?: string): string {
  const params = new URLSearchParams()
  if (cursor) params.set('cursor', cursor)
  if (status) params.set('status', status)
  params.set('limit', '50')
  return `/api/v1/applications?${params.toString()}`
}

export async function fetchApplications({
  cursor,
  signal,
  status,
}: FetchArgs): Promise<Page<Application>> {
  return request<Page<Application>>(listPath(cursor, status), { signal })
}

export async function searchApplications({
  q,
  cursor,
  signal,
  filters,
}: SearchArgs): Promise<Page<Application>> {
  return request<Page<Application>>('/api/v1/search/applications', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ q, cursor, filters: filters ?? {}, limit: 50 }),
    signal,
  })
}

export function useApplications(search = '', status?: string) {
  return useQuery({
    queryKey: ['applications', search, status ?? 'all'],
    queryFn: ({ signal }) =>
      search
        ? searchApplications({
            q: search,
            signal,
            filters: status && status !== 'all' ? { status } : {},
          })
        : fetchApplications({ status, signal }),
  })
}
