// ==================== TIPOS DE EVENTOS ====================

// Eventos personalizados
export interface CustomEvent<T = any> {
  type: string;
  detail: T;
  timestamp: number;
}

// Eventos del POS
export interface POSEvents {
  'pos:producto-seleccionado': { producto: import('./api').Producto };
  'pos:carrito-actualizado': { carrito: import('./ui').Carrito };
  'pos:venta-completada': { venta: import('./api').Venta };
  'pos:cliente-seleccionado': { cliente: import('./api').Cliente };
  'pos:medio-pago-cambiado': { medio_pago: number };
}

// Eventos del Portal
export interface PortalEvents {
  'portal:saldo-actualizado': { cliente_id: number; nuevo_saldo: number };
  'portal:recarga-completada': { recarga: any };
  'portal:notificacion': { notification: import('./ui').Notification };
}

// Eventos generales
export interface GlobalEvents {
  'app:user-login': { user: import('./api').Usuario };
  'app:user-logout': {};
  'app:error': { error: Error | string };
  'app:loading': { loading: boolean };
  'app:notification': { notification: import('./ui').Notification };
}

// Union type de todos los eventos
export type AllEvents = POSEvents & PortalEvents & GlobalEvents;

// Tipo helper para eventos
export type EventMap = {
  [K in keyof AllEvents]: CustomEvent<AllEvents[K]>
};

// Event listener type
export type EventListener<T extends keyof AllEvents> = (event: EventMap[T]) => void;

// Event emitter interface
export interface EventEmitter {
  on<T extends keyof AllEvents>(event: T, listener: EventListener<T>): void;
  off<T extends keyof AllEvents>(event: T, listener: EventListener<T>): void;
  emit<T extends keyof AllEvents>(event: T, data: AllEvents[T]): void;
}
