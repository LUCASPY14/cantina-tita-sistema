"""
Componentes y helpers JavaScript para POS General
===================================================

Librería de funciones reutilizables para el POS:
- Formateo de moneda
- Manejo de alertas
- Validaciones
- Utilidades de UI
"""

// Configuración global del POS
const POSConfig = {
    API_BASE: '/gestion/pos/general/api',
    REFRESH_INTERVAL: 5000, // 5 segundos
    MAX_RESULTADOS_BUSQUEDA: 20,
    MEDIOS_PAGO: {
        1: { nombre: 'Efectivo', icon: '💵', requiere_referencia: false },
        2: { nombre: 'Tarjeta Débito', icon: '💳', requiere_referencia: true },
        3: { nombre: 'Tarjeta Crédito', icon: '💳', requiere_referencia: true },
        4: { nombre: 'Tarjeta Estudiante', icon: '🎓', requiere_referencia: true }
    },
    NIVELES_SEVERIDAD: {
        'BAJA': { color: '#10B981', icon: '🟢' },
        'MEDIA': { color: '#F59E0B', icon: '🟡' },
        'ALTA': { color: '#DC2626', icon: '🔴' }
    }
};

// Utilidades de formateo
const POSFormatters = {
    /**
     * Formatea un número en moneda Guaraníes
     * @param {number} monto - Monto a formatear
     * @returns {string} - Ej: "Gs. 1,234,567"
     */
    guaranies: (monto) => {
        if (!monto) monto = 0;
        return `Gs. ${Number(monto).toLocaleString('es-PY')}`;
    },
    
    /**
     * Formatea una fecha
     * @param {Date|string} fecha - Fecha a formatear
     * @returns {string} - Ej: "09/01/2026 14:30"
     */
    fecha: (fecha) => {
        const d = new Date(fecha);
        return d.toLocaleDateString('es-PY') + ' ' + d.toLocaleTimeString('es-PY', {hour: '2-digit', minute:'2-digit'});
    },
    
    /**
     * Formatea porcentaje
     * @param {number} valor - Valor entre 0-100
     * @returns {string} - Ej: "85.5%"
     */
    porcentaje: (valor) => {
        return `${Number(valor).toFixed(1)}%`;
    },
    
    /**
     * Trunca texto largo
     * @param {string} texto - Texto a truncar
     * @param {number} longitud - Longitud máxima
     * @returns {string} - Texto truncado con "..."
     */
    truncar: (texto, longitud = 50) => {
        if (!texto) return '';
        return texto.length > longitud ? texto.substring(0, longitud) + '...' : texto;
    }
};

// Utilidades de validación
const POSValidadores = {
    /**
     * Valida código de barras
     * @param {string} codigo - Código a validar
     * @returns {boolean}
     */
    codigoBarras: (codigo) => {
        return /^\d{8,20}$/.test(codigo.trim());
    },
    
    /**
     * Valida número de tarjeta
     * @param {string} tarjeta - Número de tarjeta
     * @returns {boolean}
     */
    tarjeta: (tarjeta) => {
        return /^\d{6,20}$/.test(tarjeta.trim());
    },
    
    /**
     * Valida cantidad
     * @param {number} cantidad - Cantidad a validar
     * @returns {boolean}
     */
    cantidad: (cantidad) => {
        const q = Number(cantidad);
        return q > 0 && q <= 999;
    },
    
    /**
     * Valida monto
     * @param {number} monto - Monto a validar
     * @returns {boolean}
     */
    monto: (monto) => {
        const m = Number(monto);
        return m > 0 && m <= 999999999;
    }
};

// Utilidades de HTTP/API
const POSHttp = {
    /**
     * Obtiene CSRF token del formulario
     * @returns {string} - CSRF token
     */
    getCSRFToken: () => {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    },
    
    /**
     * Realiza petición POST con autenticación
     * @param {string} endpoint - URL del endpoint (relativa a API_BASE)
     * @param {object} datos - Datos a enviar
     * @returns {Promise} - Response parseado como JSON
     */
    post: async (endpoint, datos) => {
        const url = `${POSConfig.API_BASE}${endpoint}`;
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': POSHttp.getCSRFToken()
            },
            body: JSON.stringify(datos)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response.json();
    },
    
    /**
     * Realiza petición GET
     * @param {string} endpoint - URL del endpoint
     * @returns {Promise} - Response parseado como JSON
     */
    get: async (endpoint) => {
        const response = await fetch(`${POSConfig.API_BASE}${endpoint}`);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response.json();
    }
};

// Utilidades de UI
const POSUI = {
    /**
     * Muestra una notificación toast
     * @param {string} mensaje - Mensaje a mostrar
     * @param {string} tipo - 'success', 'error', 'info', 'warning'
     * @param {number} duracion - Duración en ms (0 = permanente)
     */
    notificar: (mensaje, tipo = 'info', duracion = 3000) => {
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-error',
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[tipo] || 'alert-info';
        
        const icon = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }[tipo] || 'ℹ️';
        
        const html = `
            <div class="alert ${alertClass} shadow-lg mb-4 animate-pulse">
                <span>${icon} ${mensaje}</span>
            </div>
        `;
        
        // Insertar al inicio del contenedor principal
        const container = document.querySelector('[x-data="posGeneral()"]');
        if (container) {
            const div = document.createElement('div');
            div.innerHTML = html;
            container.insertBefore(div.firstElementChild, container.firstChild);
            
            if (duracion > 0) {
                setTimeout(() => {
                    div.firstElementChild.remove();
                }, duracion);
            }
        }
    },
    
    /**
     * Muestra un modal de confirmación
     * @param {string} titulo - Título del modal
     * @param {string} mensaje - Mensaje
     * @returns {Promise<boolean>} - true si confirma, false si cancela
     */
    confirmar: async (titulo, mensaje) => {
        return confirm(`${titulo}\n\n${mensaje}`);
    },
    
    /**
     * Reproduce sonido de alerta
     * @param {string} tipo - 'exito', 'error', 'alerta'
     */
    sonarAlerta: (tipo = 'alerta') => {
        try {
            const audios = {
                'exito': 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAAB9AAACABAAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBg==',
                'error': 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAAB9AAACABAAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBg==',
                'alerta': 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAAB9AAACABAAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBg=='
            };
            
            const audio = new Audio(audios[tipo] || audios['alerta']);
            audio.volume = 0.5;
            audio.play().catch(() => {});
        } catch (e) {
            console.log('No se pudo reproducir sonido');
        }
    },
    
    /**
     * Muestra un loading spinner
     * @param {string} mensaje - Mensaje a mostrar
     * @returns {function} - Función para cerrar el loading
     */
    mostrarLoading: (mensaje = 'Procesando...') => {
        const dialog = document.createElement('div');
        dialog.innerHTML = `
            <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" id="loading-overlay">
                <div class="bg-white rounded-lg p-8 text-center">
                    <div class="loading loading-spinner loading-lg text-primary mb-4"></div>
                    <p class="text-gray-600">${mensaje}</p>
                </div>
            </div>
        `;
        document.body.appendChild(dialog);
        
        return () => {
            document.getElementById('loading-overlay')?.remove();
        };
    }
};

// Utilidades de cálculo
const POSCalculos = {
    /**
     * Calcula el subtotal de una línea
     * @param {number} cantidad - Cantidad
     * @param {number} precio - Precio unitario
     * @returns {number} - Subtotal
     */
    subtotal: (cantidad, precio) => {
        return Math.round(quantity * precio);
    },
    
    /**
     * Calcula el cambio
     * @param {number} total - Total de la venta
     * @param {number} recibido - Monto recibido
     * @returns {number} - Cambio (puede ser negativo)
     */
    cambio: (total, recibido) => {
        return recibido - total;
    },
    
    /**
     * Calcula comisión
     * @param {number} monto - Monto de la venta
     * @param {number} porcentaje - Porcentaje de comisión
     * @param {number} monto_fijo - Monto fijo (opcional)
     * @returns {number} - Comisión
     */
    comision: (monto, porcentaje, monto_fijo = 0) => {
        return Math.round((monto * porcentaje / 100) + monto_fijo);
    },
    
    /**
     * Calcula impuesto
     * @param {number} monto - Monto base
     * @param {number} porcentaje - Porcentaje de impuesto
     * @returns {number} - Impuesto
     */
    impuesto: (monto, porcentaje) => {
        return Math.round(monto * porcentaje / 100);
    }
};
