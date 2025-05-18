import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// Read API target from environment variable or use localhost as default
const API_TARGET = process.env.VITE_API_TARGET || 'http://localhost:8080'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    proxy: {
      // Proxy API requests to your backend server
      '/api': {
        target: API_TARGET, // Use environment variable or default
        changeOrigin: true,
        secure: false, // Set to true if using HTTPS and self-signed certs
      },
    },
  },
})
