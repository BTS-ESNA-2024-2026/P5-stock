import { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react'
import type { ReactNode } from 'react'
import type { AuthContextType } from './types'
import type { CurrentUser } from '../types'
import { authFetch, ApiError, setUnauthorizedHandler } from '../api/client'

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null)
  const [loading, setLoading] = useState(true)
  const [sessionExpired, setSessionExpired] = useState(false)
  // Avoid stacking redirects when several requests fail simultaneously.
  const handlingExpiry = useRef(false)

  const refresh = useCallback(async () => {
    try {
      const data = await authFetch<CurrentUser>('/me')
      setUser(data)
      setSessionExpired(false)
    } catch {
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  useEffect(() => {
    setUnauthorizedHandler(() => {
      if (handlingExpiry.current) return
      handlingExpiry.current = true
      setUser(null)
      setSessionExpired(true)
      // Bounce to login on the next tick, leaving any in-flight UI a chance to
      // show its own error toast first.
      window.setTimeout(() => {
        if (window.location.pathname !== '/login') {
          window.location.assign('/login?session=expired')
        }
        handlingExpiry.current = false
      }, 0)
    })
    return () => setUnauthorizedHandler(null)
  }, [])

  const login = async (username: string, password: string, otpCode?: string) => {
    const body = new URLSearchParams({ username, password })
    if (otpCode) body.append('otp_code', otpCode)
    const res = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' },
      credentials: 'include',
      body,
    })

    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new ApiError(res.status, data.message ?? 'Connexion echouee')
    }

    setSessionExpired(false)
    await refresh()
  }

  const logout = async () => {
    try {
      await authFetch('/logout', { method: 'POST' })
    } catch {
      // ignore
    }
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, sessionExpired, login, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextType {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
