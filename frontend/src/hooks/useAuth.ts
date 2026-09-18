'use client'

import { useSession, signOut } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export function useAuth() {
  const { data: session, status } = useSession()
  const router = useRouter()

  const user = session?.user

  const handleSignOut = async () => {
    await signOut({ callbackUrl: '/' })
  }

  return {
    user,
    session,
    status,
    isLoading: status === 'loading',
    isAuthenticated: status === 'authenticated',
    signOut: handleSignOut,
  }
}

export function useRequireAuth() {
  const { isAuthenticated, isLoading, user, signOut } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login')
    }
  }, [isAuthenticated, isLoading, router])

  return { user, isLoading, isAuthenticated, signOut }
}