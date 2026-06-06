/**
 * Protected Route
 * ===============
 * Redirects unauthenticated users to /login.
 * Wrap any route that requires authentication.
 *
 * Usage:
 *   <Route element={<ProtectedRoute />}>
 *     <Route path="/dashboard" element={<DashboardPage />} />
 *   </Route>
 *
 * TODO: Replace placeholder with real auth check using useAuth()
 */

import { Navigate, Outlet, useLocation } from 'react-router-dom'
// import { useAuth } from '../contexts/AuthContext'

export function ProtectedRoute() {
  const location = useLocation()

  // TODO: Replace with real auth check
  // const { isAuthenticated, isLoading } = useAuth()
  const isAuthenticated = false  // PLACEHOLDER — always false until implemented
  const isLoading = false        // PLACEHOLDER

  if (isLoading) {
    // TODO: Return a proper loading spinner component
    return <div>Loading...</div>
  }

  if (!isAuthenticated) {
    // Redirect to login, preserving the originally requested URL
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Render the child routes
  return <Outlet />
}
