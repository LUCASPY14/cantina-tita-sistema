// Tipos globales para la aplicación
export {}

declare global {
  interface Window {
    Alpine: any
    CantinaTita: {
      sounds: {
        success: any
        error: any 
        notification: any
      }
    }
    showNotification: (type: 'success' | 'error' | 'warning' | 'info', title: string, message: string) => void
    formatCurrency: (amount: number) => string
    formatDate: (date: string | Date) => string
  }

  // Alpine.js
  const Alpine: any
}

// Módulo alpinejs
declare module 'alpinejs' {
  const Alpine: any
  export default Alpine
}
