import { request } from '@/shared/api/client'
import type {
  AIStat,
  FunnelOut,
  RecruiterStat,
  SourceStat,
} from '@/shared/api/types'

export async function fetchFunnel(vacancyId: string): Promise<FunnelOut> {
  return request<FunnelOut>(`/api/v1/analytics/funnel/${vacancyId}`)
}

export async function fetchSources(): Promise<SourceStat[]> {
  return request<SourceStat[]>('/api/v1/analytics/sources')
}

export async function fetchAiStats(): Promise<AIStat[]> {
  return request<AIStat[]>('/api/v1/analytics/ai')
}

export async function fetchRecruiters(): Promise<RecruiterStat[]> {
  return request<RecruiterStat[]>('/api/v1/analytics/recruiters')
}
