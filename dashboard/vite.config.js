import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        // Must match `uvicorn ... --port` (8000 is common; 8765 if 8000 is blocked on Windows)
        target: 'http://127.0.0.1:8765',
        changeOrigin: true,
      },
    },
  },
})
