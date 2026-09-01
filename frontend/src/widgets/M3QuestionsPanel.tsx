import { useEffect, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { AIResultPanel } from '@/widgets/AIResultPanel'
import { useAiJob } from '@/shared/api/useAiJob'
import { fetchApplications } from '@/entities/application/api'
import { approveQuestionSet } from '@/entities/questions/api'
import type { QuestionCard, QuestionSetOut } from '@/shared/api/types'

const selectClass =
  'rounded-md border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[var(--accent-blue)]/40'

function QuestionCardView({ card }: { card: QuestionCard }) {
  return (
    <div className="rounded-md border border-[var(--glass-border)] bg-[var(--surface-sunken)] p-3">
      <div className="mb-1 flex items-center justify-between">
        <span className="rounded-pill bg-[var(--surface-solid)] px-2 py-0.5 text-xs text-[var(--text-secondary)]">
          {card.block || '—'}
        </span>
        {!card.valid && (
          <span className="text-xs text-[var(--accent-red)]">
            {card.validation_issues.join(', ')}
          </span>
        )}
      </div>
      <p className="text-sm font-medium text-[var(--text-primary)]">{card.question}</p>
      {card.probes.length > 0 && (
        <p className="mt-1 text-xs text-[var(--text-secondary)]">
          <span className="font-medium">Уточнения:</span> {card.probes.join('; ')}
        </p>
      )}
      {card.listen_for.length > 0 && (
        <p className="mt-1 text-xs text-[var(--text-secondary)]">
          <span className="font-medium">Слушать:</span> {card.listen_for.join('; ')}
        </p>
      )}
      {card.red_flags.length > 0 && (
        <p className="mt-1 text-xs text-[var(--accent-red)]">
          <span className="font-medium">Красные флаги:</span> {card.red_flags.join('; ')}
        </p>
      )}
      {card.indicator && (
        <p className="mt-1 text-xs text-[var(--text-tertiary)]">
          <span className="font-medium">Индикатор:</span> {card.indicator}
        </p>
      )}
    </div>
  )
}

export function M3QuestionsPanel({ candidateId }: { candidateId: string }) {
  const { data: appsData } = useQuery({
    queryKey: ['applications', 'candidate', candidateId],
    queryFn: ({ signal }) => fetchApplications({ candidateId, signal }),
  })
  const apps = appsData?.items ?? []
  const [appId, setAppId] = useState('')
  const app = apps.find((a) => a.id === appId)
  const vacancyId = app?.vacancy_id ?? ''
  const [currentSet, setCurrentSet] = useState<QuestionSetOut | null>(null)

  const runPath = `/api/v1/questions/vacancies/${vacancyId}:generate${
    appId ? `?application_id=${appId}` : ''
  }`
  const pollPath = `/api/v1/questions/vacancies/${vacancyId}`
  const genJob = useAiJob<QuestionSetOut>({ runPath, pollPath })

  useEffect(() => {
    if (genJob.result) setCurrentSet(genJob.result)
  }, [genJob.result])

  const approveMut = useMutation({
    mutationFn: (setId: string) => approveQuestionSet(setId),
    onSuccess: (data) => setCurrentSet(data),
  })

  return (
    <div className="flex flex-col gap-4">
      <label className="flex flex-col gap-1 text-sm">
        <span className="font-medium text-[var(--text-secondary)]">
          Отклик (вакансия для вопросов)
        </span>
        <select
          value={appId}
          onChange={(e) => setAppId(e.target.value)}
          className={selectClass}
          disabled={apps.length === 0}
        >
          <option value="">— выберите отклик —</option>
          {apps.map((a) => (
            <option key={a.id} value={a.id}>
              {a.vacancy_id} · {a.status}
            </option>
          ))}
        </select>
      </label>

      {apps.length === 0 && (
        <p className="text-sm text-[var(--text-tertiary)]">
          У кандидата нет откликов — создайте отклик для генерации вопросов.
        </p>
      )}

      {appId && (
        <AIResultPanel
          title="Вопросы для интервью"
          description="ИИ-генерация поведенческих вопросов STAR/CARE"
          status={genJob.status}
          error={genJob.error}
          onRun={genJob.run}
        >
          {currentSet && (
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <span className="text-xs text-[var(--text-tertiary)]">
                  Статус: {currentSet.status} · v{currentSet.version_no}
                </span>
                {currentSet.status !== 'approved' && (
                  <button
                    type="button"
                    onClick={() => approveMut.mutate(currentSet.id)}
                    disabled={approveMut.isPending}
                    className="rounded-pill bg-[var(--accent-green)] px-3 py-1.5 text-sm font-medium text-white disabled:opacity-50"
                  >
                    Утвердить
                  </button>
                )}
              </div>
              {currentSet.questions.map((q, i) => (
                <QuestionCardView key={i} card={q} />
              ))}
            </div>
          )}
        </AIResultPanel>
      )}
    </div>
  )
}
