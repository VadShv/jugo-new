import { request } from '@/shared/api/client'

export async function uploadResume(candidateId: string, file: File): Promise<unknown> {
  const form = new FormData()
  form.append('file', file)
  return request<unknown>(`/api/v1/candidates/${candidateId}/resumes`, {
    method: 'POST',
    body: form,
  })
}
