/**
 * Notification Context
 * ====================
 * Provides global notification state and toast helpers.
 * TODO: Implement with a toast library (e.g., react-hot-toast or sonner).
 */

import { createContext, useContext, ReactNode } from 'react'

interface NotificationContextType {
  /** TODO: Show a success toast */
  success: (message: string) => void
  /** TODO: Show an error toast */
  error: (message: string) => void
  /** TODO: Show an info toast */
  info: (message: string) => void
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined)

export function NotificationProvider({ children }: { children: ReactNode }) {
  const success = (_message: string) => {
    // TODO: trigger toast.success(message)
    console.log('[Toast Success]', _message)
  }

  const error = (_message: string) => {
    // TODO: trigger toast.error(message)
    console.error('[Toast Error]', _message)
  }

  const info = (_message: string) => {
    // TODO: trigger toast(message)
    console.info('[Toast Info]', _message)
  }

  return (
    <NotificationContext.Provider value={{ success, error, info }}>
      {children}
    </NotificationContext.Provider>
  )
}

export function useNotification() {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error('useNotification must be used within a <NotificationProvider>')
  }
  return context
}
