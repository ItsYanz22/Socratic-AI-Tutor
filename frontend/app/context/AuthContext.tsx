'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { supabase } from '@/lib/supabaseClient'
import { Session } from '@supabase/supabase-js'

// Define the shape of our context
interface AuthContextType {
  session: Session | null
  accessToken: string | null
}

// Create the context
const AuthContext = createContext<AuthContextType | undefined>(undefined)

// Create the "Provider" component
export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null)
  const [accessToken, setAccessToken] = useState<string | null>(null)

  useEffect(() => {
    // 1. Get the initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setAccessToken(session?.access_token ?? null)
    })

    // 2. Listen for changes in auth state (login, logout)
    const { data: authListener } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session)
        setAccessToken(session?.access_token ?? null)
        console.log('Auth state changed, new token:', session?.access_token)
      }
    )

    // Cleanup listener on unmount
    return () => {
      authListener?.subscription.unsubscribe()
    }
  }, [])

  const value = {
    session,
    accessToken,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// Create a "hook" to easily use the context
export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}