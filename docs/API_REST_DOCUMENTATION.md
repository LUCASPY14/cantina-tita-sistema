# 📚 Documentación API REST - Sistema Cantina Tita

## Información General

**Base URL:** `/api/v1/`  
**Autenticación:** Token-based (Django REST Framework)  
**Formato:** JSON  
**Versión:** 1.0.0  
**Fecha:** 3 de Diciembre, 2025

---

## 🔐 Autenticación

### Obtener Token

**Endpoint:** `POST /api/token/`

```json
{
  "username": "usuario",
  "password": "contraseña"
}
```

**Respuesta:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

### Uso del Token

Incluir en headers de todas las peticiones:
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

---

## 📦 Productos

### 1. Listar Categorías

**Endpoint:** `GET /api/v1/categorias/`

**Parámetros de búsqueda:**
- `activo` (boolean): Filtrar por activo/inactivo
- `search` (string): Buscar por nombre
- `ordering` (string): Ordenar por campos (nombre, id_categoria)

**Ejemplo:**
```
GET /api/v1/categorias/?activo=true&search=bebidas&ordering=nombre
```

**Respuesta:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id_categoria": 1,
      "nombre": "Bebidas",
      "activo": true,
      "id_categoria_padre": null
    }
  ]
}
```

### 2. Productos de una Categoría

**Endpoint:** `GET /api/v1/categorias/{id}/productos/`

**Respuesta:**
```json
[
  {
    "id_producto": 1,
    "codigo": "BEB001",
    "descripcion": "Coca Cola 500ml",
    "activo": true,
    "id_categoria": 1,
    "stock_minimo": 20
  }
]
```

### 3. Listar Productos

**Endpoint:** `GET /api/v1/productos/`

**Parámetros:**
- `activo` (boolean)
- `id_categoria` (int)
- `search` (string): Buscar en código o descripción
- `ordering` (string): codigo, descripcion

**Ejemplo:**
```
GET /api/v1/productos/?activo=true&id_categoria=1&search=coca
```

### 4. Detalle de Producto

**Endpoint:** `GET /api/v1/productos/{id}/`

**Respuesta (incluye stock y más detalles):**
```json
{
  "id_producto": 1,
  "codigo": "BEB001",
  "descripcion": "Coca Cola 500ml",
  "activo": true,
  "stock_minimo": 20,
  "id_categoria": {
    "id_categoria": 1,
    "nombre": "Bebidas"
  },
  "stock_actual": 45.0
}
```

### 5. Stock de Producto

**Endpoint:** `GET /api/v1/productos/{id}/stock/`

**Respuesta:**
```json
{
  "id_producto": 1,
  "stock_actual": 45.0,
  "fecha_ultima_actualizacion": "2025-12-03T10:30:00Z"
}
```

### 6. Productos con Stock Crítico

**Endpoint:** `GET /api/v1/productos/stock_critico/`

**Respuesta:**
```json
[
  {
    "id_producto": 5,
    "codigo": "BEB005",
    "descripcion": "Fanta 500ml",
    "stock_actual": 8.0,
    "stock_minimo": 20.0,
    "diferencia": 12.0
  }
]
```

### 7. Productos Más Vendidos

**Endpoint:** `GET /api/v1/productos/mas_vendidos/`

**Descripción:** Últimos 30 días

**Respuesta:**
```json
[
  {
    "id_producto__id_producto": 1,
    "id_producto__codigo": "BEB001",
    "id_producto__descripcion": "Coca Cola 500ml",
    "cantidad_vendida": 250,
    "total_ventas": 85
  }
]
```

---

## 👥 Clientes

### 1. Listar Clientes

**Endpoint:** `GET /api/v1/clientes/`

**Parámetros:**
- `activo` (boolean)
- `search` (string): nombres, apellidos, ci_ruc, telefono
- `ordering` (string): nombres, apellidos

**Ejemplo:**
```
GET /api/v1/clientes/?activo=true&search=González
```

**Respuesta:**
```json
{
  "count": 5,
  "results": [
    {
      "id_cliente": 1,
      "nombres": "María",
      "apellidos": "González",
      "ruc_ci": "1234567-8",
      "telefono": "0981234567",
      "activo": true,
      "limite_credito": 500000.0,
      "fecha_registro": "2025-01-15T10:00:00Z"
    }
  ]
}
```

### 2. Detalle de Cliente

**Endpoint:** `GET /api/v1/clientes/{id}/`

### 3. Hijos del Cliente

**Endpoint:** `GET /api/v1/clientes/{id}/hijos/`

**Respuesta:**
```json
[
  {
    "id_hijo": 1,
    "nombre": "Carlos",
    "apellido": "González",
    "fecha_nacimiento": "2015-03-20",
    "grado": "4to Grado",
    "id_cliente_responsable": 1
  }
]
```

### 4. Cuenta Corriente del Cliente

**Endpoint:** `GET /api/v1/clientes/{id}/cuenta_corriente/`

**Respuesta:**
```json
{
  "saldo_actual": 150000.0,
  "ventas_pendientes": [
    {
      "id_venta": 100,
      "fecha": "2025-12-01T14:30:00Z",
      "monto_total": 50000.0,
      "saldo_pendiente": 50000.0,
      "estado_pago": "PENDIENTE"
    }
  ]
}
```

### 5. Historial de Ventas

**Endpoint:** `GET /api/v1/clientes/{id}/ventas/`

---

## 💳 Tarjetas

### 1. Listar Tarjetas

**Endpoint:** `GET /api/v1/tarjetas/`

**Parámetros:**
- `estado` (string): ACTIVA, BLOQUEADA, CANCELADA
- `search` (string): nro_tarjeta, nombre/apellido del hijo

**Ejemplo:**
```
GET /api/v1/tarjetas/?estado=ACTIVA&search=1234
```

### 2. Detalle de Tarjeta (por número)

**Endpoint:** `GET /api/v1/tarjetas/{nro_tarjeta}/`

**Respuesta:**
```json
{
  "nro_tarjeta": "1234567890",
  "saldo_actual": 75000.0,
  "estado": "ACTIVA",
  "fecha_emision": "2025-01-15",
  "id_hijo": {
    "id_hijo": 1,
    "nombre": "Carlos",
    "apellido": "González",
    "grado": "4to Grado"
  }
}
```

### 3. Historial de Consumos

**Endpoint:** `GET /api/v1/tarjetas/{nro_tarjeta}/consumos/`

**Respuesta:**
```json
[
  {
    "id_consumo": 50,
    "fecha_consumo": "2025-12-03T12:30:00Z",
    "monto_consumido": 15000.0,
    "saldo_anterior": 75000.0,
    "saldo_posterior": 60000.0
  }
]
```

### 4. Historial de Recargas

**Endpoint:** `GET /api/v1/tarjetas/{nro_tarjeta}/recargas/`

**Respuesta:**
```json
[
  {
    "id_carga": 25,
    "fecha_carga": "2025-12-01T09:00:00Z",
    "monto_cargado": 100000.0,
    "id_cliente_origen": 1
  }
]
```

### 5. Recargar Tarjeta

**Endpoint:** `POST /api/v1/tarjetas/{nro_tarjeta}/recargar/`

**Body:**
```json
{
  "monto": 50000.0,
  "id_cliente_origen": 1
}
```

**Respuesta (201 Created):**
```json
{
  "id_carga": 26,
  "fecha_carga": "2025-12-03T15:30:00Z",
  "monto_cargado": 50000.0,
  "nro_tarjeta": "1234567890",
  "id_cliente_origen": 1
}
```

---

## 🛒 Ventas

### 1. Listar Ventas

**Endpoint:** `GET /api/v1/ventas/`

**Parámetros:**
- `estado` (string): Completada, Cancelada, Pendiente
- `tipo_venta` (string): CONTADO, CREDITO, TARJETA
- `id_tipo_pago` (int)
- `search` (string): nombres/apellidos del cliente
- `ordering` (string): fecha, monto_total

**Ejemplo:**
```
GET /api/v1/ventas/?estado=Completada&ordering=-fecha
```

**Respuesta:**
```json
{
  "count": 100,
  "results": [
    {
      "id_venta": 150,
      "fecha": "2025-12-03T14:30:00Z",
      "monto_total": 45000.0,
      "estado": "Completada",
      "tipo_venta": "CONTADO",
      "id_cliente": {
        "id_cliente": 1,
        "nombre_completo": "María González"
      },
      "id_empleado_cajero": {
        "id_empleado": 5,
        "nombre_completo": "Juan Pérez"
      }
    }
  ]
}
```

### 2. Detalle de Venta

**Endpoint:** `GET /api/v1/ventas/{id}/`

**Respuesta (incluye detalles de productos):**
```json
{
  "id_venta": 150,
  "fecha": "2025-12-03T14:30:00Z",
  "monto_total": 45000.0,
  "estado": "Completada",
  "tipo_venta": "CONTADO",
  "id_cliente": {...},
  "detalleventa_set": [
    {
      "id_detalle": 300,
      "id_producto": {
        "id_producto": 1,
        "codigo": "BEB001",
        "descripcion": "Coca Cola 500ml"
      },
      "cantidad": 3,
      "precio_unitario": 5000.0,
      "subtotal_total": 15000.0
    }
  ]
}
```

### 3. Ventas del Día

**Endpoint:** `GET /api/v1/ventas/ventas_dia/`

**Respuesta:**
```json
{
  "fecha": "2025-12-03",
  "cantidad_ventas": 25,
  "total_ventas": 850000.0,
  "ventas": [...]
}
```

### 4. Estadísticas de Ventas

**Endpoint:** `GET /api/v1/ventas/estadisticas/`

**Parámetros:**
- `fecha_inicio` (date): YYYY-MM-DD
- `fecha_fin` (date): YYYY-MM-DD

**Ejemplo:**
```
GET /api/v1/ventas/estadisticas/?fecha_inicio=2025-12-01&fecha_fin=2025-12-03
```

**Respuesta:**
```json
{
  "resumen": {
    "total_ventas": 100,
    "monto_total": 2500000.0,
    "monto_promedio": 25000.0
  },
  "por_estado": [
    {
      "estado": "Completada",
      "cantidad": 95,
      "monto": 2400000.0
    }
  ],
  "por_tipo": [
    {
      "tipo_venta": "CONTADO",
      "cantidad": 60,
      "monto": 1500000.0
    }
  ]
}
```

---

## 📊 Stock

### 1. Listar Stock

**Endpoint:** `GET /api/v1/stock/`

**Parámetros:**
- `search` (string): código o descripción del producto
- `ordering` (string): stock_actual, fecha_ultima_actualizacion

**Respuesta:**
```json
{
  "count": 50,
  "results": [
    {
      "id_producto": 1,
      "stock_actual": 45.0,
      "fecha_ultima_actualizacion": "2025-12-03T10:30:00Z",
      "producto": {
        "codigo": "BEB001",
        "descripcion": "Coca Cola 500ml"
      }
    }
  ]
}
```

### 2. Alertas de Stock

**Endpoint:** `GET /api/v1/stock/alertas/`

**Respuesta:**
```json
[
  {
    "id_producto": 5,
    "codigo": "BEB005",
    "descripcion": "Fanta 500ml",
    "stock_actual": 8.0,
    "stock_minimo": 20.0,
    "estado": "CRITICO"
  }
]
```

---

## 🔄 Operaciones CRUD

Todos los endpoints principales soportan:

### Crear (POST)
```
POST /api/v1/{recurso}/
Content-Type: application/json

{
  "campo1": "valor1",
  "campo2": "valor2"
}
```

### Actualizar Completo (PUT)
```
PUT /api/v1/{recurso}/{id}/
Content-Type: application/json

{
  "campo1": "valor_nuevo",
  "campo2": "valor_nuevo"
}
```

### Actualizar Parcial (PATCH)
```
PATCH /api/v1/{recurso}/{id}/
Content-Type: application/json

{
  "campo1": "valor_nuevo"
}
```

### Eliminar (DELETE)
```
DELETE /api/v1/{recurso}/{id}/
```

**Respuesta (204 No Content):**
```
(sin contenido)
```

---

## 📋 Paginación

Por defecto, las respuestas están paginadas:

```json
{
  "count": 150,
  "next": "http://api.example.com/api/v1/productos/?page=2",
  "previous": null,
  "results": [...]
}
```

**Parámetros:**
- `page` (int): Número de página
- `page_size` (int): Cantidad por página (máx: 100)

**Ejemplo:**
```
GET /api/v1/productos/?page=2&page_size=20
```

---

## 🔍 Filtros y Búsqueda

### Filtros Exactos
```
GET /api/v1/productos/?activo=true&id_categoria=1
```

### Búsqueda (SearchFilter)
```
GET /api/v1/productos/?search=coca
```

### Ordenamiento
```
GET /api/v1/ventas/?ordering=-fecha,monto_total
```

Prefijo `-` para orden descendente.

---

## ⚠️ Códigos de Estado HTTP

- **200 OK:** Petición exitosa
- **201 Created:** Recurso creado
- **204 No Content:** Eliminación exitosa
- **400 Bad Request:** Datos inválidos
- **401 Unauthorized:** Sin autenticación
- **403 Forbidden:** Sin permisos
- **404 Not Found:** Recurso no encontrado
- **500 Internal Server Error:** Error del servidor

---

## 🛠️ Ejemplos de Uso

### Python (requests)

```python
import requests

# Autenticación
response = requests.post('http://api.example.com/api/token/', json={
    'username': 'usuario',
    'password': 'contraseña'
})
token = response.json()['token']

# Usar token
headers = {'Authorization': f'Token {token}'}

# Listar productos
response = requests.get(
    'http://api.example.com/api/v1/productos/',
    headers=headers,
    params={'activo': True, 'search': 'coca'}
)
productos = response.json()['results']

# Crear venta
nueva_venta = {
    'id_cliente': 1,
    'tipo_venta': 'CONTADO',
    'monto_total': 25000
}
response = requests.post(
    'http://api.example.com/api/v1/ventas/',
    headers=headers,
    json=nueva_venta
)
```

### JavaScript (fetch)

```javascript
// Autenticación
const response = await fetch('http://api.example.com/api/token/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'usuario',
    password: 'contraseña'
  })
});
const { token } = await response.json();

// Listar productos
const productos = await fetch('http://api.example.com/api/v1/productos/?activo=true', {
  headers: { 'Authorization': `Token ${token}` }
}).then(r => r.json());

// Recargar tarjeta
await fetch('http://api.example.com/api/v1/tarjetas/1234567890/recargar/', {
  method: 'POST',
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    monto: 50000,
    id_cliente_origen: 1
  })
});
```

### cURL

```bash
# Obtener token
curl -X POST http://api.example.com/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"usuario","password":"contraseña"}'

# Listar ventas del día
curl -X GET "http://api.example.com/api/v1/ventas/ventas_dia/" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"

# Crear producto
curl -X POST http://api.example.com/api/v1/productos/ \
  -H "Authorization: Token TOKEN_AQUI" \
  -H "Content-Type: application/json" \
  -d '{
    "codigo": "BEB010",
    "descripcion": "Sprite 500ml",
    "activo": true,
    "id_categoria": 1,
    "stock_minimo": 20
  }'
```

---

## 📊 Resumen de Endpoints

| Recurso | Endpoint Base | Métodos | Custom Actions |
|---------|--------------|---------|----------------|
| **Categorías** | `/api/v1/categorias/` | GET, POST, PUT, PATCH, DELETE | `productos/`, `subcategorias/` |
| **Productos** | `/api/v1/productos/` | GET, POST, PUT, PATCH, DELETE | `stock/`, `stock_critico/`, `mas_vendidos/` |
| **Clientes** | `/api/v1/clientes/` | GET, POST, PUT, PATCH, DELETE | `hijos/`, `cuenta_corriente/`, `ventas/` |
| **Tarjetas** | `/api/v1/tarjetas/` | GET, POST, PUT, PATCH, DELETE | `consumos/`, `recargas/`, `recargar/` |
| **Ventas** | `/api/v1/ventas/` | GET, POST, PUT, PATCH, DELETE | `ventas_dia/`, `estadisticas/` |
| **Stock** | `/api/v1/stock/` | GET (solo lectura) | `alertas/` |

---

## 🔗 URLs Completas

**Base URL de producción:** `https://cantina-tita.com/api/v1/`  
**Base URL de desarrollo:** `http://localhost:8000/api/v1/`

### Endpoints Principales

```
# Autenticación
POST /api/token/

# Categorías
GET    /api/v1/categorias/
POST   /api/v1/categorias/
GET    /api/v1/categorias/{id}/
PUT    /api/v1/categorias/{id}/
PATCH  /api/v1/categorias/{id}/
DELETE /api/v1/categorias/{id}/
GET    /api/v1/categorias/{id}/productos/
GET    /api/v1/categorias/{id}/subcategorias/

# Productos
GET    /api/v1/productos/
POST   /api/v1/productos/
GET    /api/v1/productos/{id}/
PUT    /api/v1/productos/{id}/
PATCH  /api/v1/productos/{id}/
DELETE /api/v1/productos/{id}/
GET    /api/v1/productos/{id}/stock/
GET    /api/v1/productos/stock_critico/
GET    /api/v1/productos/mas_vendidos/

# Clientes
GET    /api/v1/clientes/
POST   /api/v1/clientes/
GET    /api/v1/clientes/{id}/
PUT    /api/v1/clientes/{id}/
PATCH  /api/v1/clientes/{id}/
DELETE /api/v1/clientes/{id}/
GET    /api/v1/clientes/{id}/hijos/
GET    /api/v1/clientes/{id}/cuenta_corriente/
GET    /api/v1/clientes/{id}/ventas/

# Tarjetas
GET    /api/v1/tarjetas/
POST   /api/v1/tarjetas/
GET    /api/v1/tarjetas/{nro_tarjeta}/
PUT    /api/v1/tarjetas/{nro_tarjeta}/
PATCH  /api/v1/tarjetas/{nro_tarjeta}/
DELETE /api/v1/tarjetas/{nro_tarjeta}/
GET    /api/v1/tarjetas/{nro_tarjeta}/consumos/
GET    /api/v1/tarjetas/{nro_tarjeta}/recargas/
POST   /api/v1/tarjetas/{nro_tarjeta}/recargar/

# Ventas
GET    /api/v1/ventas/
POST   /api/v1/ventas/
GET    /api/v1/ventas/{id}/
PUT    /api/v1/ventas/{id}/
PATCH  /api/v1/ventas/{id}/
DELETE /api/v1/ventas/{id}/
GET    /api/v1/ventas/ventas_dia/
GET    /api/v1/ventas/estadisticas/

# Stock
GET    /api/v1/stock/
GET    /api/v1/stock/{id}/
GET    /api/v1/stock/alertas/
```

---

## 📝 Notas Técnicas

1. **Formato de fechas:** ISO 8601 (`2025-12-03T14:30:00Z`)
2. **Moneda:** Guaraníes (Gs.) - valores numéricos sin separadores
3. **Codificación:** UTF-8
4. **Timezone:** UTC (convertir a local en cliente)
5. **Límite de requests:** 1000 peticiones/hora por token
6. **Tamaño máximo de payload:** 10 MB

---

## 🧪 Testing

### Postman Collection

Importar colección de Postman: [Descargar JSON](#)

### Swagger/OpenAPI

Documentación interactiva disponible en:
```
http://localhost:8000/api/docs/
```

---

## 📞 Soporte

**Desarrollador:** Sistema Cantina Tita  
**Email:** soporte@cantina-tita.com  
**Versión API:** 1.0.0  
**Última actualización:** 3 de Diciembre, 2025

---

**¡Gracias por usar la API de Cantina Tita!** 🎉
