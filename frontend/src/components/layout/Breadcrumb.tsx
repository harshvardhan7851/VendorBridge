/**
 * Breadcrumb — Page navigation trail
 * TODO: Auto-generate from React Router location.
 */

import { Link } from 'react-router-dom'

interface BreadcrumbItem {
  label: string
  path?: string  // If undefined, renders as current (non-linked)
}

interface BreadcrumbProps {
  items: BreadcrumbItem[]
}

export function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <nav aria-label="Breadcrumb">
      <ol className="flex items-center gap-1 text-sm text-gray-500">
        {items.map((item, index) => (
          <li key={index} className="flex items-center gap-1">
            {index > 0 && <span className="text-gray-300">/</span>}
            {item.path ? (
              <Link to={item.path} className="hover:text-gray-800 transition-colors">
                {item.label}
              </Link>
            ) : (
              <span className="text-gray-800 font-medium">{item.label}</span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  )
}
