/**
 * 403 Unauthorized Page — Placeholder
 */
import { Link } from 'react-router-dom'

export function UnauthorizedPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center">
      <h1 className="text-6xl font-bold text-red-200">403</h1>
      <p className="text-xl text-gray-600 mt-4">Access denied</p>
      <p className="text-gray-500 mt-2">You don't have permission to view this page.</p>
      <Link to="/dashboard" className="mt-6 text-blue-600 hover:underline">
        Go to Dashboard
      </Link>
    </div>
  )
}
