import { request } from '@/shared/api/client'
import type { QuestionSetOut } from '@/shared/api/types'

export async function fetchLatestQuestions(
  vacancyId: string,
  signal?: AbortSignal,
): Promise<QuestionSetOut> {
  return request<QuestionSetOut>(`/api/v1/questions/vacancies/${vacancyId}`, {
    signal,
  })
}

export async function approveQuestionSet(setId: string): Promise<QuestionSetOut> {
  return request<QuestionSetOut>(`/api/v1/questions/sets/${setId}:approve`, {
    method: 'POST',
  })
}
