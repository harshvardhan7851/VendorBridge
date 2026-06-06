/**
 * useLocalStorage Hook
 * ====================
 * Generic hook for reading and writing values to localStorage.
 * Used for persisting auth tokens and user preferences.
 */

import { useState } from 'react'

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = localStorage.getItem(key)
      return item ? (JSON.parse(item) as T) : initialValue
    } catch {
      return initialValue
    }
  })

  const setValue = (value: T) => {
    try {
      setStoredValue(value)
      localStorage.setItem(key, JSON.stringify(value))
    } catch {
      // TODO: Log error to monitoring service
    }
  }

  const removeValue = () => {
    try {
      setStoredValue(initialValue)
      localStorage.removeItem(key)
    } catch {
      // TODO: Log error
    }
  }

  return [storedValue, setValue, removeValue] as const
}
