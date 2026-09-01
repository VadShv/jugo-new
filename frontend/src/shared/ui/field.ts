/** Shared form field styles for consistent, polished inputs across the app. */
export const fieldClass =
  'w-full rounded-lg border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 text-sm text-[var(--text-primary)] outline-none transition-colors focus:border-[var(--accent-blue)] focus:ring-2 focus:ring-[var(--accent-blue)]/30 placeholder:text-[var(--text-tertiary)] disabled:opacity-50'

export const fieldLabelClass =
  'text-sm font-medium text-[var(--text-secondary)]'

export const fieldErrorClass =
  'text-xs text-[var(--accent-red)]'

export const buttonPrimaryClass =
  'inline-flex items-center justify-center gap-2 rounded-pill bg-[var(--accent-blue)] px-4 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50'

export const buttonGhostClass =
  'inline-flex items-center justify-center gap-2 rounded-pill border border-[var(--glass-border)] bg-[var(--surface-solid)] px-3 py-2 text-sm font-medium text-[var(--text-secondary)] transition-colors hover:bg-[var(--surface-sunken)]'
