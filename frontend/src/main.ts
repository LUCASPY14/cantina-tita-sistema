// Importaciones
import './styles/main.css'
import { audioManager } from './utils/audio'
import { eventSystem } from './utils/events'
import { formatCurrency, formatDate } from './utils/formatters'
import Alpine from 'alpinejs'

// Import types properly
import type { Usuario } from './types/api'
import type { Notification } from './types/ui'

// HTMX para interactividad
import 'htmx.org'

// Configuración de Alpine.js
(window as any).Alpine = Alpine
if (Alpine.start) {
  Alpine.start()
} else {
  console.log('Alpine started')
}

// API global CantinaTita
const cantinaTitaAPI = {
  // Sistema de sonidos
  sounds: {
    success: audioManager.createSound('/static/sounds/success.mp3'),
    error: audioManager.createSound('/static/sounds/error.mp3'),
    notification: audioManager.createSound('/static/sounds/notification.mp3')
  },
  
  // Eventos del sistema
  events: eventSystem,
  
  // Utilidades
  utils: {
    formatCurrency,
    formatDate
  },
  
  // Estado global
  state: {
    user: null as Usuario | null,
    notifications: [] as Notification[]
  }
};

(window as any).CantinaTita = cantinaTitaAPI;

// Sistema de notificaciones global
function playNotificationSound(type: string) {
  try {
    switch (type) {
      case 'success':
        (window as any).CantinaTita.sounds.success.play()
        break
      case 'error':
        (window as any).CantinaTita.sounds.error.play()
        break
      default:
        (window as any).CantinaTita.sounds.notification.play()
    }
  } catch (error) {
    console.log('Audio not available:', error)
  }
}

// Crear elemento de notificación
function createNotificationElement(type: string, title: string, message: string) {
  const notification = document.createElement('div')
  notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full ${
    type === 'success' ? 'bg-green-500 text-white' :
    type === 'error' ? 'bg-red-500 text-white' :
    type === 'warning' ? 'bg-yellow-500 text-black' :
    'bg-blue-500 text-white'
  }`
  
  notification.innerHTML = `
    <div class="flex items-center">
      <div class="flex-1">
        <h4 class="font-medium">${title}</h4>
        <p class="text-sm opacity-90">${message}</p>
      </div>
      <button class="ml-4 text-lg opacity-70 hover:opacity-100">&times;</button>
    </div>
  `
  
  return notification
}

// Función global de notificaciones
(window as any).showNotification = (type: 'success' | 'error' | 'warning' | 'info', title: string, message: string) => {
  playNotificationSound(type)
  
  const notification = createNotificationElement(type, title, message)
  document.body.appendChild(notification)
  
  // Animar entrada
  setTimeout(() => notification.classList.remove('translate-x-full'), 100)
  
  // Auto-remove
  const removeNotification = () => {
    notification.classList.add('translate-x-full')
    setTimeout(() => notification.remove(), 300)
  }
  
  // Botón cerrar
  notification.querySelector('button')?.addEventListener('click', removeNotification)
  
  // Auto-remove después de 5 segundos
  setTimeout(removeNotification, 5000)
}

// Utilidades globales
(window as any).formatCurrency = formatCurrency;
(window as any).formatDate = formatDate

// Log de inicio
console.log('🚀 Cantina Tita Frontend iniciado')
