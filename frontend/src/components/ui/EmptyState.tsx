/**
 * EmptyState — Empty list/no-data fallback
 * Replaces the old EmptyState.tsx at components/EmptyState.tsx
 */

import { Button } from './Button'

interface EmptyStateProps {
  title?: string
  description?: string
  /** Optional label for an action CTA button */
  actionLabel?: string
  onAction?: () => void
  /** TODO: Add an illustration/icon prop */
}

export function EmptyState({
  title = 'No data found',
  description = 'Nothing to display here yet.',
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center gap-3">
      {/* TODO: Replace with an SVG illustration */}
      <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center text-3xl">
        📭
      </div>
      <h3 className="text-base font-semibold text-gray-900">{title}</h3>
      <p className="text-sm text-gray-500 max-w-xs">{description}</p>
      {actionLabel && onAction && (
        <Button size="sm" onClick={onAction}>{actionLabel}</Button>
      )}
    </div>
  )
}
