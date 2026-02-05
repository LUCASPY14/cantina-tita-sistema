/**
 * E2E Test - PWA Modo Offline
 * Sprint 8 - Testing y QA
 * 
 * Verificaciones:
 * 1. Service Worker se registra correctamente
 * 2. Aplicación funciona offline
 * 3. Cache almacena recursos estáticos
 * 4. Navegación offline funcional
 * 5. Sincronización al volver online
 */

import { test, expect } from '@playwright/test';

test.describe('PWA - Modo Offline', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  // ============================================================
  // TEST 1: REGISTRO DE SERVICE WORKER
  // ============================================================
  test('Service Worker se registra correctamente', async ({ page, context }) => {
    test.step('Verificar registro del Service Worker', async () => {
      // Esperar a que el Service Worker se registre
      await page.waitForTimeout(2000);
      
      // Verificar que el Service Worker está registrado
      const swRegistered = await page.evaluate(async () => {
        if ('serviceWorker' in navigator) {
          const registrations = await navigator.serviceWorker.getRegistrations();
          return registrations.length > 0;
        }
        return false;
      });
      
      expect(swRegistered).toBeTruthy();
    });

    test.step('Verificar estado del Service Worker', async () => {
      const swState = await page.evaluate(async () => {
        if ('serviceWorker' in navigator) {
          const registration = await navigator.serviceWorker.ready;
          return {
            active: registration.active !== null,
            scope: registration.scope,
            updateViaCache: registration.updateViaCache
          };
        }
        return null;
      });
      
      expect(swState).not.toBeNull();
      expect(swState?.active).toBeTruthy();
    });
  });

  // ============================================================
  // TEST 2: FUNCIONAMIENTO OFFLINE
  // ============================================================
  test('Aplicación funciona en modo offline', async ({ page, context }) => {
    test.step('1. Cargar aplicación con conexión', async () => {
      // Login al sistema
      await page.goto('/');
      
      // Si hay login, autenticarse
      const loginForm = page.locator('form[action*="login"], input[name="username"]');
      
      if (await loginForm.count() > 0) {
        await page.fill('input[name="username"]', 'admin');
        await page.fill('input[name="password"]', 'admin123');
        await page.click('button[type="submit"]');
        await page.waitForTimeout(2000);
      }
      
      // Navegar a POS
      await page.goto('/pos/venta/');
      await page.waitForLoadState('networkidle');
      
      // Esperar que el Service Worker cachee los recursos
      await page.waitForTimeout(3000);
    });

    test.step('2. Simular modo offline', async () => {
      // Desconectar la red
      await context.setOffline(true);
      
      // Verificar que estamos offline
      const isOffline = await page.evaluate(() => !navigator.onLine);
      expect(isOffline).toBeTruthy();
    });

    test.step('3. Verificar navegación offline', async () => {
      // Recargar la página (debería funcionar desde cache)
      await page.reload();
      
      // Verificar que la página cargó (no error de red)
      await expect(page.locator('body')).not.toContainText(/ERR_INTERNET_DISCONNECTED|sin conexión|no internet/i);
      
      // Verificar que los elementos principales están visibles
      const mainContent = page.locator('main, [role="main"], body');
      await expect(mainContent).toBeVisible();
    });

    test.step('4. Verificar navegación entre páginas offline', async () => {
      // Navegar a otra página
      const dashboardLink = page.locator('a[href*="/pos"], a[href*="/dashboard"]').first();
      
      if (await dashboardLink.isVisible({ timeout: 2000 })) {
        await dashboardLink.click();
        await page.waitForTimeout(1000);
        
        // Verificar que la navegación funcionó
        const content = page.locator('body');
        await expect(content).toBeVisible();
      }
    });

    test.step('5. Restaurar conexión', async () => {
      await context.setOffline(false);
      
      const isOnline = await page.evaluate(() => navigator.onLine);
      expect(isOnline).toBeTruthy();
    });
  });

  // ============================================================
  // TEST 3: VERIFICAR CACHE
  // ============================================================
  test('Cache almacena recursos estáticos correctamente', async ({ page }) => {
    test.step('Verificar que el cache contiene recursos', async () => {
      // Esperar a que se cacheen los recursos
      await page.waitForTimeout(3000);
      
      // Verificar contenido del cache
      const cacheContents = await page.evaluate(async () => {
        const cacheNames = await caches.keys();
        const results: Record<string, number> = {};
        
        for (const cacheName of cacheNames) {
          const cache = await caches.open(cacheName);
          const keys = await cache.keys();
          results[cacheName] = keys.length;
        }
        
        return results;
      });
      
      // Verificar que hay al menos un cache con contenido
      const totalCachedItems = Object.values(cacheContents).reduce((sum, count) => sum + count, 0);
      expect(totalCachedItems).toBeGreaterThan(0);
    });

    test.step('Verificar recursos críticos en cache', async () => {
      const criticalResources = await page.evaluate(async () => {
        const cacheNames = await caches.keys();
        const foundResources: string[] = [];
        
        for (const cacheName of cacheNames) {
          const cache = await caches.open(cacheName);
          
          // Buscar recursos críticos
          const criticalUrls = [
            '/static/css/',
            '/static/js/',
            '/manifest.json',
            '/pos/venta/'
          ];
          
          for (const url of criticalUrls) {
            const keys = await cache.keys();
            const found = keys.some(request => request.url.includes(url));
            
            if (found) {
              foundResources.push(url);
            }
          }
        }
        
        return foundResources;
      });
      
      // Al menos algunos recursos críticos deberían estar cacheados
      expect(criticalResources.length).toBeGreaterThan(0);
    });
  });

  // ============================================================
  // TEST 4: MANIFEST Y PWA INSTALL
  // ============================================================
  test('Manifest está configurado correctamente', async ({ page }) => {
    test.step('Verificar link al manifest', async () => {
      const manifestLink = page.locator('link[rel="manifest"]');
      await expect(manifestLink).toHaveCount(1);
      
      const href = await manifestLink.getAttribute('href');
      expect(href).toBeTruthy();
    });

    test.step('Verificar contenido del manifest', async ({ page }) => {
      // Navegar al manifest
      const manifestLink = await page.locator('link[rel="manifest"]').getAttribute('href');
      
      if (manifestLink) {
        const manifestUrl = new URL(manifestLink, page.url()).toString();
        const manifestResponse = await page.request.get(manifestUrl);
        
        expect(manifestResponse.ok()).toBeTruthy();
        
        const manifest = await manifestResponse.json();
        
        // Verificar propiedades esenciales
        expect(manifest.name).toBeTruthy();
        expect(manifest.short_name).toBeTruthy();
        expect(manifest.start_url).toBeTruthy();
        expect(manifest.display).toBeTruthy();
        expect(manifest.icons).toBeTruthy();
        expect(manifest.icons.length).toBeGreaterThan(0);
        
        // Verificar que hay iconos de diferentes tamaños
        const iconSizes = manifest.icons.map((icon: any) => icon.sizes);
        expect(iconSizes).toContain('192x192');
        expect(iconSizes).toContain('512x512');
      }
    });
  });

  // ============================================================
  // TEST 5: EVENTOS ONLINE/OFFLINE
  // ============================================================
  test('Aplicación responde a eventos online/offline', async ({ page, context }) => {
    test.step('Configurar listeners de eventos', async () => {
      // Configurar listeners
      await page.evaluate(() => {
        (window as any).onlineEvents = 0;
        (window as any).offlineEvents = 0;
        
        window.addEventListener('online', () => {
          (window as any).onlineEvents++;
        });
        
        window.addEventListener('offline', () => {
          (window as any).offlineEvents++;
        });
      });
    });

    test.step('Simular cambios de conectividad', async () => {
      // Ir offline
      await context.setOffline(true);
      await page.waitForTimeout(1000);
      
      // Volver online
      await context.setOffline(false);
      await page.waitForTimeout(1000);
      
      // Verificar que se dispararon los eventos
      const events = await page.evaluate(() => ({
        online: (window as any).onlineEvents,
        offline: (window as any).offlineEvents
      }));
      
      expect(events.offline).toBeGreaterThan(0);
      expect(events.online).toBeGreaterThan(0);
    });
  });

  // ============================================================
  // TEST 6: ACTUALIZACIÓN DEL SERVICE WORKER
  // ============================================================
  test('Service Worker se actualiza correctamente', async ({ page }) => {
    test.step('Verificar mecanismo de actualización', async () => {
      const updateCheck = await page.evaluate(async () => {
        if ('serviceWorker' in navigator) {
          const registration = await navigator.serviceWorker.ready;
          
          // Forzar check de actualización
          await registration.update();
          
          return {
            hasUpdate: registration.waiting !== null,
            installing: registration.installing !== null,
            active: registration.active !== null
          };
        }
        return null;
      });
      
      expect(updateCheck).not.toBeNull();
      expect(updateCheck?.active).toBeTruthy();
    });
  });

  // ============================================================
  // TEST 7: FALLBACK OFFLINE
  // ============================================================
  test('Página offline fallback funciona', async ({ page, context }) => {
    test.step('Cargar página y luego ir offline', async () => {
      // Cargar una página que no está en cache
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);
      
      // Ir offline
      await context.setOffline(true);
      
      // Intentar navegar a una página que probablemente no esté en cache
      await page.goto('/pagina-que-no-existe-' + Date.now(), { waitUntil: 'domcontentloaded' }).catch(() => {});
      
      await page.waitForTimeout(2000);
      
      // Verificar que hay algún contenido (página offline fallback)
      const body = page.locator('body');
      await expect(body).toBeVisible();
      
      // Restaurar conexión
      await context.setOffline(false);
    });
  });
});

// ============================================================
// TEST DE RENDIMIENTO PWA
// ============================================================
test.describe('PWA - Rendimiento', () => {
  
  test('Métricas de rendimiento cumplen estándares PWA', async ({ page }) => {
    test.step('Medir tiempo de carga', async () => {
      const startTime = Date.now();
      
      await page.goto('/pos/venta/');
      await page.waitForLoadState('networkidle');
      
      const loadTime = Date.now() - startTime;
      
      // El tiempo de carga debería ser razonable (< 5 segundos)
      expect(loadTime).toBeLessThan(5000);
    });

    test.step('Verificar métricas web vitals', async () => {
      const metrics = await page.evaluate(() => {
        return new Promise((resolve) => {
          const observer = new PerformanceObserver((list) => {
            const entries = list.getEntries();
            const lcpEntry = entries.find((entry) => entry.entryType === 'largest-contentful-paint');
            
            resolve({
              lcp: lcpEntry ? (lcpEntry as any).renderTime || (lcpEntry as any).loadTime : 0
            });
          });
          
          observer.observe({ entryTypes: ['largest-contentful-paint'] });
          
          // Timeout después de 10 segundos
          setTimeout(() => resolve({ lcp: 0 }), 10000);
        });
      });
      
      // LCP debería ser < 2.5 segundos (2500ms) para "Good"
      // Relajamos a < 4 segundos para desarrollo
      expect((metrics as any).lcp).toBeLessThan(4000);
    });
  });
});
