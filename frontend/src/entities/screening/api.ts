import { request } from '@/shared/api/client'
import type { RequirementSetOut, ScreeningResultOut } from '@/shared/api/types'

export async function fetchRequirements(
  vacancyId: string,
  signal?: AbortSignal,
): Promise<RequirementSetOut> {
  return request<RequirementSetOut>(
    `/api/v1/screening/vacancies/${vacancyId}/requirements`,
    { signal },
  )
}

export async function fetchScreeningResult(
  applicationId: string,
  signal?: AbortSignal,
): Promise<ScreeningResultOut> {
  return request<ScreeningResultOut>(
    `/api/v1/screening/applications/${applicationId}`,
    { signal },
  )
}
