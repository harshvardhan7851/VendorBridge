/**
 * Role Protected Route
 * ====================
 * Redirects users who don't have the required role to /unauthorized.
 * Must be nested inside a <ProtectedRoute> (authentication already checked).
 *
 * Usage:
 *   <Route element={<RoleProtectedRoute allowedRoles={['admin', 'manager']} />}>
 *     <Route path="/approvals" element={<ApprovalsPage />} />
 *   </Route>
 *
 * Roles:
 *   admin | procurement_officer | vendor | manager
 *
 * TODO: Replace placeholder with real role check using useAuth()
 */

import { Navigate, Outlet } from 'react-router-dom'
import type { UserRole } from '../types'
// import { useAuth } from '../contexts/AuthContext'

interface RoleProtectedRouteProps {
  allowedRoles: UserRole[]
}

export function RoleProtectedRoute({ allowedRoles }: RoleProtectedRouteProps) {
  // TODO: Replace with real user from AuthContext
  // const { user } = useAuth()
  const user = null  // PLACEHOLDER

  if (!user) {
    return <Navigate to="/login" replace />
  }

  // TODO: Check user.role against allowedRoles
  // const hasPermission = allowedRoles.includes(user.role)
  const hasPermission = false  // PLACEHOLDER

  if (!hasPermission) {
    return <Navigate to="/unauthorized" replace />
  }

  return <Outlet />
}
