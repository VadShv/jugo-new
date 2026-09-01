import type { CriterionScore, ScreeningResultOut } from '@/shared/api/types'

const RECO_COLOR: Record<string, string> = {
  recommend: 'var(--accent-green)',
  borderline: 'var(--accent-orange)',
  reject: 'var(--accent-red)',
}

export function ScreeningResultView({ result }: { result: ScreeningResultOut }) {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap gap-4">
        {result.total_score != null && (
          <div>
            <div className="text-xs text-[var(--text-tertiary)]">Итоговый балл</div>
            <div className="text-lg font-semibold text-[var(--text-primary)]">
              {Math.round(result.total_score * 100)}%
            </div>
          </div>
        )}
        {result.recommendation && (
          <div>
            <div className="text-xs text-[var(--text-tertiary)]">Рекомендация</div>
            <div
              className="text-lg font-semibold"
              style={{ color: RECO_COLOR[result.recommendation] ?? 'var(--text-primary)' }}
            >
              {result.recommendation}
            </div>
          </div>
        )}
        {result.confidence != null && (
          <div>
            <div className="text-xs text-[var(--text-tertiary)]">Уверенность</div>
            <div className="text-lg font-semibold text-[var(--text-primary)]">
              {Math.round(result.confidence * 100)}%
            </div>
          </div>
        )}
      </div>
      <div className="overflow-auto rounded-md border border-[var(--glass-border)]">
        <table className="w-full text-sm">
          <thead className="bg-[var(--surface-sunken)] text-left text-xs uppercase text-[var(--text-secondary)]">
            <tr>
              <th className="px-3 py-2">Критерий</th>
              <th className="px-3 py-2">Балл</th>
              <th className="px-3 py-2">Доказательство</th>
              <th className="px-3 py-2">Цитата</th>
            </tr>
          </thead>
          <tbody>
            {result.per_criterion.map((c: CriterionScore, i: number) => (
              <tr key={i} className="border-t border-[var(--glass-border)] align-top">
                <td className="px-3 py-2 font-medium">{c.criterion}</td>
                <td className="px-3 py-2 tabular-nums">{c.score.toFixed(1)}</td>
                <td className="px-3 py-2 text-[var(--text-secondary)]">{c.evidence ?? '—'}</td>
                <td className="px-3 py-2 text-[var(--text-tertiary)]">{c.quote ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {result.model && (
        <p className="text-xs text-[var(--text-tertiary)]">
          Модель: {result.model} · whitebox (ai_runs)
        </p>
      )}
    </div>
  )
}
