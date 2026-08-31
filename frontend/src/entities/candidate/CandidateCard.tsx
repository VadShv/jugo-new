import type { Candidate } from '@/shared/api/types'
import { CandidateCard as CandidateCardUI } from '@/shared/ui/CandidateCard'

export interface EntityCandidateCardProps {
  candidate: Candidate
  onClick?: () => void
}

/**
 * Entity-level candidate card: maps the {@link Candidate} model onto the
 * presentational glass/opaque card from shared/ui.
 */
export function CandidateCard({ candidate, onClick }: EntityCandidateCardProps) {
  return (
    <CandidateCardUI
      name={`${candidate.first_name} ${candidate.last_name}`}
      role={candidate.headline ?? undefined}
      onClick={onClick}
    />
  )
}
