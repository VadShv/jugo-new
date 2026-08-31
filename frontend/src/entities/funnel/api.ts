import { useQuery } from '@tanstack/react-query'
import { request } from '@/shared/api/client'
import type { FunnelPreset, FunnelStage, Page } from '@/shared/api/types'

export async function fetchPresets(): Promise<Page<FunnelPreset>> {
  return request<Page<FunnelPreset>>('/api/v1/funnel/presets?limit=50')
}

export async function fetchStages(presetId: string): Promise<FunnelStage[]> {
  return request<FunnelStage[]>(`/api/v1/funnel/presets/${presetId}/stages`)
}

/** Returns stages of the default (or first) funnel preset. */
export function useDefaultStages() {
  const presets = useQuery({
    queryKey: ['funnel-presets'],
    queryFn: fetchPresets,
  })
  const presetId =
    presets.data?.items.find((p) => p.is_default)?.id ?? presets.data?.items[0]?.id
  const stages = useQuery({
    queryKey: ['funnel-stages', presetId],
    enabled: !!presetId,
    queryFn: () => fetchStages(presetId as string),
  })
  return {
    stages: stages.data ?? [],
    loading: presets.isLoading || stages.isLoading,
  }
}
