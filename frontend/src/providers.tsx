"use client"

import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { useState } from "react"
import { Toaster } from "react-hot-toast"

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            refetchOnWindowFocus: false,
            retry: 1,
          },
        },
      })
  )

  return (
    <QueryClientProvider client={queryClient}>
      <Toaster 
        position="top-right" 
        toastOptions={{
          style: {
            background: 'var(--glass-bg)',
            color: 'var(--foreground)',
            backdropFilter: 'blur(16px)',
            border: '1px solid var(--border)',
            borderRadius: '1rem',
            padding: '16px',
            fontSize: '14px',
            boxShadow: '0 10px 40px rgba(0,0,0,0.2)'
          },
          success: {
            iconTheme: { primary: 'var(--color-wa-green)', secondary: '#fff' }
          },
          error: {
            iconTheme: { primary: 'var(--color-wa-rose)', secondary: '#fff' }
          }
        }} 
      />
      {children}
    </QueryClientProvider>
  )
}
