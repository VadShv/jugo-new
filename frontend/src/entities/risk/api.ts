import { request } from '@/shared/api/client'
import type { RiskReportOut } from '@/shared/api/types'

export async function fetchRiskReport(
  applicationId: string,
  signal?: AbortSignal,
): Promise<RiskReportOut> {
  return request<RiskReportOut>(`/api/v1/risk/applications/${applicationId}`, {
    signal,
  })
}
