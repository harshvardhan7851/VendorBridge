/**
 * 404 Not Found Page
 */
import { Link } from 'react-router-dom'
import { Button } from '../../components/ui'

export function NotFoundPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center px-4">
      <div className="text-8xl font-black text-gray-200 select-none">404</div>
      <h1 className="text-2xl font-bold text-gray-800 mt-4">Page not found</h1>
      <p className="text-gray-500 mt-2 max-w-sm">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <Link to="/dashboard" className="mt-6">
        <Button variant="primary">← Back to Dashboard</Button>
      </Link>
    </div>
  )
}
