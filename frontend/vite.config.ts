import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // ASTRO_API lets the dev server point at a backend on another port
      // when :8000 is taken (e.g. ASTRO_API=http://127.0.0.1:8001 npm run dev)
      '/api': process.env.ASTRO_API ?? 'http://127.0.0.1:8000',
    },
  },
})
