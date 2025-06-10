import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    host: '0.0.0.0',  // Bind to all network interfaces for mobile access
    proxy: {
      // Mobile API routing: /api/* requests get proxied to backend
      '/api': {
        target: 'http://192.168.86.148:3001',  // Auto-detected local IP for mobile devices
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
