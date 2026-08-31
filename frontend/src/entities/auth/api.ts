import { request } from '@/shared/api/client'

export interface LoginPayload {
  email: string
  password: string
  role: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface Me {
  user_id: string
  tenant_id: string
  role: string
}

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  return request<LoginResponse>('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export async function fetchMe(): Promise<Me> {
  return request<Me>('/api/v1/auth/me')
}
