/**
 * Auth Components — LoginForm
 * TODO: Implement controlled form with react-hook-form + zod validation.
 */

import { Button, Input } from '../ui'

interface LoginFormProps {
  onSubmit?: (email: string, password: string) => void
  isLoading?: boolean
}

export function LoginForm({ onSubmit, isLoading }: LoginFormProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Read form values, call onSubmit(email, password)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Email address"
        type="email"
        placeholder="you@company.com"
        required
        autoComplete="email"
        id="login-email"
      />
      <Input
        label="Password"
        type="password"
        placeholder="••••••••"
        required
        autoComplete="current-password"
        id="login-password"
      />

      <div className="flex items-center justify-between text-sm">
        <label className="flex items-center gap-2 text-gray-600 cursor-pointer">
          <input type="checkbox" className="rounded" /> Remember me
        </label>
        {/* TODO: Link to /forgot-password */}
        <a href="/forgot-password" className="text-blue-600 hover:underline">
          Forgot password?
        </a>
      </div>

      <Button type="submit" variant="primary" isLoading={isLoading} className="w-full justify-center">
        Sign In
      </Button>

      <p className="text-center text-sm text-gray-500">
        Don't have an account?{' '}
        <a href="/signup" className="text-blue-600 hover:underline">
          Sign up
        </a>
      </p>
    </form>
  )
}
