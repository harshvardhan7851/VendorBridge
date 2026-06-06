/**
 * Application Routes
 * ==================
 * Central route configuration for VendorBridge ERP.
 * All pages are imported from their feature sub-folder under pages/.
 *
 * Route Groups:
 *   Public     : /login, /signup
 *   Protected  : /dashboard, /vendors, /rfqs, /quotations, /approvals,
 *                /purchase-orders, /invoices, /reports, /notifications
 *   Role-gated : /approvals (admin, manager)  /reports (admin)
 */

import { Routes, Route, Navigate } from 'react-router-dom'

// --- Route Guards ---
import { ProtectedRoute }     from './ProtectedRoute'
import { RoleProtectedRoute } from './RoleProtectedRoute'

// --- Layouts ---
import { MainLayout } from '../layouts/MainLayout'
import { AuthLayout } from '../layouts/AuthLayout'

// --- Auth Pages ---
import { LoginPage }  from '../pages/auth/LoginPage'
import { SignupPage } from '../pages/auth/SignupPage'

// --- Feature Pages ---
import { DashboardPage }       from '../pages/dashboard/DashboardPage'
import { VendorsPage }         from '../pages/vendors/VendorsPage'
import { VendorDetailPage }    from '../pages/vendors/VendorDetailPage'
import { RFQsPage }            from '../pages/rfqs/RFQsPage'
import { QuotationsPage }      from '../pages/quotations/QuotationsPage'
import { ApprovalsPage }       from '../pages/approvals/ApprovalsPage'
import { PurchaseOrdersPage }  from '../pages/purchase-orders/PurchaseOrdersPage'
import { InvoicesPage }        from '../pages/invoices/InvoicesPage'
import { ReportsPage }         from '../pages/reports/ReportsPage'
import { NotificationsPage }   from '../pages/notifications/NotificationsPage'

// --- Error Pages ---
import { NotFoundPage }     from '../pages/errors/NotFoundPage'
import { UnauthorizedPage } from '../pages/errors/UnauthorizedPage'

export function AppRoutes() {
  return (
    <Routes>

      {/* ------------------------------------------------------------------ */}
      {/* Public — Auth pages (centered card layout)                          */}
      {/* ------------------------------------------------------------------ */}
      <Route element={<AuthLayout />}>
        <Route path="/login"           element={<LoginPage />} />
        <Route path="/signup"          element={<SignupPage />} />
        {/* TODO: <Route path="/forgot-password" element={<ForgotPasswordPage />} /> */}
      </Route>

      {/* ------------------------------------------------------------------ */}
      {/* Protected — Requires authentication                                 */}
      {/* ------------------------------------------------------------------ */}
      <Route element={<ProtectedRoute />}>
        <Route element={<MainLayout />}>

          {/* Default redirect */}
          <Route index element={<Navigate to="/dashboard" replace />} />

          {/* All authenticated users */}
          <Route path="/dashboard"         element={<DashboardPage />} />
          <Route path="/vendors"           element={<VendorsPage />} />
          <Route path="/vendors/:id"       element={<VendorDetailPage />} />
          <Route path="/rfqs"              element={<RFQsPage />} />
          {/* TODO: <Route path="/rfqs/:id" element={<RFQDetailPage />} /> */}
          <Route path="/quotations"        element={<QuotationsPage />} />
          <Route path="/purchase-orders"   element={<PurchaseOrdersPage />} />
          <Route path="/invoices"          element={<InvoicesPage />} />
          <Route path="/notifications"     element={<NotificationsPage />} />

          {/* Manager + Admin only */}
          <Route element={<RoleProtectedRoute allowedRoles={['admin', 'manager']} />}>
            <Route path="/approvals" element={<ApprovalsPage />} />
          </Route>

          {/* Admin only */}
          <Route element={<RoleProtectedRoute allowedRoles={['admin']} />}>
            <Route path="/reports" element={<ReportsPage />} />
          </Route>

        </Route>
      </Route>

      {/* ------------------------------------------------------------------ */}
      {/* Error Pages                                                         */}
      {/* ------------------------------------------------------------------ */}
      <Route path="/unauthorized" element={<UnauthorizedPage />} />
      <Route path="*"             element={<NotFoundPage />} />

    </Routes>
  )
}
