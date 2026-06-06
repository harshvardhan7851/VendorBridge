/**
 * Auth Layout
 * ============
 * Centered card layout for public pages: Login, Signup, Forgot Password.
 */

import { Outlet } from 'react-router-dom'

export function AuthLayout() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="w-full max-w-md">
        {/* Brand */}
        <div className="text-center mb-8">
          <span className="text-5xl">🌉</span>
          <h1 className="mt-3 text-3xl font-bold text-gray-900 tracking-tight">VendorBridge</h1>
          <p className="text-sm text-gray-500 mt-1">Procurement & Vendor Management ERP</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
