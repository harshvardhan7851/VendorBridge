/**
 * Notifications — NotificationList
 */

import type { Notification } from '../../../types'
import { NotificationItem } from './NotificationItem'
import { EmptyState, Button } from '../ui'

interface NotificationListProps {
  notifications?: Notification[]
  isLoading?: boolean
  onMarkRead?: (id: string) => void
  onMarkAllRead?: () => void
}

export function NotificationList({ notifications = [], isLoading, onMarkRead, onMarkAllRead }: NotificationListProps) {
  const unreadCount = notifications.filter((n) => !n.is_read).length

  return (
    <div>
      {/* Header row */}
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-gray-700">
          Notifications {unreadCount > 0 && <span className="ml-1 text-blue-600">({unreadCount} unread)</span>}
        </h2>
        {unreadCount > 0 && (
          <Button size="sm" variant="ghost" onClick={onMarkAllRead}>
            Mark all as read
          </Button>
        )}
      </div>

      {/* List */}
      {isLoading ? (
        <p className="text-sm text-gray-400 py-8 text-center">Loading notifications...</p>
      ) : notifications.length === 0 ? (
        <EmptyState title="No notifications" description="You're all caught up!" />
      ) : (
        <div className="space-y-1">
          {notifications.map((n) => (
            <NotificationItem key={n.id} notification={n} onMarkRead={onMarkRead} />
          ))}
        </div>
      )}
    </div>
  )
}
