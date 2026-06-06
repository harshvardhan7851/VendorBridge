/**
 * Signup Page
 * Composes: AuthLayout (from layouts/) + SignupForm (from components/auth/)
 */

import { SignupForm } from '../../components/auth'

export function SignupPage() {
  const handleSignup = async (data: object) => {
    // TODO: Call authApi.signup(data), redirect to /login with success message
    console.log('Signup:', data)
  }

  return <SignupForm onSubmit={handleSignup} />
}
