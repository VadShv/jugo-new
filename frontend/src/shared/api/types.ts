export type Stage = 'new' | 'screening' | 'interview' | 'offer' | 'rejected'

export type Channel = 'email' | 'telegram' | 'phone' | 'whatsapp'

export type VacancyStatus = 'draft' | 'open' | 'paused' | 'closed'

export interface Candidate {
  id: string
  full_name: string
  position?: string
  grade?: string
  location?: string
  tags?: string[]
  avatar_url?: string
  match_score?: number
  channels?: Channel[]
}

export interface Vacancy {
  id: string
  title: string
  department?: string
  status?: VacancyStatus
  location?: string
  created_at?: string
}

export interface Application {
  id: string
  candidate_id: string
  candidate_name?: string
  vacancy_id: string
  vacancy_title?: string
  stage: Stage
  updated_at?: string
}

export interface Page<T> {
  items: T[]
  next_cursor: string | null
  has_more: boolean
}
