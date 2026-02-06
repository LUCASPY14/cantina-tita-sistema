
// BASE JS - JavaScript principal del sistema
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sistema POS inicializado');
    
    // Configurar CSRF para peticiones AJAX
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (csrfToken) {
        // Configurar CSRF para fetch requests
        const originalFetch = window.fetch;
        window.fetch = function(url, options = {}) {
            if (options.method && options.method.toUpperCase() !== 'GET') {
                options.headers = options.headers || {};
                options.headers['X-CSRFToken'] = csrfToken;
            }
            return originalFetch(url, options);
        };
    }
    
    // Función para mostrar mensajes
    window.showMessage = function(message, type = 'info') {
        const alertClass = {
            'success': 'alert-success',
            'error': 'alert-error', 
            'warning': 'alert-warning',
            'info': 'alert-info'
        }[type] || 'alert-info';
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert ${alertClass}`;
        alertDiv.textContent = message;
        
        // Insertar al inicio del contenido
        const container = document.querySelector('.container') || document.body;
        container.insertBefore(alertDiv, container.firstChild);
        
        // Remover después de 5 segundos
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    };
    
    // Confirmación para acciones peligrosas
    document.querySelectorAll('[data-confirm]').forEach(element => {
        element.addEventListener('click', function(e) {
            const message = this.dataset.confirm;
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });
    
    // Auto-submit para selects con data-auto-submit
    document.querySelectorAll('select[data-auto-submit]').forEach(select => {
        select.addEventListener('change', function() {
            this.form.submit();
        });
    });
});
