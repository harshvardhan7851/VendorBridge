/**
 * VendorBridge ERP - Root Application Component
 * ===============================================
 * Assembles the application routing structure.
 * All route definitions are in src/routes/AppRoutes.tsx
 *
 * TODO: Add global error boundary, toast notifications, theme provider
 */

import { AppRoutes } from './routes/AppRoutes'

function App() {
  return <AppRoutes />
}

export default App
