'use client' // This tells Next.js it's a client-side component

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { supabase } from '@/lib/supabaseClient' // <-- Import your Supabase client
import { useRouter } from 'next/navigation' // <-- 1. IMPORT THE ROUTER

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const router = useRouter() // <-- 2. INITIALIZE THE ROUTER

  // --- THIS IS THE FINALIZED FUNCTION ---
  const handleLogin = async () => {
    try {
      // 1. Call the Supabase auth function
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email,
        password: password,
      })

      // 2. Handle any errors
      if (error) {
        console.error('Error logging in:', error.message)
        alert(`Error: ${error.message}`) // Show error to the user
        return
      }

      // 3. Handle success
      console.log('Login successful!', data)

      // 4. REDIRECT TO THE DASHBOARD
      // Our AuthProvider (in layout.tsx) will automatically
      // detect this new session.
      router.push('/dashboard/gym')

    } catch (error) {
      console.error('Unexpected error:', error)
      alert('An unexpected error occurred.')
    }
  }
  // --- END OF FINALIZED FUNCTION ---

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <div className="w-full max-w-md p-8 space-y-6">
        <h1 className="text-3xl font-bold text-center">Login to Sahayogi</h1>
        <div className="space-y-4">
          <div>
            <label htmlFor="email">Email</label>
            <Input
              id="email"
              type="email"
              placeholder="test@test.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label htmlFor="password">Password</label>
            <Input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <Button onClick={handleLogin} className="w-full">
            Login
          </Button>
        </div>
      </div>
    </div>
  )
}