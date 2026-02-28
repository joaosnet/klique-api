import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'favicon.svg', 'robots.txt', 'icons/*.png'],
      manifest: {
        name: 'Game Theory Platform',
        short_name: 'GameTheory',
        description: 'Simulador Universal de Teoria dos Jogos',
        theme_color: '#12121a',
        background_color: '#12121a',
        display: 'standalone',
        start_url: '/',
        icons: [
          { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any maskable' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
      },
    }),
  ],
  server: {
    host: '0.0.0.0',
    port: 3000,
    // Allow HMR to work inside Docker — the browser connects to the host machine
    hmr: {
      clientPort: 3000,
    },
    proxy: {
      '/api': { target: process.env.VITE_BACKEND_URL || 'http://fastapi-klique:8000', changeOrigin: true },
      '/token': { target: process.env.VITE_BACKEND_URL || 'http://fastapi-klique:8000', changeOrigin: true },
      '/auth': { target: process.env.VITE_BACKEND_URL || 'http://fastapi-klique:8000', changeOrigin: true },
      '/users': { target: process.env.VITE_BACKEND_URL || 'http://fastapi-klique:8000', changeOrigin: true },
    },
  },
})
