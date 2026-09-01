import { useCallback, useEffect, useRef, useState } from 'react'
import { ApiError, request } from './client'

export type AiJobStatus = 'idle' | 'running' | 'done' | 'error'

export interface UseAiJobOptions {
  /** POST endpoint that enqueues the job (returns 202). */
  runPath: string
  /** GET endpoint polled for the result (returns 200 when ready, 404 while pending). */
  pollPath: string
  pollIntervalMs?: number
  timeoutMs?: number
}

export interface UseAiJobResult<T> {
  status: AiJobStatus
  result: T | null
  error: string | null
  run: () => Promise<void>
}

/**
 * Async AI job pattern: POST :run -> 202, then poll GET until a result appears
 * (200) or timeout. 404 while pending is treated as "still running".
 */
export function useAiJob<T>(opts: UseAiJobOptions): UseAiJobResult<T> {
  const [status, setStatus] = useState<AiJobStatus>('idle')
  const [result, setResult] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  const timer = useRef<number | null>(null)
  const deadline = useRef<number>(0)

  const stop = useCallback(() => {
    if (timer.current !== null) {
      window.clearTimeout(timer.current)
      timer.current = null
    }
  }, [])

  const poll = useCallback(async () => {
    if (Date.now() > deadline.current) {
      setStatus('error')
      setError('Превышено время ожидания результата')
      return
    }
    try {
      const data = await request<T>(opts.pollPath)
      setResult(data)
      setStatus('done')
    } catch (e) {
      if (e instanceof ApiError && e.status === 404) {
        timer.current = window.setTimeout(poll, opts.pollIntervalMs ?? 2000)
      } else {
        setStatus('error')
        setError(e instanceof ApiError ? e.message : 'Ошибка опроса результата')
      }
    }
  }, [opts.pollPath, opts.pollIntervalMs])

  const run = useCallback(async () => {
    stop()
    setStatus('running')
    setError(null)
    setResult(null)
    deadline.current = Date.now() + (opts.timeoutMs ?? 60000)
    try {
      await request(opts.runPath, { method: 'POST' })
    } catch (e) {
      setStatus('error')
      setError(e instanceof ApiError ? e.message : 'Ошибка запуска задачи')
      return
    }
    timer.current = window.setTimeout(poll, opts.pollIntervalMs ?? 2000)
  }, [opts.runPath, opts.timeoutMs, opts.pollIntervalMs, poll, stop])

  useEffect(() => () => stop(), [stop])

  return { status, result, error, run }
}
