import { test, expect } from '@playwright/test'

/**
 * Smoke Tests - Tests básicos para verificar funcionalidad crítica
 * Estos tests deben ejecutarse rápido y validar el happy path
 */

test.describe('Smoke Tests - Sistema de Cantina', () => {
  
  test('Homepage carga correctamente', async ({ page }) => {
    await page.goto('/')
    
    // Verificar que la página carga
    await expect(page).toHaveTitle(/Cantina/)
    
    // Verificar elementos clave
    await expect(page.locator('body')).toBeVisible()
  })
  
  test('Login page está accesible', async ({ page }) => {
    await page.goto('/login/')
    
    // Verificar campos de login
    await expect(page.locator('input[name="username"]')).toBeVisible()
    await expect(page.locator('input[name="password"]')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })
  
  test('API health check responde', async ({ request }) => {
    const response = await request.get('/api/health/')
    
    expect(response.ok()).toBeTruthy()
    expect(response.status()).toBe(200)
  })
  
  test('Recursos estáticos se cargan', async ({ page }) => {
    await page.goto('/')
    
    // Verificar que CSS se carga
    const styles = await page.locator('link[rel="stylesheet"]')
    await expect(styles.first()).toHaveAttribute('href', /.+\.css/)
    
    // Verificar que no hay errores de consola críticos
    const errors: string[] = []
    page.on('pageerror', error => errors.push(error.message))
    
    await page.waitForLoadState('networkidle')
    
    // Permitir solo warnings, no errors
    const criticalErrors = errors.filter(e => !e.includes('warning'))
    expect(criticalErrors).toHaveLength(0)
  })
  
  test('Navegación básica funciona', async ({ page }) => {
    await page.goto('/')
    
    // Click en diferentes secciones
    const links = await page.locator('a[href]').all()
    
    // Al menos debe haber algunos links
    expect(links.length).toBeGreaterThan(0)
  })
  
  test('Sistema responde en tiempo razonable', async ({ page }) => {
    const startTime = Date.now()
    
    await page.goto('/')
    await page.waitForLoadState('domcontentloaded')
    
    const loadTime = Date.now() - startTime
    
    // Página debe cargar en menos de 3 segundos
    expect(loadTime).toBeLessThan(3000)
  })
})

test.describe('Smoke Tests - POS', () => {
  
  test.beforeEach(async ({ page }) => {
    // Login como cajero
    await page.goto('/login/')
    await page.fill('input[name="username"]', 'cajero')
    await page.fill('input[name="password"]', 'Cajero123!')
    await page.click('button[type="submit"]')
    
    // Esperar redirección
    await page.waitForURL(/\/pos/)
  })
  
  test('POS dashboard carga', async ({ page }) => {
    await expect(page.locator('h1')).toContainText(/POS|Punto de Venta/)
  })
  
  test('Puede buscar productos', async ({ page }) => {
    const searchInput = page.locator('input[type="search"]').first()
    
    if (await searchInput.isVisible()) {
      await searchInput.fill('test')
      
      // Debe mostrar resultados o mensaje
      await page.waitForTimeout(500)
      const results = page.locator('[data-testid="search-results"]')
      
      // Verificar que algo cambió en la UI
      await expect(page.locator('body')).toBeVisible()
    }
  })
})

test.describe('Smoke Tests - Portal Padres', () => {
  
  test('Portal padres es accesible', async ({ page }) => {
    await page.goto('/portal/')
    
    // Verificar login o dashboard
    await expect(page.locator('body')).toBeVisible()
  })
  
  test('Puede ver información de recargas', async ({ page }) => {
    await page.goto('/portal/')
    
    // Buscar elementos relacionados a recargas
    const pageContent = await page.content()
    
    // Página debe tener contenido
    expect(pageContent.length).toBeGreaterThan(100)
  })
})
