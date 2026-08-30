export interface ProblemDetails {
  type?: string
  title?: string
  status?: number
  detail?: string
  instance?: string
  [key: string]: unknown
}

export class ApiError extends Error {
  readonly status: number
  readonly problem: ProblemDetails | null

  constructor(message: string, status: number, problem: ProblemDetails | null) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.problem = problem
  }
}

const BASE_URL = import.meta.env.VITE_API_URL ?? ''

function getToken(): string | null {
  try {
    return localStorage.getItem('ats.token')
  } catch {
    return null
  }
}

/**
 * Typed fetch wrapper. Prepends VITE_API_URL, injects a Bearer token when
 * present, forwards the caller's AbortSignal, and parses application/problem+json
 * errors into {@link ApiError}.
 */
export async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const url = `${BASE_URL}${path}`
  const headers = new Headers(init.headers)
  if (!headers.has('Accept')) headers.set('Accept', 'application/json')

  const token = getToken()
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  let response: Response
  try {
    response = await fetch(url, {
      ...init,
      headers,
      signal: init.signal ?? undefined,
    })
  } catch {
    throw new ApiError('Network error', 0, null)
  }

  if (!response.ok) {
    let problem: ProblemDetails | null = null
    const contentType = response.headers.get('content-type') ?? ''
    if (
      contentType.includes('application/problem+json') ||
      contentType.includes('application/json')
    ) {
      try {
        problem = (await response.json()) as ProblemDetails
      } catch {
        problem = null
      }
    }
    throw new ApiError(
      problem?.detail ?? problem?.title ?? response.statusText,
      response.status,
      problem,
    )
  }

  const contentType = response.headers.get('content-type') ?? ''
  if (response.status === 204 || contentType.length === 0) {
    return undefined as T
  }
  return (await response.json()) as T
}
