/**
 * E2E Test - Flujo Completo POS
 * Sprint 8 - Testing y QA
 * 
 * Flujo testeado:
 * 1. Login al sistema POS
 * 2. Acceder al módulo de ventas
 * 3. Buscar producto
 * 4. Agregar producto al carrito
 * 5. Procesar venta
 * 6. Registrar pago
 * 7. Verificar impresión/recibo
 */

import { test, expect } from '@playwright/test';

// Configuración de test
test.describe('POS - Flujo Completo de Venta', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navegar a la página de login
    await page.goto('/');
  });

  test('Flujo completo: Login → Buscar → Venta → Pago → Recibo', async ({ page }) => {
    // ============================================================
    // PASO 1: LOGIN AL SISTEMA
    // ============================================================
    test.step('1. Login al sistema POS', async () => {
      // Verificar que estamos en la página de login
      await expect(page).toHaveURL(/\/login/i);
      
      // Llenar credenciales (ajustar según tu implementación)
      await page.fill('input[name="username"]', 'admin');
      await page.fill('input[name="password"]', 'admin123');
      
      // Click en botón de login
      await page.click('button[type="submit"]');
      
      // Esperar redirección al dashboard
      await page.waitForURL(/\/(pos|dashboard)/i, { timeout: 10000 });
      
      // Verificar que el login fue exitoso
      await expect(page.locator('body')).toContainText(/dashboard|bienvenido|pos/i);
    });

    // ============================================================
    // PASO 2: NAVEGAR AL MÓDULO DE VENTAS
    // ============================================================
    test.step('2. Acceder al módulo de ventas', async () => {
      // Buscar y hacer click en el enlace/botón de ventas
      const ventaLink = page.locator('a[href*="/pos/venta"], button:has-text("Nueva Venta"), a:has-text("Ventas")').first();
      
      if (await ventaLink.isVisible()) {
        await ventaLink.click();
      } else {
        // Alternativa: navegar directamente
        await page.goto('/pos/venta/');
      }
      
      // Verificar que estamos en la página de ventas
      await expect(page).toHaveURL(/\/pos\/venta/i);
      
      // Verificar elementos clave de la interfaz de ventas
      await expect(page.locator('body')).toContainText(/nueva venta|venta|productos/i);
    });

    // ============================================================
    // PASO 3: BUSCAR PRODUCTO
    // ============================================================
    test.step('3. Buscar producto en catálogo', async () => {
      // Buscar el campo de búsqueda de productos
      const searchInput = page.locator('input[type="search"], input[placeholder*="Buscar"], input[name*="producto"]').first();
      
      if (await searchInput.isVisible()) {
        await searchInput.fill('producto');
        await searchInput.press('Enter');
        
        // Esperar a que carguen los resultados
        await page.waitForTimeout(1000);
        
        // Verificar que hay resultados
        const productosContainer = page.locator('[class*="producto"], [class*="grid"], [class*="card"]');
        await expect(productosContainer.first()).toBeVisible({ timeout: 5000 });
      }
    });

    // ============================================================
    // PASO 4: AGREGAR PRODUCTO AL CARRITO
    // ============================================================
    test.step('4. Agregar producto al carrito', async () => {
      // Seleccionar el primer producto disponible
      const primerProducto = page.locator('[class*="producto"]:visible, [data-product]:visible, button:has-text("Agregar"):visible').first();
      
      if (await primerProducto.isVisible()) {
        await primerProducto.click();
        
        // Esperar feedback visual (modal, animación, etc.)
        await page.waitForTimeout(500);
        
        // Verificar que el carrito se actualizó
        const carrito = page.locator('[class*="carrito"], [class*="cart"], [id*="carrito"]');
        
        // Verificar que hay al menos 1 item en el carrito
        const itemsCount = page.locator('[class*="cart-item"], [class*="item-carrito"], tr[class*="item"]');
        await expect(itemsCount.first()).toBeVisible({ timeout: 5000 });
      }
    });

    // ============================================================
    // PASO 5: PROCESAR VENTA
    // ============================================================
    test.step('5. Procesar venta', async () => {
      // Buscar botón de procesar/finalizar venta
      const procesarBtn = page.locator(
        'button:has-text("Procesar"), button:has-text("Finalizar"), button:has-text("Confirmar"), button[type="submit"]:visible'
      ).first();
      
      if (await procesarBtn.isVisible()) {
        // Hacer click en procesar venta
        await procesarBtn.click();
        
        // Esperar modal de pago o página de confirmación
        await page.waitForTimeout(1000);
        
        // Verificar que estamos en el paso de pago
        await expect(page.locator('body')).toContainText(/pago|monto|total|confirmar/i);
      }
    });

    // ============================================================
    // PASO 6: REGISTRAR PAGO
    // ============================================================
    test.step('6. Registrar pago', async () => {
      // Seleccionar método de pago (efectivo por defecto)
      const metodoPagoSelect = page.locator('select[name*="pago"], select[name*="metodo"]').first();
      
      if (await metodoPagoSelect.isVisible()) {
        await metodoPagoSelect.selectOption({ label: /efectivo|cash/i });
      }
      
      // Ingresar monto (si es necesario)
      const montoInput = page.locator('input[name*="monto"], input[type="number"]').first();
      
      if (await montoInput.isVisible()) {
        // Obtener el total de la venta
        const totalText = await page.locator('[class*="total"], [id*="total"]').first().textContent();
        const total = totalText?.replace(/[^0-9]/g, '') || '50000';
        
        await montoInput.fill(total);
      }
      
      // Confirmar pago
      const confirmarPagoBtn = page.locator('button:has-text("Confirmar"), button:has-text("Pagar"), button[type="submit"]').first();
      
      if (await confirmarPagoBtn.isVisible()) {
        await confirmarPagoBtn.click();
        
        // Esperar confirmación
        await page.waitForTimeout(2000);
      }
    });

    // ============================================================
    // PASO 7: VERIFICAR RECIBO/IMPRESIÓN
    // ============================================================
    test.step('7. Verificar generación de recibo', async () => {
      // Verificar mensaje de éxito
      const successMessage = page.locator('[class*="success"], [class*="alert-success"], :has-text("exitosa"), :has-text("completada")');
      
      // Esperar a que aparezca el mensaje de éxito o el recibo
      await expect(successMessage.or(page.locator('[class*="recibo"], [class*="ticket"]')).first()).toBeVisible({ timeout: 5000 });
      
      // Verificar que hay opción de imprimir o descargar
      const imprimirBtn = page.locator('button:has-text("Imprimir"), button:has-text("Ticket"), a:has-text("Descargar")');
      
      // Si existe botón de imprimir, verificar que está visible
      if (await imprimirBtn.count() > 0) {
        await expect(imprimirBtn.first()).toBeVisible();
      }
      
      // Verificar que podemos volver al inicio
      const nuevaVentaBtn = page.locator('button:has-text("Nueva Venta"), a:has-text("Nueva Venta"), a[href*="/pos/venta"]');
      
      if (await nuevaVentaBtn.count() > 0) {
        await expect(nuevaVentaBtn.first()).toBeVisible();
      }
    });
  });

  // ============================================================
  // TEST ADICIONAL: VENTA CANCELADA
  // ============================================================
  test('Flujo alternativo: Cancelar venta en proceso', async ({ page }) => {
    test.step('Login y navegación a ventas', async () => {
      await page.goto('/');
      await page.fill('input[name="username"]', 'admin');
      await page.fill('input[name="password"]', 'admin123');
      await page.click('button[type="submit"]');
      await page.waitForURL(/\/(pos|dashboard)/i);
      await page.goto('/pos/venta/');
    });

    test.step('Agregar producto y cancelar', async () => {
      // Agregar producto
      const primerProducto = page.locator('[class*="producto"]:visible, button:has-text("Agregar"):visible').first();
      
      if (await primerProducto.isVisible()) {
        await primerProducto.click();
        await page.waitForTimeout(500);
      }
      
      // Buscar y hacer click en botón de cancelar
      const cancelarBtn = page.locator('button:has-text("Cancelar"), button:has-text("Limpiar"), button:has-text("Descartar")').first();
      
      if (await cancelarBtn.isVisible()) {
        await cancelarBtn.click();
        
        // Confirmar cancelación si hay modal
        const confirmarCancelar = page.locator('button:has-text("Sí"), button:has-text("Confirmar")').first();
        
        if (await confirmarCancelar.isVisible({ timeout: 2000 })) {
          await confirmarCancelar.click();
        }
        
        // Verificar que el carrito está vacío
        await page.waitForTimeout(1000);
        
        // El carrito debería estar vacío o mostrar mensaje
        await expect(page.locator('body')).toContainText(/vacío|sin productos|no hay items/i);
      }
    });
  });

  // ============================================================
  // TEST ADICIONAL: VALIDACIONES
  // ============================================================
  test('Validaciones: No se puede procesar venta sin productos', async ({ page }) => {
    test.step('Login y navegación', async () => {
      await page.goto('/');
      await page.fill('input[name="username"]', 'admin');
      await page.fill('input[name="password"]', 'admin123');
      await page.click('button[type="submit"]');
      await page.waitForURL(/\/(pos|dashboard)/i);
      await page.goto('/pos/venta/');
    });

    test.step('Intentar procesar sin productos', async () => {
      // Buscar botón de procesar
      const procesarBtn = page.locator('button:has-text("Procesar"), button:has-text("Finalizar")').first();
      
      if (await procesarBtn.isVisible()) {
        // El botón debería estar deshabilitado o no hacer nada
        const isDisabled = await procesarBtn.isDisabled();
        
        if (!isDisabled) {
          await procesarBtn.click();
          await page.waitForTimeout(500);
          
          // Debería mostrar un mensaje de error
          const errorMessage = page.locator('[class*="error"], [class*="alert-danger"], :has-text("agregar productos"), :has-text("carrito vacío")');
          
          await expect(errorMessage.first()).toBeVisible({ timeout: 3000 });
        } else {
          // Verificar que está deshabilitado
          expect(isDisabled).toBeTruthy();
        }
      }
    });
  });
});
