import {
  createRootRoute,
  createRoute,
  createRouter,
  redirect,
} from '@tanstack/react-router'
import { Layout } from './Layout'
import { isAuthenticated } from '@/shared/api/auth'
import VacanciesPage from '../pages/VacanciesPage'
import VacancyDetailPage from '../pages/VacancyDetailPage'
import CandidatesPage from '../pages/CandidatesPage'
import CandidateDetailPage from '../pages/CandidateDetailPage'
import ApplicationsPage from '../pages/ApplicationsPage'
import ApplicationDetailPage from '../pages/ApplicationDetailPage'
import AnalyticsPage from '../pages/AnalyticsPage'
import LoginPage from '../pages/LoginPage'
import DashboardPage from '../pages/DashboardPage'

const rootRoute = createRootRoute({})

const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/login',
  component: LoginPage,
  beforeLoad: () => {
    if (isAuthenticated()) throw redirect({ to: '/' })
  },
})

const protectedRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: '_protected',
  component: Layout,
  beforeLoad: () => {
    if (!isAuthenticated()) throw redirect({ to: '/login' })
  },
})

const dashboardRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/',
  component: DashboardPage,
})

const vacanciesRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/vacancies',
  component: VacanciesPage,
})

const vacancyDetailRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/vacancies/$vacancyId',
  component: VacancyDetailPage,
})

const candidatesRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/candidates',
  component: CandidatesPage,
})

const candidateDetailRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/candidates/$candidateId',
  component: CandidateDetailPage,
})

const applicationsRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/applications',
  component: ApplicationsPage,
})

const applicationDetailRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/applications/$applicationId',
  component: ApplicationDetailPage,
})

const analyticsRoute = createRoute({
  getParentRoute: () => protectedRoute,
  path: '/analytics',
  component: AnalyticsPage,
})

const routeTree = rootRoute.addChildren([
  loginRoute,
  protectedRoute.addChildren([
    dashboardRoute,
    vacanciesRoute,
    vacancyDetailRoute,
    candidatesRoute,
    candidateDetailRoute,
    applicationsRoute,
    applicationDetailRoute,
    analyticsRoute,
  ]),
])

export const router = createRouter({ routeTree })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
