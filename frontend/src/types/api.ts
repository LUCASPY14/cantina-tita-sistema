// Tipos de API simplificados
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
  id: number
  nombre: string
  precio: number
  stock_actual: number
  categoria?: string
  activo: boolean
}

export interface Venta {
  id: number
  numero: string
  cliente?: Cliente
  items: VentaItem[]
  total: number
  fecha: string
}

export interface VentaItem {
  producto: Producto
  cantidad: number
  precio_unitario: number
  subtotal: number
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
