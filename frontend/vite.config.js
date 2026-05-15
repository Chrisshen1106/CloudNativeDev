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
      '/api': 'http://localhost:8001',
      '/maintenance-api': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/maintenance-api/, '/api')
      },
      '/user-api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: path => path.replace(/^\/user-api/, '/api')
      }
    }
  }
})