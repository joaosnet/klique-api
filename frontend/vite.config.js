/* global process */
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'
import viteCompression from 'vite-plugin-compression'
import obfuscatorPlugin from 'vite-plugin-javascript-obfuscator'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'favicon.svg', 'robots.txt', 'icons/*.png'],
      manifest: {
        name: 'OmniFlash',
        short_name: 'OmniFlash',
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
    viteCompression({
      algorithm: 'gzip',
      ext: '.gz',
    }),
    viteCompression({
      algorithm: 'brotliCompress',
      ext: '.br',
    }),
    obfuscatorPlugin({
      include: ['src/**/*.js', 'src/**/*.jsx', 'src/**/*.ts', 'src/**/*.tsx'],
      exclude: [/node_modules/],
      apply: 'build', // only during build
      options: {
        compact: true,
        controlFlowFlattening: false,
        deadCodeInjection: false,
        debugProtection: false,
        disableConsoleOutput: true,
        identifierNamesGenerator: 'hexadecimal',
        log: false,
        numbersToExpressions: true,
        renameGlobals: false,
        selfDefending: false,
        simplify: true,
        splitStrings: false,
        stringArray: true,
        stringArrayCallsTransform: true,
        stringArrayEncoding: ['base64'],
        stringArrayIndexShift: true,
        stringArrayRotate: true,
        stringArrayShuffle: true,
        stringArrayWrappersCount: 2,
        stringArrayWrappersChainedCalls: true,
        stringArrayWrappersParametersMaxCount: 2,
        stringArrayWrappersType: 'variable',
        stringArrayThreshold: 0.75,
        transformObjectKeys: false,
        unicodeEscapeSequence: false
      }
    }),
  ],
  build: {
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            return id.toString().split('node_modules/')[1].split('/')[0].toString();
          }
        }
      }
    }
  },
  server: {
    host: '0.0.0.0',
    port: 3000,
    watch: {
      usePolling: true,
      interval: 1000,
    },
    // Allow HMR to work inside Docker — the browser connects to the host machine
    // clientPort: 80 is only needed inside Docker (nginx proxy). Omit it for native dev.
    ...(process.env.VITE_DOCKER ? { hmr: { clientPort: 80 } } : {}),
    proxy: {
      '/api': { target: process.env.VITE_BACKEND_URL || 'http://localhost:8000', changeOrigin: true, secure: false },
      '/token': { target: process.env.VITE_BACKEND_URL || 'http://localhost:8000', changeOrigin: true, secure: false },
      '/auth': { target: process.env.VITE_BACKEND_URL || 'http://localhost:8000', changeOrigin: true, secure: false },
      '/users': { target: process.env.VITE_BACKEND_URL || 'http://localhost:8000', changeOrigin: true, secure: false },
      '/media': { target: process.env.VITE_BACKEND_URL || 'http://localhost:8000', changeOrigin: true, secure: false },
    },
  },
})
