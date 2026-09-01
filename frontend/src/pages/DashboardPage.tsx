import { useQuery } from '@tanstack/react-query'
import { Link } from '@tanstack/react-router'
import {
  Briefcase,
  ClipboardList,
  TrendingUp,
  Users,
  type LucideIcon,
} from 'lucide-react'
import { Card } from '@/widgets/Card'
import { StatusBadge } from '@/shared/ui/StatusBadge'
import { fetchVacancies } from '@/entities/vacancy/api'
import { fetchCandidates } from '@/entities/candidate/api'
import { fetchApplications } from '@/entities/application/api'

function KpiCard({
  icon: Icon,
  label,
  value,
  to,
}: {
  icon: LucideIcon
  label: string
  value: string
  to: string
}) {
  return (
    <Link to={to}>
      <Card className="transition-shadow hover:shadow-elevated">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-[var(--surface-sunken)]">
            <Icon size={20} className="text-[var(--accent-blue)]" />
          </div>
          <div>
            <div className="text-caption text-[var(--text-tertiary)]">{label}</div>
            <div className="text-display font-semibold text-[var(--text-primary)]">
              {value}
            </div>
          </div>
        </div>
      </Card>
    </Link>
  )
}

export default function DashboardPage() {
  const vacancies = useQuery({
    queryKey: ['vacancies-select'],
    queryFn: ({ signal }) => fetchVacancies({ signal }),
  })
  const candidates = useQuery({
    queryKey: ['candidates-select'],
    queryFn: ({ signal }) => fetchCandidates({ signal }),
  })
  const applications = useQuery({
    queryKey: ['applications-select'],
    queryFn: ({ signal }) => fetchApplications({ signal }),
  })

  const vCount = vacancies.data?.items.length ?? 0
  const cCount = candidates.data?.items.length ?? 0
  const aCount = applications.data?.items.length ?? 0
  const recentApps = (applications.data?.items ?? []).slice(0, 5)

  return (
    <div className="flex flex-col gap-5">
      <div>
        <h1 className="text-display font-semibold text-[var(--text-primary)]">
          Обзор
        </h1>
        <p className="text-sm text-[var(--text-secondary)]">
          Сводка по найму и последняя активность
        </p>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <KpiCard
          icon={Briefcase}
          label="Вакансий"
          value={String(vCount)}
          to="/vacancies"
        />
        <KpiCard
          icon={Users}
          label="Кандидатов"
          value={String(cCount)}
          to="/candidates"
        />
        <KpiCard
          icon={ClipboardList}
          label="Откликов"
          value={String(aCount)}
          to="/applications"
        />
      </div>

      {recentApps.length > 0 && (
        <Card header={<span className="text-sm font-semibold">Последние отклики</span>}>
          <ul className="flex flex-col gap-2">
            {recentApps.map((app) => (
              <li
                key={app.id}
                className="flex items-center justify-between rounded-md border border-[var(--glass-border)] bg-[var(--surface-sunken)] p-3"
              >
                <div className="flex flex-col">
                  <span className="font-mono text-xs text-[var(--text-secondary)]">
                    {app.candidate_id.slice(0, 8)} → {app.vacancy_id.slice(0, 8)}
                  </span>
                  <span className="text-caption text-[var(--text-tertiary)]">
                    {app.updated_at ?? '—'}
                  </span>
                </div>
                <StatusBadge status={app.status} />
              </li>
            ))}
          </ul>
        </Card>
      )}

      {recentApps.length === 0 && !applications.isLoading && (
        <Card>
          <div className="flex flex-col items-center gap-2 py-8 text-center">
            <TrendingUp size={32} className="text-[var(--text-tertiary)]" />
            <p className="text-sm text-[var(--text-secondary)]">
              Пока нет откликов. Создайте вакансию и кандидата, чтобы начать.
            </p>
            <Link
              to="/vacancies"
              className="rounded-pill bg-[var(--accent-blue)] px-4 py-2 text-sm font-medium text-white"
            >
              К вакансиям
            </Link>
          </div>
        </Card>
      )}
    </div>
  )
}
