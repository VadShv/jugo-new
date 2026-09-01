import { createContext, useContext, useState, type ReactNode } from 'react'
import * as Toast from '@radix-ui/react-toast'
import { AlertCircle, CheckCircle, Info } from 'lucide-react'

type ToastType = 'success' | 'error' | 'info'

interface ToastData {
  id: string
  type: ToastType
  title: string
  description?: string
}

const ToastContext = createContext<{
  toast: (type: ToastType, title: string, description?: string) => void
}>({ toast: () => {} })

export const useToast = () => useContext(ToastContext)

const ICONS: Record<ToastType, typeof CheckCircle> = {
  success: CheckCircle,
  error: AlertCircle,
  info: Info,
}

const COLORS: Record<ToastType, string> = {
  success: 'var(--accent-green)',
  error: 'var(--accent-red)',
  info: 'var(--accent-blue)',
}

export function ToasterProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastData[]>([])

  const toast = (type: ToastType, title: string, description?: string) => {
    const id = crypto.randomUUID()
    setToasts((t) => [...t, { id, type, title, description }])
    window.setTimeout(
      () => setToasts((t) => t.filter((x) => x.id !== id)),
      4000,
    )
  }

  return (
    <ToastContext.Provider value={{ toast }}>
      <Toast.Provider swipeDirection="right">
        {children}
        {toasts.map((t) => {
          const Icon = ICONS[t.type]
          return (
            <Toast.Root
              key={t.id}
              className="glass glass--regular rounded-lg p-3 shadow-glass data-[state=open]:animate-[fade-in_200ms_ease]"
            >
              <div className="flex items-start gap-2">
                <Icon
                  size={18}
                  style={{ color: COLORS[t.type] }}
                  className="mt-0.5 shrink-0"
                />
                <div className="flex flex-col">
                  <Toast.Title className="text-sm font-medium text-[var(--text-primary)]">
                    {t.title}
                  </Toast.Title>
                  {t.description && (
                    <Toast.Description className="text-xs text-[var(--text-secondary)]">
                      {t.description}
                    </Toast.Description>
                  )}
                </div>
              </div>
            </Toast.Root>
          )
        })}
        <Toast.Viewport className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2" />
      </Toast.Provider>
    </ToastContext.Provider>
  )
}
