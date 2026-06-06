import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  resolve: {
    alias: {
      // Allows "@/components/..." imports throughout the app
      '@': path.resolve(__dirname, './src'),
    },
  },

  server: {
    // Required for Docker — allows Vite to accept connections from outside container
    host: '0.0.0.0',
    port: 5173,

    // Proxy API requests to the FastAPI backend service
    // The backend container is accessible at http://backend:8000 inside Docker network
    proxy: {
      '/api': {
        target: 'http://backend:8000',
        changeOrigin: true,
        // TODO: Enable rewrite if API path structure changes
        // rewrite: (path) => path.replace(/^\/api/, '')
      },
    },
  },
})
