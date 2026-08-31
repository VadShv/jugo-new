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
