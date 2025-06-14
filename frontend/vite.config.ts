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
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:3001',
        changeOrigin: true,
        secure: false,
        ws: true // Enable WebSocket proxying
      }
    }
  },
  preview: {
    port: 4173,
    host: '0.0.0.0',
    allowedHosts: ['codenames.up.railway.app']
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          socket: ['socket.io-client']
        }
      }
    }
  },
  // Ensure environment variables are available in production
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL || 'https://backend-production-8bea.up.railway.app'),
    'import.meta.env.VITE_WS_URL': JSON.stringify(process.env.VITE_WS_URL || 'https://backend-production-8bea.up.railway.app'),
    'import.meta.env.VITE_NODE_ENV': JSON.stringify(process.env.VITE_NODE_ENV || 'production'),
    'import.meta.env.VITE_SOCKET_URL': JSON.stringify(process.env.VITE_WS_URL || 'https://backend-production-8bea.up.railway.app')
  }
})
