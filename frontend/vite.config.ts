import { defineConfig } from 'vite'
import { resolve } from 'path'
import { fileURLToPath, URL } from 'node:url'
import { viteStaticCopy } from 'vite-plugin-static-copy'

const __dirname = fileURLToPath(new URL('.', import.meta.url))

export default defineConfig({
  // Configuración de entrada
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'src/main.ts'),
        pos: resolve(__dirname, 'src/pos.ts'),
        portal: resolve(__dirname, 'src/portal.ts'),
        admin: resolve(__dirname, 'src/admin.ts'),
        // CSS
        styles: resolve(__dirname, 'src/styles/main.css')
      },
      output: {
        entryFileNames: 'js/[name]-[hash].js',
        chunkFileNames: 'js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const extType = assetInfo.name?.split('.').pop() || ''
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType)) {
            return 'img/[name]-[hash][extname]'
          }
          if (/css/i.test(extType)) {
            return 'css/[name]-[hash][extname]'
          }
          return 'assets/[name]-[hash][extname]'
        }
      }
    },
    // Generar manifest para Django
    manifest: true,
    // Source maps para desarrollo
    sourcemap: true
  },
  
  // Servidor de desarrollo
  server: {
    port: 3000,
    host: '0.0.0.0',
    cors: true,
    // Proxy para API Django
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/admin': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  
  // Plugins
  plugins: [
    viteStaticCopy({
      targets: [
        {
          src: 'static/icons/**/*',
          dest: 'icons'
        },
        {
          src: 'static/sounds/**/*',
          dest: 'sounds'
        },
        {
          src: 'static/manifest.json',
          dest: '.'
        },
        {
          src: 'static/sw.js',
          dest: '.'
        }
      ]
    })
  ],
  
  // Resolución de módulos
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@utils': resolve(__dirname, 'src/utils'),
      '@types': resolve(__dirname, 'src/types'),
      '@styles': resolve(__dirname, 'src/styles')
    }
  },
  
  // Optimizaciones
  define: {
    __VUE_OPTIONS_API__: false,
    __VUE_PROD_DEVTOOLS__: false
  }
})