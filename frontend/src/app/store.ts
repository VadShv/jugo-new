import { create } from 'zustand'

export type DrawerKind = 'candidate' | 'vacancy' | 'application'

export interface ActiveDrawer {
  kind: DrawerKind
  id: string
}

export interface UiState {
  activeDrawer: ActiveDrawer | null
  openDrawer: (drawer: ActiveDrawer) => void
  closeDrawer: () => void
  savedView: string | null
  setSavedView: (view: string | null) => void
}

export const useUiStore = create<UiState>((set) => ({
  activeDrawer: null,
  openDrawer: (drawer) => set({ activeDrawer: drawer }),
  closeDrawer: () => set({ activeDrawer: null }),
  savedView: null,
  setSavedView: (view) => set({ savedView: view }),
}))
