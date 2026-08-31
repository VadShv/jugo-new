/** Application status (backend ApplicationOut.status). */
export type ApplicationStatus =
  | 'new'
  | 'in_progress'
  | 'hired'
  | 'rejected'
  | 'withdrawn'

export interface Candidate {
  id: string
  tenant_id: string
  first_name: string
  last_name: string
  headline?: string | null
  current_company?: string | null
  grade?: string | null
  location?: string | null
  tags: string[]
  is_blacklisted: boolean
  created_at: string
  updated_at: string
}

export interface Vacancy {
  id: string
  tenant_id: string
  title: string
  description?: string | null
  status: string
  headcount: number
  recruiter_id?: string | null
  hiring_manager_id?: string | null
  created_at: string
  updated_at: string
}

export interface Application {
  id: string
  tenant_id: string
  candidate_id: string
  vacancy_id: string
  current_stage_id?: string | null
  origin: string
  status: string
  screening_score?: number | null
  risk_level?: string | null
  created_at: string
  updated_at: string
}

export interface Page<T> {
  items: T[]
  next_cursor: string | null
  has_more: boolean
}

export interface FunnelPreset {
  id: string
  tenant_id: string
  name: string
  description?: string | null
  is_default: boolean
  created_at: string
  updated_at: string
}

export interface FunnelStage {
  id: string
  tenant_id: string
  preset_id?: string | null
  vacancy_id?: string | null
  name: string
  order_index: number
  stage_type: string
  created_at: string
  updated_at: string
}

export interface FunnelOut {
  vacancy_id: string
  total: number
  by_status: Record<string, number>
  by_stage: Array<{ stage_id: string | null; count: number }>
  hired_rate: number
  reject_rate: number
}

export interface SourceStat {
  origin: string
  count: number
}

export interface AIStat {
  task: string
  count: number
  avg_latency_ms?: number | null
}

export interface RecruiterStat {
  recruiter_id?: string | null
  count: number
}
