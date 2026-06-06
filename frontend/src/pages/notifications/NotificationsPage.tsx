/**
 * Notifications Page
 */

import { NotificationList } from '../../components/notifications'
import { PageHeader } from '../../components/ui'

export function NotificationsPage() {
  return (
    <div>
      <PageHeader
        title="Notifications"
        description="Your activity feed and alerts"
      />
      <NotificationList
        notifications={[]}
        // TODO: onMarkRead, onMarkAllRead — wire to notificationsApi
      />
    </div>
  )
}
