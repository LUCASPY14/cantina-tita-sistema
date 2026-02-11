/**
 * Service Worker para Cantina Tita POS
 * Implementa estrategias de cache para funcionamiento offline
 */

const CACHE_NAME = 'cantina-pos-v1';
const OFFLINE_CACHE = 'cantina-offline-v1';
const DATA_CACHE = 'cantina-data-v1';

// Recursos estáticos para cachear en instalación
const STATIC_ASSETS = [
    '/pos/',
    '/pos/dashboard/',
    '/static/manifest.json',
    // CDNs importantes
    'https://unpkg.com/htmx.org@1.9.10',
    'https://unpkg.com/alpinejs@3.13.3/dist/cdn.min.js',
    'https://cdn.tailwindcss.com',
    'https://cdn.jsdelivr.net/npm/daisyui@4.4.19/dist/full.min.css',
    'https://cdn.jsdelivr.net/npm/howler@2.2.4/dist/howler.min.js',
    'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js'
];

// URLs de la API que se cachearán con estrategia Network First
const API_URLS = [
    '/pos/buscar-productos/',
    '/pos/productos-categoria/',
    '/pos/buscar-tarjeta/',
    '/api/v1/productos/',
    '/api/v1/categorias/'
];

/**
 * Evento de instalación: cachear recursos estáticos
 */
self.addEventListener('install', event => {
    console.log('[SW] Instalando Service Worker...');
    
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            console.log('[SW] Cacheando recursos estáticos');
            return cache.addAll(STATIC_ASSETS).catch(err => {
                console.error('[SW] Error al cachear recursos:', err);
            });
        })
    );
    
    // Activar inmediatamente
    self.skipWaiting();
});

/**
 * Evento de activación: limpiar caches antiguos
 */
self.addEventListener('activate', event => {
    console.log('[SW] Activando Service Worker...');
    
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME && 
                        cacheName !== OFFLINE_CACHE && 
                        cacheName !== DATA_CACHE) {
                        console.log('[SW] Eliminando cache antiguo:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    
    // Tomar control inmediatamente
    return self.clients.claim();
});

/**
 * Evento fetch: estrategias de cache según el tipo de recurso
 */
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Ignorar extensiones de navegador y requests no-http
    if (!url.protocol.startsWith('http')) {
        return;
    }
    
    // Estrategia para procesar ventas: SOLO Network (guardar offline si falla)
    if (url.pathname === '/pos/procesar-venta/') {
        event.respondWith(handleSaleRequest(request));
        return;
    }
    
    // Estrategia para API: Network First (con fallback a cache)
    if (isAPIRequest(url)) {
        event.respondWith(networkFirstStrategy(request));
        return;
    }
    
    // Estrategia para recursos estáticos: Cache First (con fallback a network)
    event.respondWith(cacheFirstStrategy(request));
});

/**
 * Manejo especial para ventas offline
 */
async function handleSaleRequest(request) {
    try {
        // Intentar enviar al servidor
        const response = await fetch(request.clone());
        
        if (response.ok) {
            // Procesar ventas pendientes si existen
            processOfflineSales();
            return response;
        }
        
        throw new Error('Network response was not ok');
        
    } catch (error) {
        console.log('[SW] Sin conexión, guardando venta offline');
        
        // Guardar venta en IndexedDB para sincronizar después
        const saleData = await request.clone().json();
        await saveOfflineSale(saleData);
        
        return new Response(JSON.stringify({
            success: true,
            offline: true,
            message: 'Venta guardada offline. Se sincronizará cuando haya conexión.'
        }), {
            status: 200,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

/**
 * Estrategia Cache First: buscar en cache, si no existe buscar en red
 */
async function cacheFirstStrategy(request) {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
        // Actualizar cache en background
        fetchAndCache(request);
        return cachedResponse;
    }
    
    return fetchAndCache(request);
}

/**
 * Estrategia Network First: buscar en red, si falla buscar en cache
 */
async function networkFirstStrategy(request) {
    try {
        const response = await fetch(request);
        
        if (response.ok) {
            // Cachear respuesta exitosa
            const cache = await caches.open(DATA_CACHE);
            cache.put(request, response.clone());
        }
        
        return response;
        
    } catch (error) {
        console.log('[SW] Network failed, trying cache');
        const cachedResponse = await caches.match(request);
        
        if (cachedResponse) {
            return cachedResponse;
        }
        
        // Si no hay cache, retornar respuesta offline
        return offlineResponse();
    }
}

/**
 * Fetch y cachear recurso
 */
async function fetchAndCache(request) {
    try {
        const response = await fetch(request);
        
        if (response.ok) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, response.clone());
        }
        
        return response;
        
    } catch (error) {
        console.log('[SW] Fetch failed:', error);
        return offlineResponse();
    }
}

/**
 * Verificar si es request de API
 */
function isAPIRequest(url) {
    return API_URLS.some(apiUrl => url.pathname.startsWith(apiUrl));
}

/**
 * Respuesta offline genérica
 */
function offlineResponse() {
    return new Response(JSON.stringify({
        success: false,
        offline: true,
        error: 'Sin conexión a internet'
    }), {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
    });
}

/**
 * Guardar venta offline en IndexedDB
 */
async function saveOfflineSale(saleData) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('CantinaPOS', 1);
        
        request.onerror = () => reject(request.error);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['offlineSales'], 'readwrite');
            const store = transaction.objectStore('offlineSales');
            
            const sale = {
                ...saleData,
                timestamp: Date.now(),
                synced: false
            };
            
            store.add(sale);
            
            transaction.oncomplete = () => {
                console.log('[SW] Venta guardada offline');
                resolve();
            };
            
            transaction.onerror = () => reject(transaction.error);
        };
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('offlineSales')) {
                db.createObjectStore('offlineSales', { autoIncrement: true });
            }
        };
    });
}

/**
 * Procesar ventas offline pendientes
 */
async function processOfflineSales() {
    try {
        const db = await openDatabase();
        const transaction = db.transaction(['offlineSales'], 'readwrite');
        const store = transaction.objectStore('offlineSales');
        const sales = await store.getAll();
        
        if (sales.length === 0) return;
        
        console.log(`[SW] Sincronizando ${sales.length} ventas offline`);
        
        for (const sale of sales) {
            if (!sale.synced) {
                try {
                    const response = await fetch('/pos/procesar-venta/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(sale)
                    });
                    
                    if (response.ok) {
                        // Marcar como sincronizada
                        sale.synced = true;
                        await store.put(sale);
                        console.log('[SW] Venta sincronizada exitosamente');
                    }
                } catch (error) {
                    console.error('[SW] Error al sincronizar venta:', error);
                }
            }
        }
        
    } catch (error) {
        console.error('[SW] Error al procesar ventas offline:', error);
    }
}

/**
 * Abrir base de datos IndexedDB
 */
function openDatabase() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('CantinaPOS', 1);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('offlineSales')) {
                db.createObjectStore('offlineSales', { autoIncrement: true });
            }
        };
    });
}

/**
 * Background Sync: sincronizar cuando haya conexión
 */
self.addEventListener('sync', event => {
    console.log('[SW] Background sync event:', event.tag);
    
    if (event.tag === 'sync-sales') {
        event.waitUntil(processOfflineSales());
    }
});

/**
 * Push notifications (opcional para futuras funcionalidades)
 */
self.addEventListener('push', event => {
    const data = event.data ? event.data.json() : {};
    
    const options = {
        body: data.body || 'Notificación de Cantina POS',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/icon-72x72.png',
        vibrate: [200, 100, 200],
        data: data
    };
    
    event.waitUntil(
        self.registration.showNotification(data.title || 'Cantina POS', options)
    );
});

console.log('[SW] Service Worker cargado');
