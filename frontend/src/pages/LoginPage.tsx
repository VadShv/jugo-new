import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useNavigate } from '@tanstack/react-router'
import { LogIn } from 'lucide-react'
import { login } from '@/entities/auth/api'
import { setToken } from '@/shared/api/auth'
import { ApiError } from '@/shared/api/client'
import {
  buttonPrimaryClass,
  fieldClass,
  fieldErrorClass,
  fieldLabelClass,
} from '@/shared/ui/field'

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

  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--surface-canvas)] px-4">
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="glass glass--regular w-full max-w-sm rounded-2xl p-8 shadow-glass"
      >
        <div className="mb-6 flex flex-col gap-1">
          <h1 className="text-2xl font-semibold text-[var(--text-on-glass)]">
            ATS Jugo
          </h1>
          <p className="text-sm text-[var(--text-secondary)]">
            Войдите в систему найма
          </p>
        </div>

        <div className="flex flex-col gap-4">
          <label className="flex flex-col gap-1.5">
            <span className={fieldLabelClass}>Email</span>
            <input
              type="email"
              autoComplete="email"
              {...register('email')}
              className={fieldClass}
            />
            {errors.email && (
              <span className={fieldErrorClass}>{errors.email.message}</span>
            )}
          </label>

          <label className="flex flex-col gap-1.5">
            <span className={fieldLabelClass}>Пароль</span>
            <input
              type="password"
              autoComplete="current-password"
              {...register('password')}
              className={fieldClass}
            />
            {errors.password && (
              <span className={fieldErrorClass}>{errors.password.message}</span>
            )}
          </label>

          <label className="flex flex-col gap-1.5">
            <span className={fieldLabelClass}>Роль</span>
            <select {...register('role')} className={fieldClass}>
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
            className={buttonPrimaryClass}
          >
            <LogIn size={16} />
            {isSubmitting ? 'Вход…' : 'Войти'}
          </button>

          {error && <p className={fieldErrorClass}>{error}</p>}
        </div>
      </form>
    </div>
  )
}
