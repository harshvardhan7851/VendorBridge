/**
 * Badge — Status/label badge component
 * Replaces the old StatusBadge.tsx at components/StatusBadge.tsx
 */

import { getStatusColor } from '../../utils/formatters'

interface BadgeProps {
  label: string
  /** If true, uses the status-color map from formatters; otherwise renders in gray */
  isStatus?: boolean
  className?: string
}

export function Badge({ label, isStatus = false, className = '' }: BadgeProps) {
  const colorClass = isStatus ? getStatusColor(label) : 'bg-gray-100 text-gray-700'
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${colorClass} ${className}`}
    >
      {label.replace(/_/g, ' ')}
    </span>
  )
}

/** Convenience wrapper — status-colored badge */
export function StatusBadge({ status }: { status: string }) {
  return <Badge label={status} isStatus />
}
