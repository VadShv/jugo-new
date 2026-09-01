import * as AlertDialog from '@radix-ui/react-alert-dialog'

export interface ConfirmDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description?: string
  confirmLabel?: string
  cancelLabel?: string
  onConfirm: () => void
  destructive?: boolean
}

/** Radix AlertDialog for destructive/important confirmations. */
export function ConfirmDialog({
  open,
  onOpenChange,
  title,
  description,
  confirmLabel = 'Подтвердить',
  cancelLabel = 'Отмена',
  onConfirm,
  destructive,
}: ConfirmDialogProps) {
  return (
    <AlertDialog.Root open={open} onOpenChange={onOpenChange}>
      <AlertDialog.Portal>
        <AlertDialog.Overlay className="fixed inset-0 z-50 bg-[var(--glass-scrim)] data-[state=open]:animate-[fade-in_200ms_ease]" />
        <AlertDialog.Content className="glass glass--regular fixed left-1/2 top-1/2 z-50 w-full max-w-sm -translate-x-1/2 -translate-y-1/2 rounded-lg p-5 shadow-glass">
          <AlertDialog.Title className="text-sm font-semibold text-[var(--text-primary)]">
            {title}
          </AlertDialog.Title>
          {description && (
            <AlertDialog.Description className="mt-1 text-xs text-[var(--text-secondary)]">
              {description}
            </AlertDialog.Description>
          )}
          <div className="mt-4 flex justify-end gap-2">
            <AlertDialog.Cancel asChild>
              <button className="rounded-pill border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-1.5 text-sm text-[var(--text-secondary)]">
                {cancelLabel}
              </button>
            </AlertDialog.Cancel>
            <AlertDialog.Action asChild>
              <button
                onClick={onConfirm}
                className={`rounded-pill px-3 py-1.5 text-sm font-medium text-white ${
                  destructive ? 'bg-[var(--accent-red)]' : 'bg-[var(--accent-blue)]'
                }`}
              >
                {confirmLabel}
              </button>
            </AlertDialog.Action>
          </div>
        </AlertDialog.Content>
      </AlertDialog.Portal>
    </AlertDialog.Root>
  )
}
