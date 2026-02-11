/**
 * PWA Install Prompt
 * Maneja la instalación de la Progressive Web App
 */

let deferredPrompt;
let installButton;

// Capturar el evento beforeinstallprompt
window.addEventListener('beforeinstallprompt', (e) => {
    console.log('[PWA] beforeinstallprompt event fired');
    
    // Prevenir que Chrome 67 y anteriores muestren el prompt automáticamente
    e.preventDefault();
    
    // Guardar el evento para usarlo después
    deferredPrompt = e;
    
    // Mostrar botón de instalación
    showInstallButton();
});

/**
 * Mostrar botón de instalación en la UI
 */
function showInstallButton() {
    // Buscar o crear el botón de instalación
    installButton = document.getElementById('pwa-install-btn');
    
    if (!installButton) {
        // Crear botón flotante si no existe
        installButton = createInstallButton();
        document.body.appendChild(installButton);
    }
    
    installButton.style.display = 'flex';
    installButton.addEventListener('click', installPWA);
}

/**
 * Crear botón de instalación flotante
 */
function createInstallButton() {
    const button = document.createElement('button');
    button.id = 'pwa-install-btn';
    button.className = 'btn btn-primary btn-circle fixed bottom-20 right-6 z-50 shadow-2xl hover:scale-110 transition-transform';
    button.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
    `;
    button.title = 'Instalar App';
    button.setAttribute('aria-label', 'Instalar aplicación');
    button.style.display = 'none';
    
    return button;
}

/**
 * Instalar PWA
 */
async function installPWA() {
    if (!deferredPrompt) {
        console.warn('[PWA] deferredPrompt no disponible');
        return;
    }
    
    // Ocultar botón
    installButton.style.display = 'none';
    
    // Mostrar el prompt de instalación
    deferredPrompt.prompt();
    
    // Esperar a que el usuario responda
    const { outcome } = await deferredPrompt.userChoice;
    
    console.log(`[PWA] User choice: ${outcome}`);
    
    if (outcome === 'accepted') {
        console.log('[PWA] Usuario aceptó la instalación');
        document.dispatchEvent(new CustomEvent('notify', {
            detail: { 
                message: 'Instalando aplicación...', 
                type: 'info' 
            }
        }));
    } else {
        console.log('[PWA] Usuario rechazó la instalación');
        // Volver a mostrar el botón después de un tiempo
        setTimeout(() => {
            installButton.style.display = 'flex';
        }, 60000); // 1 minuto
    }
    
    // Limpiar el prompt
    deferredPrompt = null;
}

/**
 * Verificar si la app ya está instalada
 */
function isAppInstalled() {
    // En modo standalone significa que está instalada
    if (window.matchMedia('(display-mode: standalone)').matches) {
        return true;
    }
    
    // En iOS Safari
    if (window.navigator.standalone === true) {
        return true;
    }
    
    return false;
}

/**
 * Mostrar indicador de modo offline/online
 */
function updateOnlineStatus() {
    const statusIndicator = document.getElementById('online-status');
    
    if (!statusIndicator) return;
    
    if (navigator.onLine) {
        statusIndicator.className = 'badge badge-success gap-2';
        statusIndicator.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            Online
        `;
    } else {
        statusIndicator.className = 'badge badge-warning gap-2';
        statusIndicator.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            Offline
        `;
    }
}

// Inicializar al cargar
window.addEventListener('load', () => {
    // Ocultar botón si ya está instalada
    if (isAppInstalled()) {
        console.log('[PWA] App ya está instalada');
        const btn = document.getElementById('pwa-install-btn');
        if (btn) btn.remove();
    }
    
    // Actualizar indicador de conexión
    updateOnlineStatus();
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
});

// Evento cuando la app se instala
window.addEventListener('appinstalled', () => {
    console.log('[PWA] App installed');
    
    // Ocultar botón de instalación
    if (installButton) {
        installButton.remove();
    }
    
    // Limpiar el prompt
    deferredPrompt = null;
    
    // Notificar al usuario
    document.dispatchEvent(new CustomEvent('notify', {
        detail: { 
            message: '¡App instalada exitosamente!', 
            type: 'success' 
        }
    }));
});

// Exportar funciones útiles
window.PWA = {
    install: installPWA,
    isInstalled: isAppInstalled,
    updateOnlineStatus: updateOnlineStatus
};
