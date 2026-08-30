import { useState } from 'react'
import ReactECharts from 'echarts-for-react'
import type { EChartsOption } from 'echarts'
import * as Tabs from '@radix-ui/react-tabs'
import { GlassTopBar } from '@/shared/ui/GlassTopBar'
import { GlassSegmentedControl } from '@/shared/ui/GlassSegmentedControl'

const PERIODS = [
  { label: 'Неделя', value: 'week' },
  { label: 'Месяц', value: 'month' },
  { label: 'Квартал', value: 'quarter' },
]

const funnelOption: EChartsOption = {
  tooltip: { trigger: 'item' },
  series: [
    {
      type: 'funnel',
      left: '10%',
      width: '80%',
      data: [
        { value: 100, name: 'Отклики' },
        { value: 64, name: 'Скрининг' },
        { value: 38, name: 'Интервью' },
        { value: 21, name: 'Оффер' },
        { value: 17, name: 'Приняты' },
      ],
    },
  ],
}

const sourceOption: EChartsOption = {
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: ['Job boards', 'Реферал', 'LinkedIn', 'Прямо'],
  },
  yAxis: { type: 'value' },
  series: [{ type: 'bar', data: [120, 80, 64, 32] }],
}

export default function AnalyticsPage() {
  const [period, setPeriod] = useState('month')

  return (
    <div className="flex flex-col gap-3">
      <GlassTopBar
        title="Аналитика"
        sticky={false}
        trailing={
          <GlassSegmentedControl
            options={PERIODS}
            value={period}
            onChange={setPeriod}
          />
        }
      />

      <div className="rounded-lg border border-[var(--glass-border)] bg-[var(--surface-solid)] p-4 shadow-card">
        <h2 className="mb-3 text-base font-semibold text-[var(--text-primary)]">
          Воронка найма
        </h2>
        <Tabs.Root defaultValue="funnel">
          <Tabs.List className="mb-3 inline-flex gap-1 rounded-pill bg-[var(--surface-sunken)] p-1">
            <Tabs.Trigger
              value="funnel"
              className="rounded-pill px-3 py-1 text-sm font-medium text-[var(--text-secondary)] data-[state=active]:bg-[var(--surface-solid)] data-[state=active]:text-[var(--text-primary)] data-[state=active]:shadow-card"
            >
              Воронка
            </Tabs.Trigger>
            <Tabs.Trigger
              value="source"
              className="rounded-pill px-3 py-1 text-sm font-medium text-[var(--text-secondary)] data-[state=active]:bg-[var(--surface-solid)] data-[state=active]:text-[var(--text-primary)] data-[state=active]:shadow-card"
            >
              Источники
            </Tabs.Trigger>
          </Tabs.List>
          <Tabs.Content value="funnel">
            <ReactECharts option={funnelOption} style={{ height: 360 }} />
          </Tabs.Content>
          <Tabs.Content value="source">
            <ReactECharts option={sourceOption} style={{ height: 360 }} />
          </Tabs.Content>
        </Tabs.Root>
      </div>
    </div>
  )
}
