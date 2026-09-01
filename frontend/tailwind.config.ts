import type { Config } from 'tailwindcss'

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        canvas: 'var(--surface-canvas)',
        solid: 'var(--surface-solid)',
        sunken: 'var(--surface-sunken)',
        elevated: 'var(--surface-elevated)',
        accent: {
          blue: 'var(--accent-blue)',
          green: 'var(--accent-green)',
          orange: 'var(--accent-orange)',
          red: 'var(--accent-red)',
          purple: 'var(--accent-purple)',
          teal: 'var(--accent-teal)',
        },
      },
      fontSize: {
        display: ['1.875rem', { lineHeight: '1.2' }],
        lg: ['1.125rem', { lineHeight: '1.4' }],
        base: ['0.875rem', { lineHeight: '1.5' }],
        sm: ['0.75rem', { lineHeight: '1.4' }],
        caption: ['0.6875rem', { lineHeight: '1.3' }],
      },
      borderRadius: {
        xs: 'var(--radius-xs)',
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
        pill: 'var(--radius-pill)',
      },
      boxShadow: {
        glass: 'var(--shadow-glass)',
        card: 'var(--shadow-card)',
        elevated: 'var(--shadow-elevated)',
        modal: 'var(--shadow-modal)',
      },
      backgroundImage: {
        'glass-highlight':
          'linear-gradient(180deg, var(--glass-highlight) 0%, transparent 50%)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config
