/**
 * Notifications — NotificationItem
 */

import type { Notification } from '../../../types'

interface NotificationItemProps {
  notification: Notification
  onMarkRead?: (id: string) => void
}

export function NotificationItem({ notification, onMarkRead }: NotificationItemProps) {
  return (
    <div
      className={`flex items-start gap-3 p-4 rounded-lg transition-colors cursor-pointer ${
        notification.is_read ? 'bg-white' : 'bg-blue-50 border-l-4 border-blue-500'
      }`}
      onClick={() => !notification.is_read && onMarkRead?.(notification.id)}
    >
      <span className="text-xl mt-0.5">🔔</span>
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-medium ${notification.is_read ? 'text-gray-700' : 'text-gray-900'}`}>
          {notification.title}
        </p>
        <p className="text-xs text-gray-500 mt-0.5 truncate">{notification.message}</p>
      </div>
      {!notification.is_read && (
        <span className="h-2 w-2 rounded-full bg-blue-500 mt-1.5 shrink-0" />
      )}
    </div>
  )
}
