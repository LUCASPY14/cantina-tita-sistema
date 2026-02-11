// Tipos de UI simplificados
export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  timestamp: Date
}

export interface CarritoItem {
  producto_id: number
  nombre: string
  precio: number
  cantidad: number
  subtotal: number
}

export interface Carrito {
  items: CarritoItem[]
  total: number
  cantidad_items: number
}

export interface POSConfig {
  impresora_habilitada: boolean
  sonidos_habilitados: boolean
  modo_offline: boolean
}

export interface TableConfig {
  columns: string[]
  sortable: boolean
  paginated: boolean
}

export interface FormConfig {
  fields: string[]
  validation: Record<string, string[]>
}
