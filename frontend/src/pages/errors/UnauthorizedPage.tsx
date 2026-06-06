/**
 * 403 Unauthorized Page
 */
import { Link } from 'react-router-dom'
import { Button } from '../../components/ui'

export function UnauthorizedPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center px-4">
      <div className="text-8xl font-black text-red-100 select-none">403</div>
      <h1 className="text-2xl font-bold text-gray-800 mt-4">Access Denied</h1>
      <p className="text-gray-500 mt-2 max-w-sm">
        You don't have permission to view this page. Contact your administrator.
      </p>
      <Link to="/dashboard" className="mt-6">
        <Button variant="secondary">← Back to Dashboard</Button>
      </Link>
    </div>
  )
}
