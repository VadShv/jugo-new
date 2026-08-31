import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import ReactECharts from 'echarts-for-react'
import type { EChartsOption } from 'echarts'
import * as Tabs from '@radix-ui/react-tabs'
import { GlassTopBar } from '@/shared/ui/GlassTopBar'
import {
  fetchAiStats,
  fetchFunnel,
  fetchRecruiters,
  fetchSources,
} from '@/entities/analytics/api'
import { fetchVacancies } from '@/entities/vacancy/api'

const STATUS_LABEL: Record<string, string> = {
  new: 'Новый',
  in_progress: 'В работе',
  hired: 'Нанят',
  rejected: 'Отказ',
  withdrawn: 'Отозван',
}
const STATUS_ORDER = ['new', 'in_progress', 'hired', 'rejected', 'withdrawn']

const selectClass =
  'rounded-pill border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 text-sm text-[var(--text-secondary)] outline-none focus:ring-2 focus:ring-[var(--accent-blue)]/40'

function Kpi({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-[var(--glass-border)] bg-[var(--surface-solid)] p-3 shadow-card">
      <div className="text-xs text-[var(--text-tertiary)]">{label}</div>
      <div className="text-xl font-semibold text-[var(--text-primary)]">{value}</div>
    </div>
  )
}

function Empty({ text }: { text: string }) {
  return (
    <div className="flex h-40 items-center justify-center text-sm text-[var(--text-tertiary)]">
      {text}
    </div>
  )
}

export default function AnalyticsPage() {
  const [vacancyId, setVacancyId] = useState('')

  const vacancies = useQuery({
    queryKey: ['vacancies-select'],
    queryFn: ({ signal }) => fetchVacancies({ signal }),
  })
  const effectiveVacancyId =
    vacancyId || vacancies.data?.items[0]?.id || ''
  const funnel = useQuery({
    queryKey: ['analytics-funnel', effectiveVacancyId],
    enabled: !!effectiveVacancyId,
    queryFn: () => fetchFunnel(effectiveVacancyId),
  })
  const sources = useQuery({
    queryKey: ['analytics-sources'],
    queryFn: () => fetchSources(),
  })
  const ai = useQuery({
    queryKey: ['analytics-ai'],
    queryFn: () => fetchAiStats(),
  })
  const recruiters = useQuery({
    queryKey: ['analytics-recruiters'],
    queryFn: () => fetchRecruiters(),
  })

  const funnelBar: EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: STATUS_ORDER.map((s) => STATUS_LABEL[s] ?? s),
    },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        type: 'bar',
        data: STATUS_ORDER.map((s) => funnel.data?.by_status[s] ?? 0),
        itemStyle: { color: 'var(--accent-blue)' },
      },
    ],
  }

  const sourceBar: EChartsOption = {
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: sources.data?.map((s) => s.origin) ?? [],
    },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        type: 'bar',
        data: sources.data?.map((s) => s.count) ?? [],
        itemStyle: { color: 'var(--accent-teal)' },
      },
    ],
  }

  return (
    <div className="flex flex-col gap-3">
      <GlassTopBar
        title="Аналитика"
        sticky={false}
        trailing={
          <select
            value={effectiveVacancyId}
            onChange={(e) => setVacancyId(e.target.value)}
            className={selectClass}
          >
            {(vacancies.data?.items ?? []).map((v) => (
              <option key={v.id} value={v.id}>
                {v.title}
              </option>
            ))}
          </select>
        }
      />

      <Tabs.Root defaultValue="funnel">
        <Tabs.List className="inline-flex gap-1 rounded-pill bg-[var(--surface-sunken)] p-1">
          {[
            ['funnel', 'Воронка'],
            ['sources', 'Источники'],
            ['ai', 'ИИ-операции'],
            ['recruiters', 'Рекрутёры'],
          ].map(([value, label]) => (
            <Tabs.Trigger
              key={value}
              value={value}
              className="rounded-pill px-3 py-1 text-sm font-medium text-[var(--text-secondary)] data-[state=active]:bg-[var(--surface-solid)] data-[state=active]:text-[var(--text-primary)] data-[state=active]:shadow-card"
            >
              {label}
            </Tabs.Trigger>
          ))}
        </Tabs.List>

        <Tabs.Content value="funnel" className="mt-3">
          <div className="rounded-lg border border-[var(--glass-border)] bg-[var(--surface-solid)] p-4 shadow-card">
            <div className="mb-3 grid grid-cols-3 gap-3">
              <Kpi label="Всего откликов" value={String(funnel.data?.total ?? 0)} />
              <Kpi
                label="Найм"
                value={`${Math.round((funnel.data?.hired_rate ?? 0) * 100)}%`}
              />
              <Kpi
                label="Отказ"
                value={`${Math.round((funnel.data?.reject_rate ?? 0) * 100)}%`}
              />
            </div>
            {funnel.isLoading ? (
              <Empty text="Загрузка…" />
            ) : (funnel.data?.total ?? 0) === 0 ? (
              <Empty text="Нет откликов по вакансии" />
            ) : (
              <ReactECharts option={funnelBar} style={{ height: 320 }} />
            )}
          </div>
        </Tabs.Content>

        <Tabs.Content value="sources" className="mt-3">
          <div className="rounded-lg border border-[var(--glass-border)] bg-[var(--surface-solid)] p-4 shadow-card">
            {sources.isLoading ? (
              <Empty text="Загрузка…" />
            ) : (sources.data?.length ?? 0) === 0 ? (
              <Empty text="Нет данных по источникам" />
            ) : (
              <ReactECharts option={sourceBar} style={{ height: 320 }} />
            )}
          </div>
        </Tabs.Content>

        <Tabs.Content value="ai" className="mt-3">
          <div className="overflow-auto rounded-md border border-[var(--glass-border)] bg-[var(--surface-solid)] shadow-card">
            <table className="w-full text-sm">
              <thead className="bg-[var(--surface-sunken)] text-left text-xs uppercase tracking-wide text-[var(--text-secondary)]">
                <tr>
                  <th className="px-3 py-2">Задача</th>
                  <th className="px-3 py-2">Запусков</th>
                  <th className="px-3 py-2">Ср. латентность, мс</th>
                </tr>
              </thead>
              <tbody>
                {ai.isLoading ? (
                  <tr><td colSpan={3} className="px-3 py-4 text-center text-[var(--text-tertiary)]">Загрузка…</td></tr>
                ) : (ai.data?.length ?? 0) === 0 ? (
                  <tr><td colSpan={3} className="px-3 py-4 text-center text-[var(--text-tertiary)]">Нет AI-запусков</td></tr>
                ) : (
                  ai.data?.map((row) => (
                    <tr key={row.task} className="border-t border-[var(--glass-border)]">
                      <td className="px-3 py-2 font-mono text-xs">{row.task}</td>
                      <td className="px-3 py-2">{row.count}</td>
                      <td className="px-3 py-2">
                        {row.avg_latency_ms != null ? Math.round(row.avg_latency_ms) : '—'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Tabs.Content>

        <Tabs.Content value="recruiters" className="mt-3">
          <div className="overflow-auto rounded-md border border-[var(--glass-border)] bg-[var(--surface-solid)] shadow-card">
            <table className="w-full text-sm">
              <thead className="bg-[var(--surface-sunken)] text-left text-xs uppercase tracking-wide text-[var(--text-secondary)]">
                <tr>
                  <th className="px-3 py-2">Рекрутёр</th>
                  <th className="px-3 py-2">Откликов</th>
                </tr>
              </thead>
              <tbody>
                {recruiters.isLoading ? (
                  <tr><td colSpan={2} className="px-3 py-4 text-center text-[var(--text-tertiary)]">Загрузка…</td></tr>
                ) : (recruiters.data?.length ?? 0) === 0 ? (
                  <tr><td colSpan={2} className="px-3 py-4 text-center text-[var(--text-tertiary)]">Нет данных</td></tr>
                ) : (
                  recruiters.data?.map((row, i) => (
                    <tr key={row.recruiter_id ?? i} className="border-t border-[var(--glass-border)]">
                      <td className="px-3 py-2 font-mono text-xs">
                        {row.recruiter_id ?? '—'}
                      </td>
                      <td className="px-3 py-2">{row.count}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Tabs.Content>
      </Tabs.Root>
    </div>
  )
}
