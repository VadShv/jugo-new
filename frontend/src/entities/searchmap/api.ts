import { request } from '@/shared/api/client'
import type { SearchMapOut } from '@/shared/api/types'

export async function fetchSearchMap(
  vacancyId: string,
  signal?: AbortSignal,
): Promise<SearchMapOut> {
  return request<SearchMapOut>(`/api/v1/search-map/vacancies/${vacancyId}`, {
    signal,
  })
}
