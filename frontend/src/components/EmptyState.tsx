/**
 * EmptyState Component — Placeholder
 * TODO: Add illustration/icon, improved typography.
 */
interface EmptyStateProps {
  title?: string
  description?: string
}

export function EmptyState({
  title = 'No data found',
  description = 'There are no items to display at this time.',
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {/* TODO: Add empty state illustration */}
      <h3 className="text-lg font-medium text-gray-900">{title}</h3>
      <p className="mt-1 text-sm text-gray-500">{description}</p>
    </div>
  )
}
