import type { ReactNode } from 'react'
import * as Tabs from '@radix-ui/react-tabs'

export interface DetailTab {
  value: string
  label: string
  content: ReactNode
}

export interface DetailLayoutProps {
  title: ReactNode
  meta?: ReactNode
  actions?: ReactNode
  tabs: DetailTab[]
  defaultTab?: string
}

/**
 * Reusable detail page shell: a header (title + meta + actions) over a glass
 * tab bar, with opaque content per tab. Used by candidate/vacancy/application
 * detail pages.
 */
export function DetailLayout({
  title,
  meta,
  actions,
  tabs,
  defaultTab,
}: DetailLayoutProps) {
  return (
    <div className="flex flex-col gap-4">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex flex-col gap-1">
          <h1 className="text-xl font-semibold text-[var(--text-primary)]">{title}</h1>
          {meta && (
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-[var(--text-secondary)]">
              {meta}
            </div>
          )}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </header>

      <Tabs.Root defaultValue={defaultTab ?? tabs[0]?.value}>
        <Tabs.List className="glass glass--regular inline-flex gap-1 rounded-pill p-1">
          {tabs.map((tab) => (
            <Tabs.Trigger
              key={tab.value}
              value={tab.value}
              className="rounded-pill px-3 py-1.5 text-sm font-medium text-[var(--text-secondary)] outline-none data-[state=active]:bg-[var(--surface-solid)] data-[state=active]:text-[var(--text-primary)] data-[state=active]:shadow-card"
            >
              {tab.label}
            </Tabs.Trigger>
          ))}
        </Tabs.List>
        {tabs.map((tab) => (
          <Tabs.Content
            key={tab.value}
            value={tab.value}
            className="mt-3 data-[state=active]:animate-[fade-in_200ms_ease]"
          >
            {tab.content}
          </Tabs.Content>
        ))}
      </Tabs.Root>
    </div>
  )
}
