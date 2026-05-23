import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      '/api/user': {
        target: 'http://localhost:8001',
        changeOrigin: true
      },
      '/api/maintenance': {
        target: 'http://localhost:8002',
        changeOrigin: true
      },
      '/api/asset': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})