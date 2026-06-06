/**
 * Main Application Layout
 * ========================
 * Shell for all authenticated routes.
 * Composes Sidebar + Header from components/layout/
 */

import { Outlet } from 'react-router-dom'
import { Sidebar } from '../components/layout/Sidebar'
import { Header }  from '../components/layout/Header'

export function MainLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Left: Sidebar nav */}
      <Sidebar />

      {/* Right: Header + scrollable content */}
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
