import { useQuery } from '@tanstack/react-query'
import { useUiStore } from '@/app/store'
import { fetchVacancies } from '@/entities/vacancy/api'
import { fieldClass } from '@/shared/ui/field'

/** Vacancy selector dropdown — sets the global vacancy context (Zustand). */
export function VacancySelector() {
  const { data } = useQuery({
    queryKey: ['vacancies-select'],
    queryFn: ({ signal }) => fetchVacancies({ signal }),
  })
  const selectedVacancyId = useUiStore((s) => s.selectedVacancyId)
  const setSelectedVacancy = useUiStore((s) => s.setSelectedVacancy)
  const clearSelectedVacancy = useUiStore((s) => s.clearSelectedVacancy)

  return (
    <select
      value={selectedVacancyId ?? ''}
      onChange={(e) => {
        const v = data?.items.find((item) => item.id === e.target.value)
        if (v) {
          setSelectedVacancy(v.id, v.title)
        } else {
          clearSelectedVacancy()
        }
      }}
      className={`${fieldClass} w-auto`}
    >
      <option value="">Все вакансии</option>
      {(data?.items ?? []).map((v) => (
        <option key={v.id} value={v.id}>
          {v.title}
        </option>
      ))}
    </select>
  )
}
