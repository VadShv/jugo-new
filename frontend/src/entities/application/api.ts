import { useQuery } from '@tanstack/react-query'
import { request } from '@/shared/api/client'
import type { Application, Page } from '@/shared/api/types'

export interface FetchArgs {
  cursor?: string
  search?: string
  signal?: AbortSignal
  status?: string
  candidateId?: string
  vacancyId?: string
}

export interface SearchArgs {
  q: string
  cursor?: string
  signal?: AbortSignal
  filters?: Record<string, string>
}

export interface ApplicationCreatePayload {
  candidate_id: string
  vacancy_id: string
  current_stage_id?: string
  origin?: string
  status?: string
}

export interface TransitionPayload {
  to_stage_id: string
  reason?: string
}

export interface TransitionResult {
  application_id: string
  from_stage_id?: string | null
  to_stage_id: string
  status: string
  transition_id: string
}

function listPath(
  cursor?: string,
  status?: string,
  candidateId?: string,
  vacancyId?: string,
): string {
  const params = new URLSearchParams()
  if (cursor) params.set('cursor', cursor)
  if (status) params.set('status', status)
  if (candidateId) params.set('candidate_id', candidateId)
  if (vacancyId) params.set('vacancy_id', vacancyId)
  params.set('limit', '50')
  return `/api/v1/applications?${params.toString()}`
}

export async function fetchApplications({
  cursor,
  signal,
  status,
  candidateId,
  vacancyId,
}: FetchArgs): Promise<Page<Application>> {
  return request<Page<Application>>(listPath(cursor, status, candidateId, vacancyId), {
    signal,
  })
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

export async function createApplication(
  payload: ApplicationCreatePayload,
): Promise<Application> {
  return request<Application>('/api/v1/applications', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ origin: 'manual', status: 'new', ...payload }),
  })
}

export async function transitionApplication(
  id: string,
  payload: TransitionPayload,
): Promise<TransitionResult> {
  return request<TransitionResult>(`/api/v1/applications/${id}/transition`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
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
