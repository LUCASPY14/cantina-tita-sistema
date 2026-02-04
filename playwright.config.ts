import { defineConfig, devices } from '@playwright/test'

/**
 * Configuración de Playwright para tests E2E
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  // Directorio de tests
  testDir: './e2e',
  
  // Tests en paralelo por archivo
  fullyParallel: true,
  
  // Fallar build si quedaron test.only
  forbidOnly: !!process.env.CI,
  
  // Reintentos en CI
  retries: process.env.CI ? 2 : 0,
  
  // Workers (en paralelo)
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter
  reporter: [
    ['html'],
    ['list'],
    ['junit', { outputFile: 'playwright-report/results.xml' }]
  ],
  
  // Configuración compartida para todos los tests
  use: {
    // Base URL para tests
    baseURL: 'http://localhost:8000',
    
    // Trace en retry
    trace: 'on-first-retry',
    
    // Screenshot en fallo
    screenshot: 'only-on-failure',
    
    // Video en fallo
    video: 'retain-on-failure',
    
    // Timeout de acción
    actionTimeout: 10000,
    
    // Ignorar HTTPS errors
    ignoreHTTPSErrors: true,
  },

  // Configurar proyectos para cada navegador
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    // Tests mobile
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // Servidor web local para tests
  webServer: {
    command: 'python backend/manage.py runserver',
    url: 'http://localhost:8000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
  
  // Timeouts
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  
  // Output directory
  outputDir: 'test-results/',
})
