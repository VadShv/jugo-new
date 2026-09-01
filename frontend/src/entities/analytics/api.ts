import { request } from '@/shared/api/client'
import type {
  AIStat,
  FunnelOut,
  RecruiterStat,
  SourceStat,
} from '@/shared/api/types'

export async function fetchFunnel(
  vacancyId: string,
  signal?: AbortSignal,
): Promise<FunnelOut> {
  return request<FunnelOut>(`/api/v1/analytics/funnel/${vacancyId}`, { signal })
}

export async function fetchSources(signal?: AbortSignal): Promise<SourceStat[]> {
  return request<SourceStat[]>('/api/v1/analytics/sources', { signal })
}

export async function fetchAiStats(signal?: AbortSignal): Promise<AIStat[]> {
  return request<AIStat[]>('/api/v1/analytics/ai', { signal })
}

export async function fetchRecruiters(signal?: AbortSignal): Promise<RecruiterStat[]> {
  return request<RecruiterStat[]>('/api/v1/analytics/recruiters', { signal })
}
