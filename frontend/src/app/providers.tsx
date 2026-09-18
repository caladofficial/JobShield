'use client'

import { SessionProvider } from 'next-auth/react'
import { Toaster } from 'react-hot-toast'
import { ReactNode } from 'react'

export function Providers({ children }: { children: ReactNode }) {
  return (
    <SessionProvider>
      {children}
      <Toaster
        position="bottom-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#1B1E22',
            color: '#F2F2F2',
            border: '1px solid #2A2E35',
            borderRadius: '1rem',
            padding: '1rem',
          },
          success: {
            iconTheme: {
              primary: '#A8FF60',
              secondary: '#0E0F11',
            },
          },
          error: {
            iconTheme: {
              primary: '#EF4444',
              secondary: '#0E0F11',
            },
          },
        }}
      />
    </SessionProvider>
  )
}

