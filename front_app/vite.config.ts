import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    hmr: {
      overlay: false,
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
      },
    },
  },
  // 🔥 Correction : Supprimer logOverride qui n'existe pas
  build: {
    rollupOptions: {
      onwarn(warning, warn) {
        // Ignorer les warnings de variables non utilisées
        if (warning.code === 'UNUSED_EXTERNAL_IMPORT') return
        if (warning.message?.includes('is declared but its value is never read')) return
        if (warning.message?.includes('is assigned a value but never used')) return
        warn(warning)
      }
    }
  }
})
