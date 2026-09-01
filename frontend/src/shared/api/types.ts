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

export interface Criterion {
  criterion: string
  weight: number
  description?: string | null
}

export interface RequirementSetOut {
  id: string
  vacancy_id: string
  name: string
  requirements: Criterion[]
  is_active: boolean
  created_at: string
}

export interface CriterionScore {
  criterion: string
  score: number
  weight: number
  evidence?: string | null
  quote?: string | null
}

export interface ScreeningResultOut {
  id: string
  application_id: string
  vacancy_id: string
  candidate_id: string
  requirement_set_id?: string | null
  total_score?: number | null
  recommendation?: string | null
  confidence?: number | null
  per_criterion: CriterionScore[]
  model?: string | null
  status: string
  is_stale: boolean
  created_at: string
  updated_at: string
}

export interface RiskSignal {
  code: string
  severity: string
  confidence: number
  evidence?: string | null
  alternative_explanation?: string | null
  verification_question?: string | null
}

export interface RiskReportOut {
  id: string
  application_id: string
  candidate_id: string
  vacancy_id: string
  risk_level?: string | null
  signals: RiskSignal[]
  top_risks: string[]
  summary?: string | null
  model?: string | null
  status: string
  created_at: string
  updated_at: string
}

export interface QuestionCard {
  block: string
  question: string
  probes: string[]
  listen_for: string[]
  red_flags: string[]
  source_quote?: string | null
  indicator?: string | null
  valid: boolean
  validation_issues: string[]
}

export interface QuestionSetOut {
  id: string
  vacancy_id: string
  application_id?: string | null
  version_no: number
  status: string
  origin: string
  manual_edited: boolean
  questions: QuestionCard[]
  model?: string | null
  created_at: string
  updated_at: string
}

export interface Donor {
  name: string
  tier: number
  rationale?: string | null
}

export interface Hypothesis {
  text: string
  rationale?: string | null
}

export interface QueryPassport {
  platform: string
  query: string
  terms: string[]
  exclusions: string[]
  rationale?: string | null
}

export interface SearchMapOut {
  id: string
  vacancy_id: string
  version_no: number
  status: string
  role_ontology?: Record<string, unknown> | null
  donors: Donor[]
  hypotheses: Hypothesis[]
  anti_map: string[]
  term_pool?: Record<string, unknown> | null
  query_passports: QueryPassport[]
  justifications: Record<string, string>
  model?: string | null
  created_at: string
  updated_at: string
}
