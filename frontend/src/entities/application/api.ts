import { useQuery } from '@tanstack/react-query'
import { request } from '@/shared/api/client'
import type { Application, Page } from '@/shared/api/types'

export interface FetchArgs {
  cursor?: string
  search?: string
  signal?: AbortSignal
  status?: string
}

function buildPath(cursor?: string, search?: string, status?: string): string {
  const params = new URLSearchParams()
  if (cursor) params.set('cursor', cursor)
  if (search) params.set('q', search)
  if (status) params.set('status', status)
  params.set('limit', '50')
  const qs = params.toString()
  return `/api/v1/applications${qs ? `?${qs}` : ''}`
}

export async function fetchApplications({
  cursor,
  search,
  signal,
  status,
}: FetchArgs): Promise<Page<Application>> {
  return request<Page<Application>>(buildPath(cursor, search, status), { signal })
}

export function useApplications(search = '', status?: string) {
  return useQuery({
    queryKey: ['applications', search, status ?? 'all'],
    queryFn: ({ signal }) => fetchApplications({ search, status, signal }),
  })
}
