/**
 * 404 Not Found Page — Placeholder
 */
import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center">
      <h1 className="text-6xl font-bold text-gray-300">404</h1>
      <p className="text-xl text-gray-600 mt-4">Page not found</p>
      <Link to="/dashboard" className="mt-6 text-blue-600 hover:underline">
        Go to Dashboard
      </Link>
    </div>
  )
}
