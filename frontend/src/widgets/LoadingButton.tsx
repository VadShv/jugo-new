import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { Loader2 } from 'lucide-react'
import { cn } from '@/shared/ui/cn'

export interface LoadingButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean
  children: ReactNode
}

/** Button with a spinner when loading. Replaces inline disabled+text pattern. */
export function LoadingButton({
  loading,
  children,
  className,
  disabled,
  ...props
}: LoadingButtonProps) {
  return (
    <button
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-pill px-4 py-2 text-sm font-medium transition-opacity hover:opacity-90 disabled:opacity-50',
        className,
      )}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Loader2 size={16} className="animate-spin" />}
      {children}
    </button>
  )
}
