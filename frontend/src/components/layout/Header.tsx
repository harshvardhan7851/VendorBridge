/**
 * Header — Top application bar
 * TODO: Implement notification bell counter, user avatar dropdown, search bar.
 */

import { Link } from 'react-router-dom'
// import { useAuth } from '../../hooks/useAuth'

export function Header() {
  // TODO: const { user, logout } = useAuth()

  return (
    <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 shrink-0">
      {/* Left: Page breadcrumb area (populated by each page) */}
      <div className="text-sm text-gray-500">
        {/* TODO: Breadcrumb component */}
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-4">

        {/* Notification Bell */}
        <Link
          to="/notifications"
          className="relative text-gray-500 hover:text-gray-800 transition-colors"
          aria-label="Notifications"
        >
          🔔
          {/* TODO: Unread count badge */}
          {/* <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-red-500 text-white text-[10px] flex items-center justify-center">3</span> */}
        </Link>

        {/* User Avatar / Menu */}
        <div className="flex items-center gap-2 cursor-pointer group">
          {/* TODO: Replace with real user avatar */}
          <div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-semibold">
            U
          </div>
          <div className="hidden sm:block text-left">
            {/* TODO: Render user.full_name and user.role */}
            <p className="text-sm font-medium text-gray-800">User Name</p>
            <p className="text-xs text-gray-500 capitalize">role</p>
          </div>
          {/* TODO: Dropdown menu with Profile / Settings / Logout */}
        </div>
      </div>
    </header>
  )
}
