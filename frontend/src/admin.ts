import './styles/main.css'

// Componente Admin básico
(window as any).Alpine?.data('adminDashboard', () => ({
  stats: {
    ventas_hoy: 0,
    ingresos_hoy: 0,
    productos_bajo_stock: 0,
    clientes_activos: 0
  },
  loading: false,
  
  init() {
    this.cargarStats()
  },
  
  async cargarStats() {
    try {
      this.loading = true
      const response = await fetch('/api/admin/dashboard-stats/')
      const data = await response.json()
      this.stats = {
        ventas_hoy: data.ventas_hoy || 0,
        ingresos_hoy: data.ingresos_hoy || 0,
        productos_bajo_stock: data.productos_bajo_stock || 0,
        clientes_activos: data.clientes_activos || 0
      }
    } catch (error) {
      console.error('Error cargando stats:', error)
      this.mostrarNotificacion('error', 'Error', 'No se pudieron cargar los datos del dashboard')
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

console.log('⚡ Módulo Admin cargado')
