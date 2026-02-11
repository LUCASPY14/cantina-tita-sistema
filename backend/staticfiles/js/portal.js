
// PORTAL JS - JavaScript específico del portal de padres
document.addEventListener('DOMContentLoaded', function() {
    console.log('Portal de Padres inicializado');
    
    // Actualizar saldo automáticamente cada 30 segundos
    const saldoElement = document.querySelector('.saldo-amount');
    if (saldoElement) {
        setInterval(async () => {
            try {
                const response = await fetch('/gestion/api/portal/saldo/');
                const data = await response.json();
                if (data.saldo !== undefined) {
                    saldoElement.textContent = `Gs. ${data.saldo.toLocaleString()}`;
                }
            } catch (error) {
                console.log('Error actualizando saldo:', error);
            }
        }, 30000);
    }
    
    // Validación de formulario de recarga
    const recargaForm = document.querySelector('#recarga-form');
    if (recargaForm) {
        recargaForm.addEventListener('submit', function(e) {
            const monto = this.querySelector('[name="monto"]').value;
            if (!monto || monto < 5000) {
                e.preventDefault();
                showMessage('El monto mínimo de recarga es Gs. 5.000', 'error');
                return;
            }
            if (monto > 500000) {
                e.preventDefault();
                showMessage('El monto máximo de recarga es Gs. 500.000', 'error');
                return;
            }
        });
    }
    
    // Toggle para mostrar/ocultar movimientos
    document.querySelectorAll('[data-toggle-movimientos]').forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.dataset.toggleMovimientos;
            const target = document.getElementById(targetId);
            if (target) {
                target.style.display = target.style.display === 'none' ? 'block' : 'none';
                this.textContent = target.style.display === 'none' ? 'Ver Movimientos' : 'Ocultar Movimientos';
            }
        });
    });
});
