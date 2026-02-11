/// <reference types="vitest" />
import { defineConfig } from 'vite'
import path from 'path'

export default defineConfig({
  test: {
    // Configuración de entorno
    globals: true,
    environment: 'jsdom',
    
    // Setup files
    setupFiles: ['./src/tests/setup.ts'],
    
    // Coverage
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      reportsDirectory: './coverage',
      exclude: [
        'node_modules/',
        'src/tests/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData/',
        'dist/',
      ],
      statements: 70,
      branches: 70,
      functions: 70,
      lines: 70,
    },
    
    // Paths
    include: ['src/**/*.{test,spec}.{js,ts}'],
    exclude: [
      'node_modules',
      'dist',
      '.idea',
      '.git',
      '.cache'
    ],
    
    // Timeouts
    testTimeout: 10000,
    hookTimeout: 10000,
    
    // Reporters
    reporters: ['verbose'],
    
    // Watch mode
    watch: false,
    
    // Threads
    threads: true,
    maxThreads: 4,
    minThreads: 1,
  },
  
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@services': path.resolve(__dirname, './src/services'),
      '@stores': path.resolve(__dirname, './src/stores'),
    }
  }
})
