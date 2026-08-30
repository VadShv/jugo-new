import * as React from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import { X } from 'lucide-react'
import { cn } from './cn'

export interface GlassSheetProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title?: React.ReactNode
  children?: React.ReactNode
  className?: string
}

/**
 * Bottom sheet with a drag handle, a scrim overlay and a glass surface.
 * Animates transform/opacity only.
 */
export function GlassSheet({
  open,
  onOpenChange,
  title,
  children,
  className,
}: GlassSheetProps) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-50 bg-[var(--glass-scrim)] data-[state=open]:animate-[fade-in_200ms_ease] data-[state=closed]:animate-[fade-out_200ms_ease]" />
        <Dialog.Content
          className={cn(
            'glass glass--regular fixed inset-x-0 bottom-0 z-50 max-h-[85vh] rounded-t-lg p-4',
            'data-[state=open]:animate-[sheet-up_280ms_var(--ease-spring)]',
            className,
          )}
        >
          <div className="mx-auto mb-3 h-1.5 w-10 rounded-pill bg-[var(--surface-sunken)]" />
          <div className="mb-3 flex items-center justify-between gap-2">
            <Dialog.Title className="min-w-0 flex-1 truncate text-lg font-semibold text-[var(--text-on-glass)]">
              {title}
            </Dialog.Title>
            <Dialog.Close asChild>
              <button
                type="button"
                aria-label="Закрыть"
                className="rounded-pill p-1 text-[var(--text-secondary)] hover:bg-[var(--surface-sunken)]"
              >
                <X size={18} />
              </button>
            </Dialog.Close>
          </div>
          <Dialog.Description className="sr-only">
            Панель деталей
          </Dialog.Description>
          <div className="max-h-[70vh] overflow-y-auto">{children}</div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
