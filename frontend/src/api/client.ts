/**
 * Axios API Client
 * ================
 * Base Axios instance with interceptors for auth token injection.
 * All API modules import from this file.
 */

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// ---------------------------------------------------------------------------
// Request Interceptor — inject JWT token
// ---------------------------------------------------------------------------
apiClient.interceptors.request.use(
  (config) => {
    // TODO: Get token from AuthContext or localStorage
    // const token = localStorage.getItem('access_token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
    return config
  },
  (error) => Promise.reject(error)
)

// ---------------------------------------------------------------------------
// Response Interceptor — handle 401 (token expiry)
// ---------------------------------------------------------------------------
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // TODO: If 401, clear token and redirect to /login
    // if (error.response?.status === 401) {
    //   localStorage.removeItem('access_token')
    //   window.location.href = '/login'
    // }
    return Promise.reject(error)
  }
)

export default apiClient
