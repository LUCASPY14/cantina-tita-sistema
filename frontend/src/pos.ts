import './styles/main.css'

// Componente POS básico
(window as any).Alpine?.data('pos', () => ({
  productos: [],
  carrito: { items: [], total: 0 },
  loading: false,
  
  init() {
    this.cargarProductos()
  },
  
  async cargarProductos() {
    try {
      this.loading = true
      const response = await fetch('/api/pos/productos/')
      const data = await response.json()
      this.productos = data.results || []
    } catch (error) {
      console.error('Error cargando productos:', error)
      this.mostrarNotificacion('error', 'Error', 'No se pudieron cargar los productos')
    } finally {
      this.loading = false
    }
  },
  
  mostrarNotificacion(type: string, title: string, message: string) {
    if ((window as any).showNotification) {
      (window as any).showNotification(type, title, message)
    }
  }
}))

console.log('📊 Módulo POS cargado')
