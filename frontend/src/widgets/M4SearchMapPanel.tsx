import { AIResultPanel } from '@/widgets/AIResultPanel'
import { useAiJob } from '@/shared/api/useAiJob'
import type { SearchMapOut } from '@/shared/api/types'

const TIER_LABEL: Record<number, string> = {
  1: 'Прямые',
  2: 'Смежные',
  3: 'Широкие',
}

function SearchMapView({ map }: { map: SearchMapOut }) {
  return (
    <div className="flex flex-col gap-4">
      {map.anti_map.length > 0 && (
        <p className="text-xs text-[var(--text-tertiary)]">
          <span className="font-medium">Анти-карта:</span> {map.anti_map.join(', ')}
        </p>
      )}

      <div>
        <h4 className="mb-2 text-sm font-semibold text-[var(--text-primary)]">
          Доноры
        </h4>
        <div className="flex flex-col gap-1">
          {map.donors.map((d, i) => (
            <div
              key={i}
              className="rounded-md border border-[var(--glass-border)] bg-[var(--surface-sunken)] p-2 text-sm"
            >
              <span className="font-medium text-[var(--text-primary)]">
                {TIER_LABEL[d.tier] ?? `Тир ${d.tier}`}
              </span>{' '}
              · {d.name}
              {d.rationale && (
                <p className="mt-0.5 text-xs text-[var(--text-secondary)]">
                  {d.rationale}
                </p>
              )}
            </div>
          ))}
        </div>
      </div>

      {map.hypotheses.length > 0 && (
        <div>
          <h4 className="mb-2 text-sm font-semibold text-[var(--text-primary)]">
            Гипотезы
          </h4>
          <ul className="flex list-disc flex-col gap-1 pl-5 text-sm text-[var(--text-secondary)]">
            {map.hypotheses.map((h, i) => (
              <li key={i}>{h.text}</li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <h4 className="mb-2 text-sm font-semibold text-[var(--text-primary)]">
          Паспорта запросов
        </h4>
        <div className="flex flex-col gap-2">
          {map.query_passports.map((p, i) => (
            <div
              key={i}
              className="rounded-md border border-[var(--glass-border)] bg-[var(--surface-sunken)] p-2"
            >
              <div className="mb-1 flex items-center justify-between">
                <span className="text-sm font-medium text-[var(--text-primary)]">
                  {p.platform}
                </span>
                <button
                  type="button"
                  onClick={() => void navigator.clipboard.writeText(p.query)}
                  className="rounded-pill bg-[var(--surface-solid)] px-2 py-0.5 text-xs text-[var(--text-secondary)]"
                >
                  копировать
                </button>
              </div>
              <code className="block overflow-x-auto text-xs text-[var(--text-secondary)]">
                {p.query}
              </code>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export function M4SearchMapPanel({ vacancyId }: { vacancyId: string }) {
  const job = useAiJob<SearchMapOut>({
    runPath: `/api/v1/search-map/vacancies/${vacancyId}:generate`,
    pollPath: `/api/v1/search-map/vacancies/${vacancyId}`,
  })
  return (
    <AIResultPanel
      title="Карта поиска"
      description="ИИ-конвейер: онтология → доноры → термы → паспорта запросов"
      status={job.status}
      error={job.error}
      onRun={job.run}
    >
      {job.result && <SearchMapView map={job.result} />}
    </AIResultPanel>
  )
}
