/**
 * Sidebar — Main navigation sidebar
 * TODO: Implement active link highlighting, collapsible nav groups,
 *       role-based link visibility, collapse toggle.
 */

import { NavLink } from 'react-router-dom'

interface NavItem {
  label: string
  path: string
  icon: string        // TODO: Replace with SVG icon component
  roles?: string[]    // If set, only visible to these roles
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard',       path: '/dashboard',        icon: '🏠' },
  { label: 'Vendors',         path: '/vendors',           icon: '🏢' },
  { label: 'RFQs',            path: '/rfqs',              icon: '📋' },
  { label: 'Quotations',      path: '/quotations',        icon: '💬' },
  { label: 'Approvals',       path: '/approvals',         icon: '✅', roles: ['admin', 'manager'] },
  { label: 'Purchase Orders', path: '/purchase-orders',   icon: '📦' },
  { label: 'Invoices',        path: '/invoices',          icon: '🧾' },
  { label: 'Reports',         path: '/reports',           icon: '📊', roles: ['admin'] },
  { label: 'Notifications',   path: '/notifications',     icon: '🔔' },
]

export function Sidebar() {
  return (
    <aside className="w-64 h-full bg-gray-900 flex flex-col shrink-0">
      {/* Brand / Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-gray-700">
        {/* TODO: Replace with VendorBridge SVG logo */}
        <span className="text-2xl">🌉</span>
        <span className="text-lg font-bold text-white tracking-tight">VendorBridge</span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              }`
            }
          >
            <span className="text-base">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Footer — User info */}
      <div className="px-4 py-4 border-t border-gray-700">
        {/* TODO: Render current user avatar + name + logout button */}
        <div className="text-xs text-gray-500 text-center">VendorBridge ERP v0.1.0</div>
      </div>
    </aside>
  )
}
