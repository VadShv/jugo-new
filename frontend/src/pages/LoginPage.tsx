import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNavigate } from '@tanstack/react-router'
import { LogIn } from 'lucide-react'
import { login } from '@/entities/auth/api'
import { setToken } from '@/shared/api/auth'
import { ApiError } from '@/shared/api/client'

const ROLES = [
  { value: 'recruiter', label: 'Рекрутёр' },
  { value: 'admin', label: 'Администратор' },
  { value: 'hiring_manager', label: 'Нанимающий менеджер' },
  { value: 'viewer', label: 'Наблюдатель' },
] as const

const schema = z.object({
  email: z.string().email('Введите корректный email'),
  password: z.string().min(1, 'Введите пароль'),
  role: z.enum(['recruiter', 'admin', 'hiring_manager', 'viewer']),
})

type Values = z.infer<typeof schema>

export default function LoginPage() {
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Values>({
    resolver: zodResolver(schema),
    defaultValues: { email: '', password: '', role: 'recruiter' },
  })

  const onSubmit = async (values: Values) => {
    setError(null)
    try {
      const res = await login(values)
      setToken(res.access_token)
      await navigate({ to: '/vacancies' })
    } catch (e) {
      setError(
        e instanceof ApiError ? e.problem?.detail ?? e.message : 'Ошибка входа',
      )
    }
  }

  const inputClass =
    'w-full rounded-md border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[var(--accent-blue)]/40'

  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--surface-canvas)] px-4">
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="glass glass--regular w-full max-w-sm rounded-lg p-6 shadow-glass"
      >
        <h1 className="text-xl font-semibold text-[var(--text-on-glass)]">
          ATS Jugo
        </h1>
        <p className="mb-5 text-sm text-[var(--text-secondary)]">Вход в систему</p>

        <div className="flex flex-col gap-4">
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-[var(--text-secondary)]">Email</span>
            <input
              type="email"
              autoComplete="email"
              {...register('email')}
              className={inputClass}
            />
            {errors.email && (
              <span className="text-xs text-[var(--accent-red)]">
                {errors.email.message}
              </span>
            )}
          </label>

          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-[var(--text-secondary)]">Пароль</span>
            <input
              type="password"
              autoComplete="current-password"
              {...register('password')}
              className={inputClass}
            />
            {errors.password && (
              <span className="text-xs text-[var(--accent-red)]">
                {errors.password.message}
              </span>
            )}
          </label>

          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-[var(--text-secondary)]">Роль</span>
            <select {...register('role')} className={inputClass}>
              {ROLES.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>
          </label>

          <button
            type="submit"
            disabled={isSubmitting}
            className="inline-flex items-center justify-center gap-2 rounded-pill bg-[var(--accent-blue)] px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
          >
            <LogIn size={16} />
            {isSubmitting ? 'Вход…' : 'Войти'}
          </button>

          {error && (
            <p className="text-sm text-[var(--accent-red)]">{error}</p>
          )}
        </div>
      </form>
    </div>
  )
}
