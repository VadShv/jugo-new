import { useQuery } from '@tanstack/react-query'
import { request } from '@/shared/api/client'
import type { Application, Page } from '@/shared/api/types'

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
  return `/api/v1/applications${qs ? `?${qs}` : ''}`
}

export async function fetchApplications({
  cursor,
  search,
  signal,
}: FetchArgs): Promise<Page<Application>> {
  return request<Page<Application>>(buildPath(cursor, search), { signal })
}

export function useApplications(search = '') {
  return useQuery({
    queryKey: ['applications', search],
    queryFn: ({ signal }) => fetchApplications({ search, signal }),
  })
}
