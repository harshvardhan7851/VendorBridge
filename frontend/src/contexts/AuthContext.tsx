/**
 * Auth Context
 * ============
 * Provides authentication state (current user, token) to the entire app.
 * TODO: Implement login/logout/refresh logic.
 */

import { createContext, useContext, useState, ReactNode } from 'react'
import type { User } from '../types'

// ---------------------------------------------------------------------------
// Context Shape
// ---------------------------------------------------------------------------

interface AuthContextType {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  /** TODO: Implement — call authApi.login, store token, set user */
  login: (email: string, password: string) => Promise<void>
  /** TODO: Implement — clear token and user state */
  logout: () => void
}

// ---------------------------------------------------------------------------
// Context Creation
// ---------------------------------------------------------------------------

const AuthContext = createContext<AuthContextType | undefined>(undefined)

// ---------------------------------------------------------------------------
// Provider
// ---------------------------------------------------------------------------

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const login = async (_email: string, _password: string) => {
    // TODO: Call authApi.login(), store token in localStorage, set user state
    throw new Error('AuthContext.login not implemented')
  }

  const logout = () => {
    // TODO: Clear localStorage, reset user/token state, redirect to /login
    setUser(null)
    setToken(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user && !!token,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an <AuthProvider>')
  }
  return context
}
