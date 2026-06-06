/**
 * VendorBridge ERP - React Entry Point
 * =====================================
 * Sets up:
 *   - React Query client and provider
 *   - React Router (BrowserRouter)
 *   - Root App component
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import App from './App'
import './index.css'

// ---------------------------------------------------------------------------
// React Query Client Configuration
// ---------------------------------------------------------------------------
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // TODO: Tune staleTime, cacheTime for production
      staleTime: 1000 * 60 * 5,  // 5 minutes
      retry: 1,
    },
  },
})

// ---------------------------------------------------------------------------
// Root Render
// ---------------------------------------------------------------------------
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
      {/* Remove in production */}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </React.StrictMode>,
)
