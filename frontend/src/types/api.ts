// Tipos de API completos para Sistema POS
export interface Usuario {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
}

export interface Cliente {
  id: number
  nombre: string
  email?: string
  telefono?: string
  saldo: number
}

export interface Producto {
  id_producto: number
  codigo_producto: string
  codigo_barras?: string
  descripcion: string
  precio_venta: number
  precio_display: string
  stock: number
  stock_minimo: number
  stock_status: 'sin_stock' | 'stock_bajo' | 'disponible'
  id_categoria: number
  categoria_nombre: string
  unidad_medida: string
  activo: boolean
  fecha_vencimiento?: string
  imagen?: string
}

export interface CarritoItem {
  producto: Producto
  cantidad: number
  precio_unitario: number
  subtotal: number
}

export interface VentaItem {
  id_detalle?: number
  id_producto: number
  producto_nombre?: string
  producto_codigo?: string
  cantidad: number
  precio_unitario: number
  subtotal_total: number
}

export interface Venta {
  id_venta: number
  nro_factura_venta?: number
  id_cliente: number
  cliente_nombre?: string
  id_empleado_cajero: number
  cajero_nombre?: string
  fecha: string
  monto_total: number
  saldo_pendiente?: number
  estado_pago: 'PENDIENTE' | 'PARCIAL' | 'PAGADA'
  estado: 'PROCESADO' | 'ANULADO'
  tipo_venta: 'CONTADO' | 'CREDITO'
  detalles?: VentaItem[]
  total_pagado?: number
  porcentaje_pagado?: number
}

export interface PagoVenta {
  id_pago_venta: number
  id_venta: number
  id_medio_pago: number
  medio_pago_nombre?: string
  monto_aplicado: number
  referencia_transaccion?: string
  fecha_pago: string
  estado: string
}

export interface Categoria {
  id_categoria: number
  descripcion: string
  activo: boolean
}

export interface MedioPago {
  id_medio_pago: number
  nombre_medio_pago: string
  requiere_referencia: boolean
  activo: boolean
}

export interface Empleado {
  id_empleado: number
  nombre_completo: string
  cargo?: string
  activo: boolean
}

export interface Almuerzo {
  id: number
  fecha: string
  cliente: Cliente
  precio: number
  pagado: boolean
}

export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
}

export interface ApiError {
  error: string
  details?: string
  code?: number
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  user: Usuario
}
