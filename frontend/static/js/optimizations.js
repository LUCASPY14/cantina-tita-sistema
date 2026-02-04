/**
 * Lazy Loading de Imágenes
 * Optimiza la carga de imágenes usando Intersection Observer
 */

class LazyLoader {
    constructor(options = {}) {
        this.options = {
            root: null,
            rootMargin: '50px',
            threshold: 0.01,
            ...options
        };
        
        this.observer = null;
        this.init();
    }
    
    init() {
        // Verificar soporte de Intersection Observer
        if (!('IntersectionObserver' in window)) {
            console.warn('[LazyLoad] IntersectionObserver no soportado, cargando todas las imágenes');
            this.loadAllImages();
            return;
        }
        
        // Crear observer
        this.observer = new IntersectionObserver(
            this.handleIntersection.bind(this),
            this.options
        );
        
        // Observar todas las imágenes lazy
        this.observeImages();
    }
    
    observeImages() {
        const images = document.querySelectorAll('img[data-src], img[loading="lazy"]');
        
        images.forEach(img => {
            // Si tiene data-src, usar lazy loading personalizado
            if (img.dataset.src) {
                this.observer.observe(img);
            }
            // Si tiene loading="lazy", el navegador lo maneja
        });
    }
    
    handleIntersection(entries, observer) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                this.loadImage(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }
    
    loadImage(img) {
        const src = img.dataset.src;
        const srcset = img.dataset.srcset;
        
        if (!src) return;
        
        // Crear imagen temporal para precargar
        const tempImg = new Image();
        
        tempImg.onload = () => {
            // Aplicar src real
            img.src = src;
            if (srcset) img.srcset = srcset;
            
            // Agregar clase loaded para animaciones
            img.classList.add('lazy-loaded');
            
            // Remover data-src
            delete img.dataset.src;
            delete img.dataset.srcset;
        };
        
        tempImg.onerror = () => {
            console.error(`[LazyLoad] Error al cargar imagen: ${src}`);
            // Mostrar imagen de placeholder o fallback
            img.src = '/static/img/placeholder.png';
            img.classList.add('lazy-error');
        };
        
        // Iniciar carga
        tempImg.src = src;
        if (srcset) tempImg.srcset = srcset;
    }
    
    loadAllImages() {
        const images = document.querySelectorAll('img[data-src]');
        images.forEach(img => this.loadImage(img));
    }
    
    refresh() {
        // Observar nuevas imágenes agregadas dinámicamente
        if (this.observer) {
            this.observeImages();
        }
    }
    
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }
    }
}

/**
 * Background Image Lazy Loading
 * Para elementos con background-image
 */
class BackgroundLazyLoader {
    constructor() {
        this.observer = null;
        this.init();
    }
    
    init() {
        if (!('IntersectionObserver' in window)) return;
        
        this.observer = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const element = entry.target;
                        const bgImage = element.dataset.bg;
                        
                        if (bgImage) {
                            element.style.backgroundImage = `url(${bgImage})`;
                            element.classList.add('bg-loaded');
                            delete element.dataset.bg;
                            this.observer.unobserve(element);
                        }
                    }
                });
            },
            { rootMargin: '50px' }
        );
        
        // Observar elementos con data-bg
        document.querySelectorAll('[data-bg]').forEach(el => {
            this.observer.observe(el);
        });
    }
}

/**
 * Optimización de carga de recursos externos
 */
function optimizeExternalResources() {
    // Preconnect a dominios externos importantes
    const domains = [
        'https://cdn.jsdelivr.net',
        'https://unpkg.com',
        'https://cdn.tailwindcss.com',
        'https://cdnjs.cloudflare.com'
    ];
    
    domains.forEach(domain => {
        const link = document.createElement('link');
        link.rel = 'preconnect';
        link.href = domain;
        link.crossOrigin = 'anonymous';
        document.head.appendChild(link);
    });
}

/**
 * Defer de scripts no críticos
 */
function deferNonCriticalScripts() {
    // Cargar scripts no críticos después del load
    window.addEventListener('load', () => {
        // Analytics, widgets, etc se cargan después
        const deferredScripts = document.querySelectorAll('script[data-defer]');
        
        deferredScripts.forEach(script => {
            const newScript = document.createElement('script');
            newScript.src = script.dataset.src;
            newScript.async = true;
            document.body.appendChild(newScript);
        });
    });
}

/**
 * Comprimir y optimizar imágenes
 */
function compressImages() {
    const images = document.querySelectorAll('img');
    
    images.forEach(img => {
        // Agregar loading="lazy" si no tiene
        if (!img.loading && !img.dataset.src) {
            img.loading = 'lazy';
        }
        
        // Agregar decoding="async" para mejor performance
        img.decoding = 'async';
    });
}

// Inicializar al cargar el DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initOptimizations);
} else {
    initOptimizations();
}

function initOptimizations() {
    // Lazy loading de imágenes
    window.lazyLoader = new LazyLoader();
    window.bgLazyLoader = new BackgroundLazyLoader();
    
    // Optimizaciones adicionales
    optimizeExternalResources();
    deferNonCriticalScripts();
    compressImages();
    
    console.log('[Optimizations] Performance optimizations loaded');
}

// Exponer API global
window.LazyLoader = {
    refresh: () => {
        if (window.lazyLoader) window.lazyLoader.refresh();
        if (window.bgLazyLoader) window.bgLazyLoader.init();
    }
};

// Estilos CSS para lazy loading
const style = document.createElement('style');
style.textContent = `
    img[data-src] {
        opacity: 0;
        transition: opacity 0.3s ease-in-out;
    }
    
    img.lazy-loaded {
        opacity: 1;
    }
    
    img.lazy-error {
        opacity: 0.5;
        filter: grayscale(100%);
    }
    
    [data-bg] {
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }
    
    .bg-loaded {
        animation: fadeIn 0.5s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
`;
document.head.appendChild(style);
