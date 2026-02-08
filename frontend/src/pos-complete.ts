// Sistema POS Completo - Cliente API y Funcionalidades Integradas
// Archivo: frontend/src/pos-complete.ts

import { api } from './utils/api'
import type { 
    Producto, 
    Venta, 
    VentaItem, 
    Cliente,
    CarritoItem 
} from './types/api'

// Configuración POS
const POS_CONFIG = {
    SONIDOS_HABILITADOS: true,
    AUTOGUARDADO: true,
    TIEMPO_AUTOGUARDADO: 30000, // 30 segundos
    MAX_ITEMS_POR_VENTA: 50,
    SHORTCUTS: {
        BUSCAR_PRODUCTO: 'F2',
        NUEVA_VENTA: 'F1',
        PROCESAR_VENTA: 'F12',
        CANCELAR: 'ESC'
    }
}

// Estado global del POS
interface EstadoPOS {
    productos: Producto[]
    carrito: CarritoItem[]
    clienteSeleccionado: Cliente | null
    ventaActual: Venta | null
    cargando: boolean
    error: string | null
    busqueda: string
    estadisticas: {
        ventasHoy: number
        montoHoy: number
        productosVendidos: number
    }
}

class SistemaPOS {
    private estado: EstadoPOS = {
        productos: [],
        carrito: [],
        clienteSeleccionado: null,
        ventaActual: null,
        cargando: false,
        error: null,
        busqueda: '',
        estadisticas: {
            ventasHoy: 0,
            montoHoy: 0,
            productosVendidos: 0
        }
    }

    private listeners: { [key: string]: Function[] } = {}
    private autoguardadoInterval: NodeJS.Timeout | null = null

    constructor() {
        this.inicializar()
        this.configurarShortcuts()
        this.iniciarAutoguardado()
    }

    // MÉTODOS DE INICIALIZACIÓN
    async inicializar() {
        try {
            this.actualizarEstado({ cargando: true, error: null })
            
            // Cargar datos iniciales en paralelo
            await Promise.all([
                this.cargarProductos(),
                this.cargarEstadisticas(),
                this.recuperarCarritoGuardado()
            ])

            this.emitir('pos:inicializado')
            this.log('✅ Sistema POS inicializado correctamente')
        } catch (error) {
            this.manejarError('Error inicializando POS', error)
        } finally {
            this.actualizarEstado({ cargando: false })
        }
    }

    private configurarShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Solo procesar si no estamos en un input
            if (e.target instanceof HTMLInputElement) return

            switch (e.key) {
                case 'F2':
                    e.preventDefault()
                    this.enfocarBusqueda()
                    break
                case 'F1':
                    e.preventDefault()
                    this.nuevaVenta()
                    break
                case 'F12':
                    e.preventDefault()
                    this.procesarVenta()
                    break
                case 'Escape':
                    e.preventDefault()
                    this.cancelarVenta()
                    break
            }
        })
    }

    private iniciarAutoguardado() {
        if (POS_CONFIG.AUTOGUARDADO) {
            this.autoguardadoInterval = setInterval(() => {
                this.guardarCarritoLocal()
            }, POS_CONFIG.TIEMPO_AUTOGUARDADO)
        }
    }

    // MÉTODOS DE PRODUCTOS
    async cargarProductos() {
        try {
            const response = await api.get('/pos/productos/disponibles/')
            this.actualizarEstado({ 
                productos: response.results || response 
            })
            this.log(`📦 ${this.estado.productos.length} productos cargados`)
        } catch (error) {
            throw new Error('Error cargando productos: ' + error)
        }
    }

    async buscarProductos(termino: string) {
        if (!termino.trim()) {
            return this.estado.productos
        }

        try {
            const params = new URLSearchParams({
                search: termino,
                ordering: 'descripcion'
            })
            
            const response = await api.get(`/pos/productos/?${params}`)
            return response.results || response
        } catch (error) {
            this.manejarError('Error buscando productos', error)
            return []
        }
    }

    async buscarPorCodigo(codigo: string): Promise<Producto | null> {
        try {
            const response = await api.get(`/pos/productos/buscar_codigo/?codigo=${codigo}`)
            return response
        } catch (error) {
            if (error.message.includes('404')) {
                return null // Producto no encontrado
            }
            throw error
        }
    }

    // MÉTODOS DE CARRITO
    agregarAlCarrito(producto: Producto, cantidad: number = 1) {
        try {
            // Validaciones
            if (cantidad <= 0) {
                throw new Error('La cantidad debe ser mayor a 0')
            }

            if (producto.stock < cantidad) {
                throw new Error(`Stock insuficiente. Disponible: ${producto.stock}`)
            }

            if (this.estado.carrito.length >= POS_CONFIG.MAX_ITEMS_POR_VENTA) {
                throw new Error(`Máximo ${POS_CONFIG.MAX_ITEMS_POR_VENTA} items por venta`)
            }

            // Buscar si ya existe en el carrito
            const indiceExistente = this.estado.carrito.findIndex(
                item => item.producto.id_producto === producto.id_producto
            )

            let nuevoCarrito = [...this.estado.carrito]

            if (indiceExistente >= 0) {
                // Actualizar cantidad existente
                const cantidadTotal = nuevoCarrito[indiceExistente].cantidad + cantidad
                
                if (cantidadTotal > producto.stock) {
                    throw new Error(`Stock insuficiente. Máximo: ${producto.stock}`)
                }

                nuevoCarrito[indiceExistente] = {
                    ...nuevoCarrito[indiceExistente],
                    cantidad: cantidadTotal,
                    subtotal: cantidadTotal * producto.precio_venta
                }
            } else {
                // Agregar nuevo item
                nuevoCarrito.push({
                    producto,
                    cantidad,
                    precio_unitario: producto.precio_venta,
                    subtotal: cantidad * producto.precio_venta
                })
            }

            this.actualizarEstado({ carrito: nuevoCarrito })
            this.reproducirSonido('agregar')
            this.emitir('carrito:actualizado', nuevoCarrito)
            this.log(`➕ ${producto.descripcion} x${cantidad} agregado al carrito`)

        } catch (error) {
            this.manejarError('Error agregando producto', error)
        }
    }

    removerDelCarrito(indice: number) {
        try {
            const producto = this.estado.carrito[indice]?.producto
            if (!producto) return

            const nuevoCarrito = this.estado.carrito.filter((_, i) => i !== indice)
            this.actualizarEstado({ carrito: nuevoCarrito })
            
            this.reproducirSonido('remover')
            this.emitir('carrito:actualizado', nuevoCarrito)
            this.log(`➖ ${producto.descripcion} removido del carrito`)
        } catch (error) {
            this.manejarError('Error removiendo producto', error)
        }
    }

    actualizarCantidadItem(indice: number, nuevaCantidad: number) {
        try {
            if (nuevaCantidad <= 0) {
                this.removerDelCarrito(indice)
                return
            }

            const item = this.estado.carrito[indice]
            if (!item) return

            if (nuevaCantidad > item.producto.stock) {
                throw new Error(`Stock insuficiente. Disponible: ${item.producto.stock}`)
            }

            const nuevoCarrito = [...this.estado.carrito]
            nuevoCarrito[indice] = {
                ...item,
                cantidad: nuevaCantidad,
                subtotal: nuevaCantidad * item.precio_unitario
            }

            this.actualizarEstado({ carrito: nuevoCarrito })
            this.emitir('carrito:actualizado', nuevoCarrito)
        } catch (error) {
            this.manejarError('Error actualizando cantidad', error)
        }
    }

    limpiarCarrito() {
        this.actualizarEstado({ carrito: [] })
        this.emitir('carrito:limpiado')
        this.log('🧹 Carrito limpiado')
    }

    // PROPIEDADES CALCULADAS DEL CARRITO
    get totalCarrito(): number {
        return this.estado.carrito.reduce((total, item) => total + item.subtotal, 0)
    }

    get cantidadItemsCarrito(): number {
        return this.estado.carrito.reduce((total, item) => total + item.cantidad, 0)
    }

    // MÉTODOS DE VENTA
    async procesarVenta() {
        if (this.estado.carrito.length === 0) {
            throw new Error('El carrito está vacío')
        }

        try {
            this.actualizarEstado({ cargando: true, error: null })

            // Preparar datos de la venta
            const datosVenta = {
                id_cliente: this.estado.clienteSeleccionado?.id || 1, // Cliente genérico por defecto
                id_tipo_pago: 1, // Contado por defecto
                tipo_venta: 'CONTADO',
                monto_total: this.totalCarrito,
                detalles: this.estado.carrito.map(item => ({
                    id_producto: item.producto.id_producto,
                    cantidad: item.cantidad,
                    precio_unitario: item.precio_unitario,
                    subtotal_total: item.subtotal
                }))
            }

            // Enviar venta al backend
            const response = await api.post('/pos/ventas/', datosVenta)
            
            // Actualizar estado post-venta
            this.actualizarEstado({ 
                ventaActual: response,
                carrito: []
            })

            // Actualizar estadísticas
            await this.cargarEstadisticas()

            this.reproducirSonido('venta_exitosa')
            this.emitir('venta:procesada', response)
            this.log(`✅ Venta #${response.id_venta} procesada exitosamente`)

            return response
        } catch (error) {
            this.manejarError('Error procesando venta', error)
            throw error
        } finally {
            this.actualizarEstado({ cargando: false })
        }
    }

    nuevaVenta() {
        this.limpiarCarrito()
        this.actualizarEstado({ 
            clienteSeleccionado: null,
            ventaActual: null,
            error: null
        })
        this.emitir('venta:nueva')
        this.log('🆕 Nueva venta iniciada')
    }

    cancelarVenta() {
        if (this.estado.carrito.length > 0) {
            if (confirm('¿Está seguro de cancelar la venta actual?')) {
                this.nuevaVenta()
                this.emitir('venta:cancelada')
            }
        }
    }

    // MÉTODOS DE ESTADÍSTICAS
    async cargarEstadisticas() {
        try {
            const hoy = new Date().toISOString().split('T')[0]
            const response = await api.get(`/pos/ventas/estadisticas/?fecha_desde=${hoy}&fecha_hasta=${hoy}`)
            
            this.actualizarEstado({
                estadisticas: {
                    ventasHoy: response.generales.total_ventas || 0,
                    montoHoy: response.generales.total_monto || 0,
                    productosVendidos: response.generales.total_items || 0
                }
            })
        } catch (error) {
            this.log('⚠️ Error cargando estadísticas:', error)
        }
    }

    // MÉTODOS DE PERSISTENCIA LOCAL
    private guardarCarritoLocal() {
        try {
            localStorage.setItem('pos_carrito_backup', JSON.stringify({
                carrito: this.estado.carrito,
                timestamp: Date.now()
            }))
        } catch (error) {
            this.log('Error guardando carrito local:', error)
        }
    }

    private async recuperarCarritoGuardado() {
        try {
            const backup = localStorage.getItem('pos_carrito_backup')
            if (!backup) return

            const { carrito, timestamp } = JSON.parse(backup)
            
            // Solo recuperar si es reciente (menos de 1 hora)
            const unaHora = 60 * 60 * 1000
            if (Date.now() - timestamp > unaHora) {
                localStorage.removeItem('pos_carrito_backup')
                return
            }

            if (carrito?.length > 0) {
                const confirmar = confirm(
                    `Se encontró un carrito guardado con ${carrito.length} items. ¿Desea recuperarlo?`
                )
                
                if (confirmar) {
                    this.actualizarEstado({ carrito })
                    this.emitir('carrito:recuperado', carrito)
                    this.log('↩️ Carrito recuperado del almacenamiento local')
                }
            }
        } catch (error) {
            this.log('Error recuperando carrito:', error)
        }
    }

    // MÉTODOS DE INTERFAZ
    enfocarBusqueda() {
        const inputBusqueda = document.getElementById('product-search') as HTMLInputElement
        if (inputBusqueda) {
            inputBusqueda.focus()
            inputBusqueda.select()
        }
    }

    // MÉTODOS DE UTILIDAD
    private actualizarEstado(cambios: Partial<EstadoPOS>) {
        this.estado = { ...this.estado, ...cambios }
        this.emitir('estado:actualizado', this.estado)
    }

    private emitir(evento: string, datos?: any) {
        const listeners = this.listeners[evento] || []
        listeners.forEach(listener => listener(datos))

        // También emitir como evento DOM
        window.dispatchEvent(new CustomEvent(evento, { detail: datos }))
    }

    on(evento: string, callback: Function) {
        if (!this.listeners[evento]) {
            this.listeners[evento] = []
        }
        this.listeners[evento].push(callback)
    }

    private reproducirSonido(tipo: string) {
        if (!POS_CONFIG.SONIDOS_HABILITADOS) return
        
        try {
            const audio = new Audio(`/static/sounds/pos_${tipo}.mp3`)
            audio.volume = 0.3
            audio.play().catch(() => {}) // Ignorar errores de reproducción
        } catch (error) {
            // Ignorar errores de sonido
        }
    }

    private manejarError(mensaje: string, error: any) {
        const mensajeError = `${mensaje}: ${error?.message || error}`
        this.actualizarEstado({ error: mensajeError })
        this.emitir('error', mensajeError)
        this.log('❌ ' + mensajeError)
    }

    private log(mensaje: string) {
        console.log(`[POS] ${new Date().toLocaleTimeString()} - ${mensaje}`)
    }

    // API PÚBLICA
    getEstado() {
        return { ...this.estado }
    }

    destroy() {
        if (this.autoguardadoInterval) {
            clearInterval(this.autoguardadoInterval)
        }
        this.guardarCarritoLocal()
        this.listeners = {}
    }
}

// Función para crear componente Alpine.js del POS
export function crearComponentePOS() {
    return function() {
        return {
            // Estado local del componente
            sistema: null as SistemaPOS | null,
            productos: [],
            carrito: [],
            busqueda: '',
            loading: false,
            error: null,
            estadisticas: {
                ventasHoy: 0,
                montoHoy: 0,
                productosVendidos: 0
            },

            // Inicialización
            init() {
                this.sistema = new SistemaPOS()
                
                // Escuchar cambios de estado
                this.sistema.on('estado:actualizado', (estado) => {
                    this.productos = estado.productos
                    this.carrito = estado.carrito
                    this.loading = estado.cargando
                    this.error = estado.error
                    this.estadisticas = estado.estadisticas
                })

                // Configurar Alpine para reactividad
                this.$watch('busqueda', (valor) => {
                    this.buscarProductos(valor)
                })
            },

            // Métodos del componente
            async buscarProductos(termino) {
                if (!this.sistema) return
                
                try {
                    const resultados = await this.sistema.buscarProductos(termino)
                    this.productos = resultados
                } catch (error) {
                    console.error('Error buscando productos:', error)
                }
            },

            agregarProducto(producto) {
                this.sistema?.agregarAlCarrito(producto)
            },

            removerProducto(indice) {
                this.sistema?.removerDelCarrito(indice)
            },

            async procesarVenta() {
                try {
                    await this.sistema?.procesarVenta()
                    // Mostrar mensaje de éxito
                    alert('¡Venta procesada exitosamente!')
                } catch (error) {
                    alert('Error procesando venta: ' + error.message)
                }
            },

            nuevaVenta() {
                this.sistema?.nuevaVenta()
            },

            // Getters computados
            get totalCarrito() {
                return this.sistema?.totalCarrito || 0
            },

            get cantidadItems() {
                return this.sistema?.cantidadItemsCarrito || 0
            },

            get carritoVacio() {
                return this.carrito.length === 0
            }
        }
    }
}

// Registrar componente globalmente para Alpine.js
if (typeof window !== 'undefined') {
    (window as any).posSistema = crearComponentePOS()
}

export { SistemaPOS, POS_CONFIG }