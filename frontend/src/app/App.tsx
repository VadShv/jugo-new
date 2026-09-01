import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider } from '@tanstack/react-router'
import { router } from './router'
import { ToasterProvider } from '@/widgets/Toaster'
import { ErrorBoundary } from '@/widgets/ErrorBoundary'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <ToasterProvider>
          <RouterProvider router={router} />
        </ToasterProvider>
      </ErrorBoundary>
    </QueryClientProvider>
  )
}
