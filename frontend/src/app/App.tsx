import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider } from '@tanstack/react-router'
import * as Toast from '@radix-ui/react-toast'
import { router } from './router'

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
      <Toast.Provider swipeDirection="right" duration={4000}>
        <RouterProvider router={router} />
        <Toast.Viewport className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2" />
      </Toast.Provider>
    </QueryClientProvider>
  )
}
