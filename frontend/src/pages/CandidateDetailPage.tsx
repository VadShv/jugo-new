import { useState, type ReactNode } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate, useParams } from '@tanstack/react-router'
import { ArrowLeft, Upload } from 'lucide-react'
import { GlassTopBar } from '@/shared/ui/GlassTopBar'
import { StatusBadge } from '@/shared/ui/StatusBadge'
import { DetailLayout, type DetailTab } from '@/widgets/DetailLayout'
import { M1ScreeningPanel } from '@/widgets/M1ScreeningPanel'
import { M2RiskPanel } from '@/widgets/M2RiskPanel'
import { M3QuestionsPanel } from '@/widgets/M3QuestionsPanel'
import { fetchCandidate } from '@/entities/candidate/api'
import { fetchApplications } from '@/entities/application/api'
import { uploadResume } from '@/entities/resumes/api'
import { ApiError } from '@/shared/api/client'
import type { Candidate } from '@/shared/api/types'

function SummaryTab({ candidate }: { candidate: Candidate }) {
  const rows: Array<[string, ReactNode]> = [
    ['Должность', candidate.headline ?? '—'],
    ['Компания', candidate.current_company ?? '—'],
    ['Грейд', candidate.grade ?? '—'],
    ['Локация', candidate.location ?? '—'],
    ['Теги', candidate.tags.length ? candidate.tags.join(', ') : '—'],
    ['Чёрный список', candidate.is_blacklisted ? 'да' : 'нет'],
  ]
  return (
    <dl className="grid grid-cols-1 gap-2 sm:grid-cols-2">
      {rows.map(([label, value]) => (
        <div
          key={label}
          className="flex flex-col rounded-md border border-[var(--glass-border)] bg-[var(--surface-solid)] p-3"
        >
          <dt className="text-xs text-[var(--text-tertiary)]">{label}</dt>
          <dd className="text-sm text-[var(--text-primary)]">{value}</dd>
        </div>
      ))}
    </dl>
  )
}

function ResumeTab({ candidateId }: { candidateId: string }) {
  const queryClient = useQueryClient()
  const [message, setMessage] = useState<string | null>(null)
  const mutation = useMutation({
    mutationFn: (file: File) => uploadResume(candidateId, file),
    onSuccess: () => {
      setMessage('Резюме загружено')
      void queryClient.invalidateQueries({ queryKey: ['candidate', candidateId] })
    },
    onError: (e) =>
      setMessage(e instanceof ApiError ? e.problem?.detail ?? e.message : 'Ошибка загрузки'),
  })

  return (
    <div className="flex flex-col gap-3">
      <label className="inline-flex w-fit cursor-pointer items-center gap-2 rounded-pill bg-[var(--accent-blue)] px-3 py-1.5 text-sm font-medium text-white">
        <Upload size={16} /> Загрузить резюме
        <input
          type="file"
          accept=".pdf,.docx,.doc,.txt,.html"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) mutation.mutate(file)
          }}
        />
      </label>
      {mutation.isPending && <p className="text-sm text-[var(--text-secondary)]">Загрузка…</p>}
      {message && <p className="text-sm text-[var(--text-primary)]">{message}</p>}
      <p className="text-xs text-[var(--text-tertiary)]">
        Поддерживаются PDF/DOCX/TXT/HTML. Текст извлекается автоматически; список версий — в G9.
      </p>
    </div>
  )
}

function ApplicationsTab({ candidateId }: { candidateId: string }) {
  const { data, isLoading } = useQuery({
    queryKey: ['applications', 'candidate', candidateId],
    queryFn: ({ signal }) => fetchApplications({ candidateId, signal }),
  })
  const items = data?.items ?? []

  if (isLoading) return <p className="text-sm text-[var(--text-tertiary)]">Загрузка…</p>
  if (items.length === 0)
    return <p className="text-sm text-[var(--text-tertiary)]">Нет откликов.</p>

  return (
    <ul className="flex flex-col gap-2">
      {items.map((app) => (
        <li
          key={app.id}
          className="flex items-center justify-between rounded-md border border-[var(--glass-border)] bg-[var(--surface-solid)] p-3"
        >
          <div className="flex flex-col">
            <span className="font-mono text-xs text-[var(--text-secondary)]">
              {app.vacancy_id}
            </span>
            <span className="text-xs text-[var(--text-tertiary)]">
              {app.updated_at ?? '—'}
            </span>
          </div>
          <StatusBadge status={app.status} />
        </li>
      ))}
    </ul>
  )
}

export default function CandidateDetailPage() {
  const params = useParams({ strict: false }) as { candidateId?: string }
  const candidateId = params.candidateId
  const navigate = useNavigate()
  const { data: candidate, isLoading } = useQuery({
    queryKey: ['candidate', candidateId],
    enabled: !!candidateId,
    queryFn: ({ signal }) => fetchCandidate(candidateId as string, signal),
  })

  if (!candidateId) return null
  if (isLoading)
    return <p className="text-sm text-[var(--text-tertiary)]">Загрузка…</p>
  if (!candidate)
    return <p className="text-sm text-[var(--text-tertiary)]">Кандидат не найден.</p>

  const tabs: DetailTab[] = [
    { value: 'summary', label: 'Сводка', content: <SummaryTab candidate={candidate} /> },
    { value: 'resume', label: 'Резюме', content: <ResumeTab candidateId={candidateId} /> },
    { value: 'applications', label: 'Отклики', content: <ApplicationsTab candidateId={candidateId} /> },
    { value: 'screening', label: 'Оценка', content: <M1ScreeningPanel candidateId={candidateId} /> },
    { value: 'risk', label: 'Риски', content: <M2RiskPanel candidateId={candidateId} /> },
    { value: 'questions', label: 'Вопросы', content: <M3QuestionsPanel candidateId={candidateId} /> },
  ]

  return (
    <div className="flex flex-col gap-3">
      <GlassTopBar
        title="Кандидат"
        sticky={false}
        trailing={
          <button
            type="button"
            onClick={() => navigate({ to: '/candidates' })}
            className="inline-flex items-center gap-1 rounded-pill border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 text-sm text-[var(--text-secondary)]"
          >
            <ArrowLeft size={16} /> К списку
          </button>
        }
      />
      <DetailLayout
        title={`${candidate.last_name} ${candidate.first_name}`}
        meta={
          <>
            {candidate.headline && <span>{candidate.headline}</span>}
            {candidate.grade && <span>· {candidate.grade}</span>}
            {candidate.location && <span>· {candidate.location}</span>}
          </>
        }
        tabs={tabs}
      />
    </div>
  )
}
