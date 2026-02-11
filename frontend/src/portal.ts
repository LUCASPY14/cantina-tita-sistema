import './styles/main.css'

// Componente Portal básico
(window as any).Alpine?.data('portal', () => ({
  usuario: null,
  saldo: 0,
  loading: false,
  
  init() {
    this.cargarDatos()
  },
  
  async cargarDatos() {
    try {
      this.loading = true
      const response = await fetch('/api/portal/dashboard/')
      const data = await response.json()
      this.usuario = data.usuario
      this.saldo = data.saldo || 0
    } catch (error) {
      console.error('Error cargando datos portal:', error)
      this.mostrarNotificacion('error', 'Error', 'No se pudieron cargar los datos')
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

console.log('👤 Módulo Portal cargado')
