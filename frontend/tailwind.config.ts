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
        accent: {
          blue: 'var(--accent-blue)',
          green: 'var(--accent-green)',
          orange: 'var(--accent-orange)',
          red: 'var(--accent-red)',
          purple: 'var(--accent-purple)',
          teal: 'var(--accent-teal)',
        },
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
