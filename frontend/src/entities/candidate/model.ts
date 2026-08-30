import { z } from 'zod'

export const candidateSchema = z.object({
  id: z.string(),
  full_name: z.string(),
  position: z.string().optional(),
  grade: z.string().optional(),
  location: z.string().optional(),
  tags: z.array(z.string()).optional(),
  avatar_url: z.string().optional(),
  match_score: z.number().min(0).max(100).optional(),
  channels: z
    .array(z.enum(['email', 'telegram', 'phone', 'whatsapp']))
    .optional(),
})

export type CandidateFormData = z.infer<typeof candidateSchema>
