/* 
 * POS System - Enhanced UX & Interactions
 * Sistema POS con experiencia de usuario mejorada
 * Incluye: sonidos, animaciones, feedback visual, shortcuts avanzados
 */

// ============================================================================
// CONFIGURACIÓN Y CONSTANTES
// ============================================================================

const POS_CONFIG = {
    SONIDOS_ACTIVOS: true,
    ANIMACIONES_ACTIVAS: true,
    DEBOUNCE_SEARCH: 300,
    NOTIFICATION_DURATION: 3000,
    SHORTCUT_HINTS_ENABLED: true,
    ACCESSIBILITY_ENABLED: true
};

const SONIDOS = {
    BEEP_SUCCESS: new Howl({ src: ['/static/sounds/beep-success.mp3'], volume: 0.3 }),
    BEEP_ERROR: new Howl({ src: ['/static/sounds/beep-error.mp3'], volume: 0.4 }),
    CASH_REGISTER: new Howl({ src: ['/static/sounds/cash-register.mp3'], volume: 0.2 }),
    BUTTON_CLICK: new Howl({ src: ['/static/sounds/button-click.mp3'], volume: 0.1 }),
    NOTIFICATION: new Howl({ src: ['/static/sounds/notification.mp3'], volume: 0.2 })
};

// ============================================================================
// UTILIDADES DE SONIDO Y FEEDBACK
// ============================================================================

function reproducirSonido(tipo) {
    if (!POS_CONFIG.SONIDOS_ACTIVOS || typeof Howl === 'undefined') return;
    
    try {
        if (SONIDOS[tipo]) {
            SONIDOS[tipo].play();
        }
    } catch (error) {
        console.warn('Error reproduciendo sonido:', error);
    }
}

function vibrar(patron = [100]) {
    if (navigator.vibrate) {
        navigator.vibrate(patron);
    }
}

function mostrarNotificacionToast(mensaje, tipo = 'info', duracion = POS_CONFIG.NOTIFICATION_DURATION) {
    // Usar el sistema de notificaciones de Alpine.js si está disponible
    if (window.Alpine && Alpine.store('notifications')) {
        Alpine.store('notifications').add(mensaje, tipo, duracion);
    } else {
        // Fallback a console o método personalizado
        console.log(`[${tipo.toUpperCase()}] ${mensaje}`);
    }
    
    reproducirSonido(tipo === 'error' ? 'BEEP_ERROR' : 'NOTIFICATION');
}

function anunciarParaLectorPantalla(mensaje) {
    if (!POS_CONFIG.ACCESSIBILITY_ENABLED) return;
    
    const anuncio = document.getElementById('aria-announcer') || crearAnunciadorAria();
    anuncio.textContent = mensaje;
}

function crearAnunciadorAria() {
    const div = document.createElement('div');
    div.id = 'aria-announcer';
    div.setAttribute('aria-live', 'polite');
    div.setAttribute('aria-atomic', 'true');
    div.className = 'sr-only';
    document.body.appendChild(div);
    return div;
}

// ============================================================================
// COMPONENTE PRINCIPAL POS 
// ============================================================================

function ventaPOS() {
    return {
        // ====== ESTADO PRINCIPAL ======
        carrito: [],
        productos: [],
        productosFiltrados: [],
        categorias: [],
        clienteSeleccionado: null,
        cargandoProductos: false,
        procesando: false,
        
        // ====== BÚSQUEDA Y FILTROS ======
        search: '',
        categoriaSeleccionada: '',
        numeroTarjeta: '',
        errorTarjeta: false,
        
        // ====== CONFIGURACIÓN UX ======
        ultimoProductoAgregado: null,
        sonidosHabilitados: POS_CONFIG.SONIDOS_ACTIVOS,
        showKeyboardHints: POS_CONFIG.SHORTCUT_HINTS_ENABLED,
        
        // ====== INICIALIZACIÓN ======
        init() {
            this.cargarProductos();
            this.cargarCategorias();
            this.configurarShortcuts();
            this.configurarAccesibilidad();
            
            // Enfocar búsqueda al iniciar
            this.$nextTick(() => {
                const searchInput = document.getElementById('product-search');
                if (searchInput) searchInput.focus();
            });
            
            console.log('🎯 Sistema POS iniciado con UX mejorada');
            mostrarNotificacionToast('Sistema POS listo', 'success');
        },
        
        // ====== PRODUCTOS ======
        async cargarProductos() {
            this.cargandoProductos = true;
            
            try {
                const response = await fetch('/api/pos/productos/disponibles/');
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                
                const data = await response.json();
                this.productos = data.map(producto => ({
                    ...producto,
                    imagenCargada: false,
                    _adding: false
                }));
                this.productosFiltrados = [...this.productos];
                
                anunciarParaLectorPantalla(`${this.productos.length} productos cargados`);
                
            } catch (error) {
                console.error('Error cargando productos:', error);
                mostrarNotificacionToast('Error al cargar productos', 'error');
            } finally {
                this.cargandoProductos = false;
            }
        },
        
        async cargarCategorias() {
            try {
                const response = await fetch('/api/pos/categorias/');
                if (response.ok) {
                    this.categorias = await response.json();
                }
            } catch (error) {
                console.warn('Error cargando categorías:', error);
            }
        },
        
        // ====== BÚSQUEDA AVANZADA ======
        buscarProductos() {
            const termino = this.search.toLowerCase().trim();
            
            if (!termino) {
                this.productosFiltrados = [...this.productos];
                return;
            }
            
            this.productosFiltrados = this.productos.filter(producto => {
                return producto.descripcion.toLowerCase().includes(termino) ||
                       (producto.codigo_barras && producto.codigo_barras.includes(termino)) ||
                       (producto.categoria_nombre && producto.categoria_nombre.toLowerCase().includes(termino));
            });
            
            // Aplicar filtro de categoría si está seleccionado
            if (this.categoriaSeleccionada) {
                this.filtrarPorCategoria();
            }
            
            anunciarParaLectorPantalla(`${this.productosFiltrados.length} productos encontrados`);
        },
        
        filtrarPorCategoria() {
            let productos = this.search ? this.productosFiltrados : this.productos;
            
            if (this.categoriaSeleccionada) {
                productos = productos.filter(p => p.id_categoria == this.categoriaSeleccionada);
            }
            
            this.productosFiltrados = productos;
        },
        
        limpiarBusqueda() {
            this.search = '';
            this.categoriaSeleccionada = '';
            this.productosFiltrados = [...this.productos];
            
            // Enfocar campo de búsqueda
            this.$nextTick(() => {
                const searchInput = document.getElementById('product-search');
                if (searchInput) searchInput.focus();
            });
        },
        
        // ====== CARRITO AVANZADO ======
        async agregarProductoConFeedback(producto) {
            if (producto.stock <= 0) {
                vibrar([100, 50, 100]);
                mostrarNotificacionToast('Producto sin stock', 'error');
                return;
            }
            
            // Animación visual en el producto
            producto._adding = true;
            reproducirSonido('BUTTON_CLICK');
            
            // Agregar al carrito
            const itemExistente = this.carrito.find(item => item.producto.id === producto.id);
            
            if (itemExistente) {
                if (itemExistente.cantidad < producto.stock) {
                    itemExistente.cantidad++;
                    this.animarCantidadActualizada(itemExistente);
                } else {
                    mostrarNotificacionToast('Stock máximo alcanzado', 'warning');
                    vibrar([50]);
                }
            } else {
                this.carrito.push({
                    producto: { ...producto },
                    cantidad: 1
                });
            }
            
            // Feedback
            this.ultimoProductoAgregado = producto.id;
            reproducirSonido('BEEP_SUCCESS');
            anunciarParaLectorPantalla(`${producto.descripcion} agregado al carrito`);
            
            // Limpiar animación
            setTimeout(() => {
                producto._adding = false;
            }, 600);
            
            // Auto-scroll al carrito en móviles
            if (window.innerWidth < 768) {
                this.scrollToCarrito();
            }
        },
        
        eliminarDelCarrito(index) {
            const item = this.carrito[index];
            if (!item) return;
            
            this.carrito.splice(index, 1);
            reproducirSonido('BEEP_ERROR');
            anunciarParaLectorPantalla(`${item.producto.descripcion} eliminado del carrito`);
        },
        
        cambiarCantidad(index, nuevaCantidad) {
            const item = this.carrito[index];
            if (!item) return;
            
            if (nuevaCantidad <= 0) {
                this.eliminarDelCarrito(index);
                return;
            }
            
            if (nuevaCantidad > item.producto.stock) {
                mostrarNotificacionToast(`Stock máximo: ${item.producto.stock}`, 'warning');
                vibrar([50]);
                return;
            }
            
            item.cantidad = nuevaCantidad;
            this.animarCantidadActualizada(item);
            reproducirSonido('BUTTON_CLICK');
        },
        
        validarCantidad(item, index) {
            if (item.cantidad > item.producto.stock) {
                mostrarNotificacionToast('Cantidad excede el stock disponible', 'warning');
                item.cantidad = item.producto.stock;
            }
            
            if (item.cantidad <= 0) {
                this.eliminarDelCarrito(index);
            }
        },
        
        limpiarCarrito() {
            if (this.carrito.length === 0) return;
            
            if (confirm('¿Está seguro de que desea limpiar todo el carrito?')) {
                const cantidadItems = this.carrito.length;
                this.carrito = [];
                reproducirSonido('BEEP_ERROR');
                mostrarNotificacionToast(`${cantidadItems} productos eliminados del carrito`, 'info');
                anunciarParaLectorPantalla('Carrito limpiado');
            }
        },
        
        animarCantidadActualizada(item) {
            // Encuentra el badge de cantidad y añade animación
            this.$nextTick(() => {
                const badges = document.querySelectorAll('.qty-badge');
                badges.forEach(badge => {
                    if (badge.textContent.trim() == item.cantidad) {
                        badge.classList.add('updated');
                        setTimeout(() => badge.classList.remove('updated'), 500);
                    }
                });
            });
        },
        
        // ====== CÁLCULOS ======
        calcularSubtotal() {
            return this.carrito.reduce((total, item) => {
                return total + (item.producto.precio_venta * item.cantidad);
            }, 0);
        },
        
        calcularIVA() {
            return Math.round(this.calcularSubtotal() * 0.1);
        },
        
        calcularTotal() {
            return this.calcularSubtotal() + this.calcularIVA();
        },
        
        // ====== VALIDACIONES ======
        puedeProcessarVenta() {
            return this.carrito.length > 0 && 
                   this.clienteSeleccionado && 
                   !this.procesando &&
                   !this.tieneStockInsuficiente();
        },
        
        tieneStockInsuficiente() {
            return this.carrito.some(item => item.cantidad > item.producto.stock);
        },
        
        productoEnCarrito(productoId) {
            return this.carrito.some(item => item.producto.id === productoId);
        },
        
        getCantidadEnCarrito(productoId) {
            const item = this.carrito.find(item => item.producto.id === productoId);
            return item ? item.cantidad : 0;
        },
        
        // ====== PROCESAMIENTO DE VENTA ======
        async procesarVentaConFeedback() {
            if (!this.puedeProcessarVenta()) {
                mostrarNotificacionToast('Complete los datos requeridos para procesar', 'warning');
                return;
            }
            
            this.procesando = true;
            reproducirSonido('CASH_REGISTER');
            anunciarParaLectorPantalla('Procesando venta, por favor espere...');
            
            try {
                const ventaData = {
                    cliente_id: this.clienteSeleccionado.id,
                    items: this.carrito.map(item => ({
                        producto_id: item.producto.id,
                        cantidad: item.cantidad,
                        precio_unitario: item.producto.precio_venta
                    })),
                    total: this.calcularTotal()
                };
                
                const response = await fetch('/api/pos/ventas/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify(ventaData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    // Éxito
                    reproducirSonido('BEEP_SUCCESS');
                    vibrar([100, 50, 100, 50, 200]);
                    mostrarNotificacionToast(`¡Venta procesada exitosamente! ID: ${result.id}`, 'success');
                    anunciarParaLectorPantalla(`Venta completada por ${this.formatearPrecio(this.calcularTotal())}`);
                    
                    // Limpiar formulario
                    this.limpiarVenta();
                    
                } else {
                    throw new Error(result.error || 'Error procesando venta');
                }
                
            } catch (error) {
                console.error('Error procesando venta:', error);
                reproducirSonido('BEEP_ERROR');
                vibrar([200, 100, 200]);
                mostrarNotificacionToast(`Error: ${error.message}`, 'error');
                anunciarParaLectorPantalla('Error al procesar venta');
            } finally {
                this.procesando = false;
            }
        },
        
        confirmarCancelarConFeedback() {
            if (this.carrito.length === 0 && !this.clienteSeleccionado) return;
            
            const mensaje = this.carrito.length > 0 
                ? `¿Cancelar venta actual? Se perderán ${this.carrito.length} productos.`
                : '¿Limpiar cliente seleccionado?';
                
            if (confirm(mensaje)) {
                this.limpiarVenta();
                reproducirSonido('BEEP_ERROR');
                mostrarNotificacionToast('Venta cancelada', 'info');
                anunciarParaLectorPantalla('Venta cancelada');
            }
        },
        
        limpiarVenta() {
            this.carrito = [];
            this.clienteSeleccionado = null;
            this.numeroTarjeta = '';
            this.search = '';
            this.categoriaSeleccionada = '';
            this.productosFiltrados = [...this.productos];
            
            // Enfocar búsqueda
            this.$nextTick(() => {
                const searchInput = document.getElementById('product-search');
                if (searchInput) searchInput.focus();
            });
        },
        
        // ====== CLIENTE/TARJETA ======
        async buscarTarjeta() {
            if (!this.numeroTarjeta.trim()) return;
            
            try {
                const response = await fetch(`/api/pos/tarjetas/buscar/?numero=${this.numeroTarjeta}`);
                const data = await response.json();
                
                if (response.ok && data.cliente) {
                    this.clienteSeleccionado = data.cliente;
                    this.errorTarjeta = false;
                    reproducirSonido('BEEP_SUCCESS');
                    anunciarParaLectorPantalla(`Cliente ${data.cliente.nombre} seleccionado`);
                } else {
                    this.errorTarjeta = true;
                    reproducirSonido('BEEP_ERROR');
                    mostrarNotificacionToast('Tarjeta no encontrada', 'error');
                }
            } catch (error) {
                console.error('Error buscando tarjeta:', error);
                this.errorTarjeta = true;
                mostrarNotificacionToast('Error al buscar tarjeta', 'error');
            }
        },
        
        seleccionarClienteGenerico() {
            this.clienteSeleccionado = {
                id: 'generico',
                nombre: 'Cliente Genérico',
                nro_tarjeta: '000000',
                saldo: 999999
            };
            reproducirSonido('BUTTON_CLICK');
            anunciarParaLectorPantalla('Cliente genérico seleccionado');
        },
        
        limpiarCliente() {
            this.clienteSeleccionado = null;
            this.numeroTarjeta = '';
            this.errorTarjeta = false;
            reproducirSonido('BUTTON_CLICK');
        },
        
        // ====== UTILIDADES ======
        formatearPrecio(precio) {
            return new Intl.NumberFormat('es-PY', {
                style: 'currency',
                currency: 'PYG',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(precio);
        },
        
        scrollToCarrito() {
            document.getElementById('cart-section')?.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        },
        
        getCSRFToken() {
            return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
        },
        
        // ====== SHORTCUTS DE TECLADO ======
        configurarShortcuts() {
            document.addEventListener('keydown', (e) => {
                // Ignorar si está escribiendo en un input
                if (e.target.tagName.toLowerCase() === 'input' || e.target.tagName.toLowerCase() === 'textarea') {
                    return;
                }
                
                switch (e.key) {
                    case 'F2':
                        e.preventDefault();
                        document.getElementById('product-search')?.focus();
                        break;
                        
                    case 'Escape':
                        e.preventDefault();
                        this.confirmarCancelarConFeedback();
                        break;
                        
                    case 'Enter':
                        if (e.ctrlKey) {
                            e.preventDefault();
                            this.procesarVentaConFeedback();
                        }
                        break;
                        
                    case 'Delete':
                        if (e.ctrlKey) {
                            e.preventDefault();
                            this.limpiarCarrito();
                        }
                        break;
                }
            });
        },
        
        configurarAccesibilidad() {
            // Crear anunciador ARIA
            crearAnunciadorAria();
            
            // Configurar navegación por teclado en productos
            this.$nextTick(() => {
                const productos = document.querySelectorAll('.product-card');
                productos.forEach((producto, index) => {
                    producto.addEventListener('keydown', (e) => {
                        switch (e.key) {
                            case 'ArrowRight':
                                e.preventDefault();
                                const siguiente = productos[index + 1];
                                siguiente?.focus();
                                break;
                                
                            case 'ArrowLeft':
                                e.preventDefault();
                                const anterior = productos[index - 1];
                                anterior?.focus();
                                break;
                        }
                    });
                });
            });
        },
        
        // ====== ACCIONES RÁPIDAS ======
        buscarProductoRapido() {
            document.getElementById('product-search')?.focus();
        },
        
        verHistorialVentas() {
            window.location.href = '/pos/historial/';
        }
    };
}

// ============================================================================
// UTILIDADES GLOBALES PARA TEMPLATES
// ============================================================================

// Función para debounce en búsquedas
function searchWithDebounce(callback, delay = POS_CONFIG.DEBOUNCE_SEARCH) {
    return {
        search: '',
        loading: false,
        timeout: null,
        
        handleSearch() {
            this.loading = true;
            clearTimeout(this.timeout);
            
            this.timeout = setTimeout(() => {
                callback.call(this);
                this.loading = false;
            }, delay);
        }
    };
}

// Sistema de notificaciones para Alpine.js
document.addEventListener('alpine:init', () => {
    Alpine.store('notifications', {
        items: [],
        nextId: 1,
        
        add(message, type = 'info', duration = 3000) {
            const id = this.nextId++;
            const notification = {
                id,
                message,
                type,
                duration,
                progress: 100
            };
            
            this.items.push(notification);
            
            if (duration > 0) {
                // Animar barra de progreso
                const interval = setInterval(() => {
                    notification.progress -= (100 / duration) * 50;
                    if (notification.progress <= 0) {
                        clearInterval(interval);
                        this.remove(id);
                    }
                }, 50);
            }
            
            return id;
        },
        
        remove(id) {
            const index = this.items.findIndex(item => item.id === id);
            if (index > -1) {
                this.items.splice(index, 1);
            }
        },
        
        clear() {
            this.items = [];
        }
    });
});

console.log('🎯 POS Enhanced UX loaded successfully');