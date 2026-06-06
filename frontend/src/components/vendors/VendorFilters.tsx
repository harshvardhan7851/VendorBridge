/**
 * Vendors — VendorFilters
 * TODO: Connect filter state to parent page via props/URL query params.
 */

import { Input } from '../ui'

interface VendorFiltersProps {
  onSearch?: (query: string) => void
  onStatusChange?: (status: string) => void
  onCategoryChange?: (category: string) => void
}

export function VendorFilters({ onSearch, onStatusChange, onCategoryChange }: VendorFiltersProps) {
  return (
    <div className="flex flex-wrap gap-3 mb-4">
      <div className="flex-1 min-w-[200px]">
        <Input
          placeholder="Search vendors..."
          id="vendor-search"
          onChange={(e) => onSearch?.(e.target.value)}
        />
      </div>

      <select
        className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        onChange={(e) => onStatusChange?.(e.target.value)}
        defaultValue=""
      >
        <option value="">All Statuses</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="rejected">Rejected</option>
        <option value="suspended">Suspended</option>
      </select>

      <select
        className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        onChange={(e) => onCategoryChange?.(e.target.value)}
        defaultValue=""
      >
        <option value="">All Categories</option>
        <option value="IT">IT</option>
        <option value="Logistics">Logistics</option>
        <option value="Office Supplies">Office Supplies</option>
        <option value="Manufacturing">Manufacturing</option>
        {/* TODO: Load categories dynamically from API */}
      </select>
    </div>
  )
}
