/**
 * StatusBadge Component — Placeholder
 * TODO: Implement a colored badge for entity statuses.
 */

import { getStatusColor } from '../utils/formatters'

interface StatusBadgeProps {
  status: string
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const colorClass = getStatusColor(status)
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>
      {status.replace(/_/g, ' ')}
    </span>
  )
}
