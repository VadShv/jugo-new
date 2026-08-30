import { z } from 'zod'

export const vacancySchema = z.object({
  id: z.string(),
  title: z.string().min(1),
  department: z.string().optional(),
  status: z.enum(['draft', 'open', 'paused', 'closed']).optional(),
  location: z.string().optional(),
  created_at: z.string().optional(),
})

export type VacancyFormData = z.infer<typeof vacancySchema>
