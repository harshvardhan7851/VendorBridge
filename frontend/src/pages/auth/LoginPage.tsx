/**
 * Login Page
 * Composes: AuthLayout (from layouts/) + LoginForm (from components/auth/)
 */

import { LoginForm } from '../../components/auth'

export function LoginPage() {
  const handleLogin = async (email: string, password: string) => {
    // TODO: Call useAuth().login(email, password), redirect to /dashboard on success
    console.log('Login:', email, password)
  }

  return <LoginForm onSubmit={handleLogin} />
}
