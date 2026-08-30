import { z } from 'zod'

export const applicationSchema = z.object({
  id: z.string(),
  candidate_id: z.string(),
  candidate_name: z.string().optional(),
  vacancy_id: z.string(),
  vacancy_title: z.string().optional(),
  stage: z.enum(['new', 'screening', 'interview', 'offer', 'rejected']),
  updated_at: z.string().optional(),
})

export type ApplicationFormData = z.infer<typeof applicationSchema>
