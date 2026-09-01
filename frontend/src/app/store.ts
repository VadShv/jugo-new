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
  selectedVacancyId: string | null
  selectedVacancyTitle: string | null
  setSelectedVacancy: (id: string, title: string) => void
  clearSelectedVacancy: () => void
}

export const useUiStore = create<UiState>((set) => ({
  activeDrawer: null,
  openDrawer: (drawer) => set({ activeDrawer: drawer }),
  closeDrawer: () => set({ activeDrawer: null }),
  savedView: null,
  setSavedView: (view) => set({ savedView: view }),
  selectedVacancyId: null,
  selectedVacancyTitle: null,
  setSelectedVacancy: (id, title) =>
    set({ selectedVacancyId: id, selectedVacancyTitle: title }),
  clearSelectedVacancy: () =>
    set({ selectedVacancyId: null, selectedVacancyTitle: null }),
}))
