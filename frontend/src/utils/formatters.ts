/**
 * Frontend Utility Helpers
 * ========================
 */

/**
 * Format a decimal number as currency string.
 * TODO: Support locale and currency code from user preferences.
 */
export function formatCurrency(amount: number, currency = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount)
}

/**
 * Format an ISO date string to a human-readable date.
 */
export function formatDate(isoDate: string): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(isoDate))
}

/**
 * Truncate a string to a maximum length with ellipsis.
 */
export function truncate(str: string, maxLength = 50): string {
  return str.length > maxLength ? `${str.substring(0, maxLength)}...` : str
}

/**
 * Map a status string to a Tailwind badge color class.
 * TODO: Extend with all domain-specific status values.
 */
export function getStatusColor(status: string): string {
  const colorMap: Record<string, string> = {
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    pending: 'bg-yellow-100 text-yellow-800',
    draft: 'bg-gray-100 text-gray-800',
    published: 'bg-blue-100 text-blue-800',
    paid: 'bg-emerald-100 text-emerald-800',
    cancelled: 'bg-red-100 text-red-700',
  }
  return colorMap[status] ?? 'bg-gray-100 text-gray-700'
}
