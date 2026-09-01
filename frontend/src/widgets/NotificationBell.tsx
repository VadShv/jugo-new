import { useEffect, useRef, useState } from 'react'
import { Bell } from 'lucide-react'

interface EventItem {
  id: string
  type: string
  payload: Record<string, unknown>
  timestamp: string
}

const EVENT_TYPES = [
  'application.stage.changed',
  'screening.completed',
  'risk.analysis.completed',
  'questions.generated',
  'searchmap.generated',
  'interview.scheduled',
  'interview.completed',
  'interview.canceled',
]

const EVENT_LABELS: Record<string, string> = {
  'application.stage.changed': 'Переход по воронке',
  'screening.completed': 'Скрининг завершён',
  'risk.analysis.completed': 'Анализ рисков завершён',
  'questions.generated': 'Вопросы сгенерированы',
  'searchmap.generated': 'Карта поиска готова',
  'interview.scheduled': 'Интервью назначено',
  'interview.completed': 'Интервью завершено',
  'interview.canceled': 'Интервью отменено',
}

export function NotificationBell() {
  const [events, setEvents] = useState<EventItem[]>([])
  const [open, setOpen] = useState(false)
  const esRef = useRef<EventSource | null>(null)

  useEffect(() => {
    const token = localStorage.getItem('ats.token')
    if (!token) return

    const es = new EventSource(`/api/v1/events/stream?token=${token}`)
    esRef.current = es

    const handler = (e: MessageEvent) => {
      try {
        const payload = JSON.parse(e.data)
        setEvents((prev) =>
          [
            {
              id: crypto.randomUUID(),
              type: e.type,
              payload,
              timestamp: new Date().toISOString(),
            },
            ...prev,
          ].slice(0, 20),
        )
      } catch {
        /* ignore parse errors */
      }
    }

    EVENT_TYPES.forEach((type) => es.addEventListener(type, handler))

    return () => {
      es.close()
      esRef.current = null
    }
  }, [])

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-label="Уведомления"
        className="relative inline-flex items-center justify-center rounded-pill px-2.5 py-1.5 text-[var(--text-secondary)] hover:bg-[var(--surface-sunken)]"
      >
        <Bell size={16} />
        {events.length > 0 && (
          <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-[var(--accent-red)] px-1 text-[10px] font-medium text-white">
            {events.length > 9 ? '9+' : events.length}
          </span>
        )}
      </button>

      {open && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setOpen(false)}
          />
          <div className="glass glass--regular absolute right-0 top-full z-50 mt-2 max-h-96 w-80 overflow-y-auto rounded-lg p-2 shadow-glass">
            {events.length === 0 ? (
              <p className="px-2 py-4 text-center text-sm text-[var(--text-tertiary)]">
                Нет уведомлений
              </p>
            ) : (
              <ul className="flex flex-col gap-1">
                {events.map((e) => (
                  <li
                    key={e.id}
                    className="rounded-md border border-[var(--glass-border)] bg-[var(--surface-sunken)] p-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-[var(--text-primary)]">
                        {EVENT_LABELS[e.type] ?? e.type}
                      </span>
                      <span className="text-caption text-[var(--text-tertiary)]">
                        {new Date(e.timestamp).toLocaleTimeString('ru-RU', {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </>
      )}
    </div>
  )
}
