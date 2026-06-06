/**
 * Auth API
 * =========
 * Placeholder functions for authentication endpoints.
 * TODO: Implement each function with actual API calls.
 */

import apiClient from './client'
import type { LoginRequest, SignupRequest, TokenResponse, User } from '../types'

export const authApi = {
  /** POST /auth/login — Authenticate user, returns JWT */
  login: async (credentials: LoginRequest): Promise<TokenResponse> => {
    // TODO: const { data } = await apiClient.post('/auth/login', credentials)
    // TODO: return data
    throw new Error('Not implemented')
  },

  /** POST /auth/signup — Register new user */
  signup: async (payload: SignupRequest): Promise<User> => {
    // TODO: const { data } = await apiClient.post('/auth/signup', payload)
    // TODO: return data
    throw new Error('Not implemented')
  },

  /** POST /auth/forgot-password — Request password reset email */
  forgotPassword: async (email: string): Promise<void> => {
    // TODO: await apiClient.post('/auth/forgot-password', { email })
    throw new Error('Not implemented')
  },

  /** GET /auth/me — Get current authenticated user */
  getMe: async (): Promise<User> => {
    // TODO: const { data } = await apiClient.get('/auth/me')
    // TODO: return data
    throw new Error('Not implemented')
  },
}
