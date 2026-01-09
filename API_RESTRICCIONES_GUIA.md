# 🔌 API de Restricciones Alimentarias - Guía de Uso
## Sistema Cantina Tita

---

## 📋 Descripción General

El sistema de matching automático proporciona 3 endpoints REST para verificar restricciones alimentarias de estudiantes en tiempo real.

**Base URL:** `/gestion/api/`  
**Autenticación:** Requiere `@login_required`  
**Formato:** JSON

---

## 🔍 Endpoint 1: Verificar Restricciones

Analiza un carrito de compras completo contra las restricciones del estudiante.

### Request

```http
POST /gestion/api/verificar-restricciones/
Content-Type: application/json
Authorization: Session Cookie (login required)
```

### Body

```json
{
  "tarjeta_codigo": "00203",
  "items": [
    {
      "producto_id": 1,
      "cantidad": 2
    },
    {
      "producto_id": 5,
      "cantidad": 1
    }
  ]
}
```

### Response (Success)

```json
{
  "success": true,
  "tiene_alertas": true,
  "puede_continuar": true,
  "requiere_autorizacion": true,
  "alertas": [
    {
      "producto_id": 5,
      "producto_nombre": "Empanada de Carne",
      "restriccion_tipo": "Vegetariano",
      "razon": "Contiene 'carne' en descripción",
      "nivel_confianza": 85,
      "severidad": "alta"
    }
  ],
  "estudiante": {
    "nombre": "Juan Pérez",
    "grado": "5to A"
  }
}
```

### Response (Error)

```json
{
  "success": false,
  "error": "Tarjeta no encontrada o inactiva"
}
```

### Códigos de Estado

- `200` - Success
- `400` - Bad Request (falta tarjeta_codigo)
- `404` - Tarjeta no encontrada
- `500` - Error del servidor

### Ejemplo de Uso (JavaScript)

```javascript
async function verificarRestricciones(nroTarjeta, items) {
  const response = await fetch('/gestion/api/verificar-restricciones/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
      tarjeta_codigo: nroTarjeta,
      items: items
    })
  });
  
  const data = await response.json();
  
  if (data.success && data.tiene_alertas) {
    // Mostrar alertas al usuario
    mostrarAlertas(data.alertas);
    
    if (data.requiere_autorizacion) {
      // Solicitar autorización
      return await solicitarAutorizacion();
    }
  }
  
  return data.puede_continuar;
}
```

### Ejemplo de Uso (Python)

```python
import requests

def verificar_restricciones(tarjeta, items):
    url = 'http://localhost:8000/gestion/api/verificar-restricciones/'
    
    data = {
        'tarjeta_codigo': tarjeta,
        'items': items
    }
    
    response = requests.post(url, json=data)
    resultado = response.json()
    
    if resultado['success'] and resultado['tiene_alertas']:
        for alerta in resultado['alertas']:
            print(f"⚠️ {alerta['producto_nombre']}: {alerta['razon']}")
            print(f"   Severidad: {alerta['severidad']}")
            print(f"   Confianza: {alerta['nivel_confianza']}%")
    
    return resultado['puede_continuar']
```

---

## 🛡️ Endpoint 2: Obtener Productos Seguros

Retorna una lista de productos seguros para un estudiante específico.

### Request

```http
GET /gestion/api/productos-seguros/00203/
Authorization: Session Cookie (login required)
```

### Query Parameters

- `categoria_id` (opcional): Filtrar por categoría

### Response (Success)

```json
{
  "success": true,
  "total": 15,
  "productos": [
    {
      "id": 1,
      "codigo": "7890123456789",
      "descripcion": "Ensalada de Frutas",
      "categoria": "Postres",
      "precio": 15000
    },
    {
      "id": 3,
      "codigo": "7890123456790",
      "descripcion": "Jugo Natural de Naranja",
      "categoria": "Bebidas",
      "precio": 8000
    }
  ]
}
```

### Response (Error)

```json
{
  "success": false,
  "error": "Tarjeta sin hijo asociado"
}
```

### Códigos de Estado

- `200` - Success
- `400` - Tarjeta sin hijo
- `404` - Tarjeta no encontrada
- `500` - Error del servidor

### Ejemplo de Uso (JavaScript)

```javascript
async function cargarProductosSeguros(nroTarjeta) {
  const response = await fetch(`/gestion/api/productos-seguros/${nroTarjeta}/`);
  const data = await response.json();
  
  if (data.success) {
    const productosDiv = document.getElementById('productos-seguros');
    
    data.productos.forEach(producto => {
      const card = `
        <div class="producto-card">
          <h3>${producto.descripcion}</h3>
          <p>Categoría: ${producto.categoria}</p>
          <p>Precio: Gs. ${producto.precio.toLocaleString('es-PY')}</p>
          <button onclick="agregarAlCarrito(${producto.id})">
            Agregar al carrito
          </button>
        </div>
      `;
      productosDiv.innerHTML += card;
    });
  }
}
```

---

## 💡 Endpoint 3: Sugerir Alternativas

Sugiere productos alternativos seguros cuando se detecta un conflicto.

### Request

```http
POST /gestion/api/sugerir-alternativas/
Content-Type: application/json
Authorization: Session Cookie (login required)
```

### Body

```json
{
  "tarjeta_codigo": "00203",
  "producto_id": 5
}
```

### Response (Success)

```json
{
  "success": true,
  "total": 3,
  "producto_original": "Empanada de Carne",
  "alternativas": [
    {
      "id": 12,
      "codigo": "7890123456791",
      "descripcion": "Empanada de Verduras",
      "categoria": "Almuerzos",
      "precio": 12000
    },
    {
      "id": 15,
      "codigo": "7890123456792",
      "descripcion": "Wrap Vegetariano",
      "categoria": "Almuerzos",
      "precio": 15000
    },
    {
      "id": 18,
      "codigo": "7890123456793",
      "descripcion": "Ensalada Completa",
      "categoria": "Almuerzos",
      "precio": 18000
    }
  ]
}
```

### Response (Error)

```json
{
  "success": false,
  "error": "Producto no encontrado"
}
```

### Códigos de Estado

- `200` - Success
- `404` - Tarjeta o producto no encontrado
- `500` - Error del servidor

### Ejemplo de Uso (JavaScript)

```javascript
async function sugerirAlternativas(nroTarjeta, productoId) {
  const response = await fetch('/gestion/api/sugerir-alternativas/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken')
    },
    body: JSON.stringify({
      tarjeta_codigo: nroTarjeta,
      producto_id: productoId
    })
  });
  
  const data = await response.json();
  
  if (data.success && data.total > 0) {
    const mensaje = `
      <div class="alert alert-warning">
        <h4>⚠️ Producto con restricción detectado</h4>
        <p>El producto "${data.producto_original}" puede no ser adecuado.</p>
        <h5>Te sugerimos estas alternativas:</h5>
        <ul>
          ${data.alternativas.map(alt => `
            <li>
              ${alt.descripcion} - Gs. ${alt.precio.toLocaleString('es-PY')}
              <button onclick="reemplazarProducto(${productoId}, ${alt.id})">
                Reemplazar
              </button>
            </li>
          `).join('')}
        </ul>
      </div>
    `;
    
    mostrarModal(mensaje);
  }
}
```

---

## 🎨 Integración con POS (Alpine.js)

### Verificación Automática al Escanear Tarjeta

```html
<div x-data="posData()">
  <!-- Input de tarjeta -->
  <input 
    type="text" 
    x-model="tarjetaCodigo"
    @change="verificarRestriccionesAutomatico()"
    placeholder="Escanear tarjeta"
  >
  
  <!-- Alertas -->
  <div x-show="alertas.length > 0" class="alert alert-warning">
    <h4>⚠️ Restricciones Alimentarias Detectadas</h4>
    <template x-for="alerta in alertas">
      <div class="alerta-item" :class="'severidad-' + alerta.severidad">
        <strong x-text="alerta.producto_nombre"></strong>
        <p x-text="alerta.razon"></p>
        <span x-text="'Confianza: ' + alerta.nivel_confianza + '%'"></span>
      </div>
    </template>
    
    <button 
      x-show="requiereAutorizacion"
      @click="solicitarAutorizacion()"
      class="btn btn-warning"
    >
      Solicitar Autorización
    </button>
  </div>
</div>

<script>
function posData() {
  return {
    tarjetaCodigo: '',
    carrito: [],
    alertas: [],
    requiereAutorizacion: false,
    
    async verificarRestriccionesAutomatico() {
      if (!this.tarjetaCodigo || this.carrito.length === 0) return;
      
      const items = this.carrito.map(item => ({
        producto_id: item.id,
        cantidad: item.cantidad
      }));
      
      const response = await fetch('/gestion/api/verificar-restricciones/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCsrfToken()
        },
        body: JSON.stringify({
          tarjeta_codigo: this.tarjetaCodigo,
          items: items
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        this.alertas = data.alertas || [];
        this.requiereAutorizacion = data.requiere_autorizacion;
        
        if (data.tiene_alertas) {
          this.mostrarNotificacion(
            `Se detectaron ${this.alertas.length} posibles restricciones`,
            'warning'
          );
        }
      }
    },
    
    async agregarProducto(producto) {
      this.carrito.push(producto);
      await this.verificarRestriccionesAutomatico();
    },
    
    getCsrfToken() {
      return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
  }
}
</script>
```

---

## 🔒 Seguridad

### Autenticación
Todos los endpoints requieren autenticación de Django (`@login_required`).

### CSRF Protection
Incluir token CSRF en todas las peticiones POST:

```javascript
headers: {
  'X-CSRFToken': getCookie('csrftoken')
}
```

### Validación de Datos
- Tarjeta debe estar activa
- Productos deben existir en la base de datos
- IDs deben ser numéricos válidos

---

## 📊 Niveles de Severidad

Las alertas se clasifican en 3 niveles:

| Nivel | Confianza | Color | Acción |
|-------|-----------|-------|--------|
| 🔴 Alta | ≥80% | Rojo | Autorización obligatoria |
| 🟡 Media | 60-79% | Amarillo | Autorización requerida |
| 🟢 Baja | 50-59% | Verde | Informativa |

---

## 🐛 Manejo de Errores

### Errores Comunes

```javascript
// Tarjeta no encontrada
{
  "success": false,
  "error": "Tarjeta no encontrada o inactiva"
}

// Falta parámetro
{
  "success": false,
  "error": "Código de tarjeta requerido"
}

// Tarjeta sin hijo
{
  "success": false,
  "error": "Tarjeta sin hijo asociado"
}

// Error del servidor
{
  "success": false,
  "error": "Internal server error message"
}
```

### Manejo Recomendado

```javascript
try {
  const response = await fetch(url, options);
  const data = await response.json();
  
  if (!data.success) {
    console.error('Error:', data.error);
    mostrarError(data.error);
    return null;
  }
  
  return data;
  
} catch (error) {
  console.error('Error de red:', error);
  mostrarError('Error de conexión con el servidor');
  return null;
}
```

---

## 📞 Soporte

**Documentación completa:** Ver `MEJORAS_IMPLEMENTADAS.md`  
**Tests:** Ejecutar `python test_restricciones_matcher.py`  
**Código fuente:** `gestion/restricciones_matcher.py` y `gestion/restricciones_api.py`

---

*Guía actualizada: 8 de Enero, 2026*
