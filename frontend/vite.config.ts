/// <reference types="vitest/config" />
import tailwindcss from '@tailwindcss/vite'
import { tanstackRouter } from '@tanstack/router-plugin/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

const API = 'http://localhost:5000'

export default defineConfig({
  plugins: [tanstackRouter({ target: 'react', autoCodeSplitting: true }), react(), tailwindcss()],
  server: {
    port: 3001,
    strictPort: true,
    proxy: {
      '/api': API,
      '/video': API,
      '/ws': { target: API, ws: true },
    },
  },
  test: { environment: 'node', include: ['src/**/*.test.ts'] },
})
