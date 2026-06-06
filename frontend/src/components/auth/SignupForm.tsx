/**
 * Auth Components — SignupForm
 * TODO: Implement with react-hook-form + zod, role selection.
 */

import { Button, Input } from '../ui'

interface SignupFormProps {
  onSubmit?: (data: object) => void
  isLoading?: boolean
}

export function SignupForm({ onSubmit, isLoading }: SignupFormProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Collect & validate form values, call onSubmit(data)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input label="Full name"       type="text"     placeholder="John Doe"          id="signup-fullname" />
      <Input label="Email address"   type="email"    placeholder="you@company.com"   id="signup-email" />
      <Input label="Password"        type="password" placeholder="Min. 8 characters" id="signup-password" />
      <Input label="Confirm password" type="password" placeholder="Repeat password"  id="signup-confirm" />

      {/* Role selector — TODO: hide/manage programmatically in production */}
      <div className="flex flex-col gap-1">
        <label htmlFor="signup-role" className="text-sm font-medium text-gray-700">Role</label>
        <select id="signup-role" className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="vendor">Vendor</option>
          <option value="procurement_officer">Procurement Officer</option>
          <option value="manager">Manager</option>
          <option value="admin">Admin</option>
        </select>
      </div>

      <Button type="submit" variant="primary" isLoading={isLoading} className="w-full justify-center">
        Create Account
      </Button>

      <p className="text-center text-sm text-gray-500">
        Already have an account?{' '}
        <a href="/login" className="text-blue-600 hover:underline">Sign in</a>
      </p>
    </form>
  )
}
