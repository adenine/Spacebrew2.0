import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/app/',
  server: {
    proxy: {
      '/api': 'http://localhost:8088',
      '/ws': {
        target: 'ws://localhost:8088',
        ws: true,
      },
    },
  },
})
