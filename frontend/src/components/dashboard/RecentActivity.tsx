/**
 * Dashboard — RecentActivity
 * TODO: Fetch from ActivityLog API endpoint.
 */

import { Card, CardHeader, EmptyState } from '../ui'

interface ActivityItem {
  id: string
  action: string
  description: string
  timestamp: string
  icon?: string
}

interface RecentActivityProps {
  items?: ActivityItem[]
  isLoading?: boolean
}

export function RecentActivity({ items = [], isLoading }: RecentActivityProps) {
  return (
    <Card>
      <CardHeader title="Recent Activity" description="Latest procurement events" />
      {isLoading ? (
        <p className="text-sm text-gray-400 py-4">Loading activity...</p>
      ) : items.length === 0 ? (
        <EmptyState title="No recent activity" description="Activity will appear here as actions are taken." />
      ) : (
        <ul className="space-y-3">
          {items.map((item) => (
            <li key={item.id} className="flex items-start gap-3">
              <span className="text-lg mt-0.5">{item.icon ?? '📌'}</span>
              <div>
                <p className="text-sm font-medium text-gray-800">{item.action}</p>
                <p className="text-xs text-gray-500">{item.description}</p>
                <p className="text-xs text-gray-400 mt-0.5">{item.timestamp}</p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </Card>
  )
}
