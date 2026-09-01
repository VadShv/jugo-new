import { useEffect, useState } from 'react'

const KEY = 'jugo.theme'

/** Dark/light theme toggle persisted to localStorage; toggles `.dark` on <html>. */
export function useTheme() {
  const [dark, setDark] = useState<boolean>(() => {
    try {
      return localStorage.getItem(KEY) === 'dark'
    } catch {
      return false
    }
  })

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    try {
      localStorage.setItem(KEY, dark ? 'dark' : 'light')
    } catch {
      /* ignore */
    }
  }, [dark])

  return { dark, toggle: () => setDark((d) => !d) }
}
