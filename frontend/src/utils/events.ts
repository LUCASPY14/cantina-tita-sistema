// Sistema de eventos simplificado
export class EventSystem {
  private listeners: Record<string, Function[]> = {}
  
  on(event: string, callback: Function) {
    if (!this.listeners[event]) {
      this.listeners[event] = []
    }
    this.listeners[event].push(callback)
  }
  
  emit(event: string, data?: any) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => callback(data))
    }
  }
}

export const eventSystem = new EventSystem()

// Validaciones básicas
export function validateRequired(value: any): boolean {
  return value !== null && value !== undefined && value !== ''
}

export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function validateRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max
}
