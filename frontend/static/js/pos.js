
// POS JS - JavaScript del sistema de punto de venta
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sistema POS inicializado');
    
    // Variables globales del POS
    window.ventaActual = {
        items: [],
        total: 0,
        tarjeta: null
    };
    
    // Función para agregar producto a la venta
    window.agregarProducto = function(productoId, nombre, precio) {
        const item = window.ventaActual.items.find(i => i.id === productoId);
        if (item) {
            item.cantidad += 1;
        } else {
            window.ventaActual.items.push({
                id: productoId,
                nombre: nombre,
                precio: parseFloat(precio),
                cantidad: 1
            });
        }
        actualizarVenta();
    };
    
    // Función para remover producto de la venta
    window.removerProducto = function(productoId) {
        const index = window.ventaActual.items.findIndex(i => i.id === productoId);
        if (index > -1) {
            window.ventaActual.items.splice(index, 1);
            actualizarVenta();
        }
    };
    
    // Función para actualizar la visualización de la venta
    function actualizarVenta() {
        const ventaContainer = document.querySelector('#venta-items');
        const totalContainer = document.querySelector('#venta-total');
        
        if (!ventaContainer || !totalContainer) return;
        
        // Limpiar items actuales
        ventaContainer.innerHTML = '';
        
        // Agregar items de la venta
        let total = 0;
        window.ventaActual.items.forEach(item => {
            const subtotal = item.precio * item.cantidad;
            total += subtotal;
            
            const itemDiv = document.createElement('div');
            itemDiv.className = 'venta-item';
            itemDiv.innerHTML = `
                <div>
                    <strong>${item.nombre}</strong><br>
                    <small>Gs. ${item.precio.toLocaleString()} x ${item.cantidad}</small>
                </div>
                <div>
                    <span>Gs. ${subtotal.toLocaleString()}</span>
                    <button type="button" onclick="removerProducto(${item.id})" class="btn btn-danger btn-sm ml-2">×</button>
                </div>
            `;
            ventaContainer.appendChild(itemDiv);
        });
        
        window.ventaActual.total = total;
        totalContainer.textContent = `Gs. ${total.toLocaleString()}`;
        
        // Actualizar botón de procesamiento
        const procesarBtn = document.querySelector('#procesar-venta');
        if (procesarBtn) {
            procesarBtn.disabled = window.ventaActual.items.length === 0 || !window.ventaActual.tarjeta;
        }
    }
    
    // Función para buscar tarjeta
    window.buscarTarjeta = async function(codigo) {
        try {
            const response = await fetch(`/pos/buscar-tarjeta/?codigo=${codigo}`);
            const data = await response.json();
            
            if (data.success) {
                window.ventaActual.tarjeta = data.tarjeta;
                document.querySelector('#tarjeta-info').innerHTML = `
                    <h4>Tarjeta: ${data.tarjeta.codigo}</h4>
                    <p>Cliente: ${data.tarjeta.cliente_nombre}</p>
                    <p class="saldo-disponible">Saldo: Gs. ${data.tarjeta.saldo.toLocaleString()}</p>
                `;
                actualizarVenta();
            } else {
                showMessage(data.error || 'Tarjeta no encontrada', 'error');
            }
        } catch (error) {
            showMessage('Error al buscar tarjeta', 'error');
        }
    };
    
    // Función para procesar venta
    window.procesarVenta = async function() {
        if (!window.ventaActual.tarjeta || window.ventaActual.items.length === 0) {
            showMessage('Debe seleccionar una tarjeta y productos', 'error');
            return;
        }
        
        try {
            const response = await fetch('/pos/venta/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    tarjeta_id: window.ventaActual.tarjeta.id,
                    items: window.ventaActual.items
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showMessage('Venta procesada exitosamente', 'success');
                // Limpiar venta
                window.ventaActual = { items: [], total: 0, tarjeta: null };
                document.querySelector('#tarjeta-info').innerHTML = '';
                actualizarVenta();
            } else {
                showMessage(data.error || 'Error al procesar venta', 'error');
            }
        } catch (error) {
            showMessage('Error al procesar venta', 'error');
        }
    };
    
    // Event listeners para productos
    document.querySelectorAll('.producto-card').forEach(card => {
        card.addEventListener('click', function() {
            const id = this.dataset.productoId;
            const nombre = this.dataset.productoNombre;
            const precio = this.dataset.productoPrecio;
            agregarProducto(id, nombre, precio);
        });
    });
    
    // Event listener para búsqueda de tarjeta
    const codigoInput = document.querySelector('#codigo-tarjeta');
    if (codigoInput) {
        codigoInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                buscarTarjeta(this.value);
                this.value = '';
            }
        });
    }
});
