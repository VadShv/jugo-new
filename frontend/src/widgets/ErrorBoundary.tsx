import { Component, type ErrorInfo, type ReactNode } from 'react'
import { AlertTriangle } from 'lucide-react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

/** Graceful error page instead of a white screen on unhandled React errors. */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-[var(--surface-canvas)] px-4 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-full bg-[var(--surface-sunken)]">
            <AlertTriangle size={28} className="text-[var(--accent-orange)]" />
          </div>
          <div>
            <p className="text-lg font-semibold text-[var(--text-primary)]">
              Что-то пошло не так
            </p>
            <p className="mt-1 text-sm text-[var(--text-secondary)]">
              Произошла неожиданная ошибка. Попробуйте перезагрузить страницу.
            </p>
          </div>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="rounded-pill bg-[var(--accent-blue)] px-4 py-2 text-sm font-medium text-white"
          >
            Перезагрузить
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
