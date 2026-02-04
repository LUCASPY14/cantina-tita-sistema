import { test, expect } from '@playwright/test'

/**
 * Tests E2E de Autenticación
 * Valida login, logout, permisos y sesiones
 */

test.describe('Autenticación', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/login/')
  })
  
  test('Login exitoso con credenciales válidas', async ({ page }) => {
    // Llenar formulario
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'Admin123!')
    
    // Submit
    await page.click('button[type="submit"]')
    
    // Verificar redirección a dashboard
    await page.waitForURL(/\/(dashboard|home)/)
    
    // Verificar que estamos autenticados
    await expect(page.locator('body')).not.toContainText(/Iniciar sesión/i)
  })
  
  test('Login falla con credenciales inválidas', async ({ page }) => {
    // Intentar login con credenciales incorrectas
    await page.fill('input[name="username"]', 'invalid')
    await page.fill('input[name="password"]', 'wrong')
    await page.click('button[type="submit"]')
    
    // Debe mostrar error
    await expect(page.locator('.alert-error, .error, [role="alert"]')).toBeVisible()
    
    // Debe permanecer en login
    await expect(page).toHaveURL(/login/)
  })
  
  test('Campos vacíos muestran validación', async ({ page }) => {
    // Intentar submit sin llenar
    await page.click('button[type="submit"]')
    
    // Validación HTML5 o error visible
    const usernameInput = page.locator('input[name="username"]')
    const isInvalid = await usernameInput.evaluate((el: HTMLInputElement) => !el.validity.valid)
    
    expect(isInvalid).toBeTruthy()
  })
  
  test('Logout funciona correctamente', async ({ page }) => {
    // Login primero
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'Admin123!')
    await page.click('button[type="submit"]')
    await page.waitForURL(/\/(dashboard|home)/)
    
    // Hacer logout
    const logoutButton = page.locator('a[href*="logout"], button:has-text("Salir")')
    await logoutButton.click()
    
    // Verificar redirección a login
    await page.waitForURL(/login/)
    await expect(page.locator('input[name="username"]')).toBeVisible()
  })
  
  test('Sesión persiste después de refresh', async ({ page }) => {
    // Login
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'Admin123!')
    await page.click('button[type="submit"]')
    await page.waitForURL(/\/(dashboard|home)/)
    
    // Refresh página
    await page.reload()
    
    // Debe seguir autenticado
    await expect(page).not.toHaveURL(/login/)
  })
  
  test('Redirige a login si no está autenticado', async ({ page }) => {
    // Intentar acceder a página protegida
    await page.goto('/dashboard/')
    
    // Debe redirigir a login
    await page.waitForURL(/login/)
    await expect(page.locator('input[name="username"]')).toBeVisible()
  })
})

test.describe('Permisos y Roles', () => {
  
  test('Admin puede acceder a todas las secciones', async ({ page }) => {
    // Login como admin
    await page.goto('/login/')
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'Admin123!')
    await page.click('button[type="submit"]')
    await page.waitForURL(/\/(dashboard|home)/)
    
    // Verificar acceso a diferentes secciones
    const sections = ['/dashboard/', '/productos/', '/ventas/']
    
    for (const section of sections) {
      await page.goto(section)
      
      // No debe redirigir a error o login
      await expect(page).not.toHaveURL(/login|403|404/)
    }
  })
  
  test('Usuario limitado no accede a admin', async ({ page, context }) => {
    // Si existe usuario con permisos limitados
    await page.goto('/login/')
    await page.fill('input[name="username"]', 'cajero')
    await page.fill('input[name="password"]', 'Cajero123!')
    await page.click('button[type="submit"]')
    
    // Intentar acceder a admin
    const response = await page.goto('/admin/')
    
    // Debe denegar acceso (403 o redirect)
    if (response) {
      expect([403, 302, 404]).toContain(response.status())
    }
  })
})
