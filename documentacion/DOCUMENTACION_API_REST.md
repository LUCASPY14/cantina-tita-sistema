# DOCUMENTACIÓN API REST
## Sistema de Gestión de Cantina Escolar "Tita"

**Versión API:** 1.0  
**Fecha:** Enero 2025  
**Base URL:** `https://cantina-tita.edu.py/api/v1/`

---

## ÍNDICE

1. [Introducción](#introducción)
2. [Autenticación](#autenticación)
3. [Endpoints - Portal de Padres](#endpoints---portal-de-padres)
4. [Endpoints - POS](#endpoints---pos)
5. [Endpoints - Almuerzos](#endpoints---almuerzos)
6. [Endpoints - Reportes](#endpoints---reportes)
7. [Modelos de Datos](#modelos-de-datos)
8. [Códigos de Error](#códigos-de-error)
9. [Ejemplos de Uso](#ejemplos-de-uso)
10. [Rate Limiting](#rate-limiting)

---

## INTRODUCCIÓN

La API REST de Cantina Tita permite integración con sistemas externos, desarrollo de aplicaciones móviles y automatización de procesos.

### Características

- Arquitectura RESTful
- Formato JSON para requests y responses
- Autenticación mediante Token
- Rate limiting para prevenir abuso
- Versionado de API (v1, v2, etc.)
- Documentación interactiva con Swagger

### Convenciones

- **Base URL**: `https://cantina-tita.edu.py/api/v1/`
- **Formato de fechas**: ISO 8601 (`2025-01-10T14:30:00Z`)
- **Moneda**: Guaraníes paraguayos (PYG)
- **Codificación**: UTF-8
- **Métodos HTTP**: GET, POST, PUT, PATCH, DELETE

---

## AUTENTICACIÓN

### Obtener Token de Acceso

**Endpoint**: `POST /api/v1/auth/login/`

**Request**:
```json
{
  "username": "1234567",
  "password": "mi_contraseña_segura"
}
```

**Response (200 OK)**:
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 123,
    "username": "1234567",
    "email": "juan.perez@email.com",
    "nombre_completo": "Juan Pérez",
    "tipo_usuario": "padre"
  },
  "expires_at": "2025-01-17T14:30:00Z"
}
```

### Usar Token en Requests

Incluir el token en el header de todas las peticiones:

```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### Renovar Token

**Endpoint**: `POST /api/v1/auth/refresh/`

**Headers**:
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

**Response (200 OK)**:
```json
{
  "token": "nuevo_token_1234567890abcdef",
  "expires_at": "2025-01-24T14:30:00Z"
}
```

### Cerrar Sesión

**Endpoint**: `POST /api/v1/auth/logout/`

**Response (200 OK)**:
```json
{
  "message": "Sesión cerrada exitosamente"
}
```

---

## ENDPOINTS - PORTAL DE PADRES

### 1. Listar Hijos del Usuario

**Endpoint**: `GET /api/v1/portal/hijos/`

**Headers**:
```
Authorization: Token [tu_token]
```

**Response (200 OK)**:
```json
{
  "count": 2,
  "results": [
    {
      "id": 245,
      "nombre": "María",
      "apellido": "Pérez",
      "nombre_completo": "María Pérez",
      "grado": "4to Grado",
      "tarjeta": {
        "numero": "00001234",
        "saldo_actual": 125000,
        "estado": "ACTIVA"
      },
      "foto_url": "https://cantina-tita.edu.py/media/fotos/hijo_245.jpg"
    },
    {
      "id": 246,
      "nombre": "Carlos",
      "apellido": "Pérez",
      "nombre_completo": "Carlos Pérez",
      "grado": "2do Grado",
      "tarjeta": {
        "numero": "00001235",
        "saldo_actual": 80000,
        "estado": "ACTIVA"
      },
      "foto_url": "https://cantina-tita.edu.py/media/fotos/hijo_246.jpg"
    }
  ]
}
```

### 2. Consultar Consumos de un Hijo

**Endpoint**: `GET /api/v1/portal/hijos/{id_hijo}/consumos/`

**Parámetros de Query**:
- `fecha_desde` (opcional): Fecha inicio (formato: YYYY-MM-DD)
- `fecha_hasta` (opcional): Fecha fin (formato: YYYY-MM-DD)
- `limit` (opcional): Cantidad de resultados (default: 20, max: 100)
- `offset` (opcional): Offset para paginación

**Ejemplo**: `GET /api/v1/portal/hijos/245/consumos/?fecha_desde=2025-01-01&fecha_hasta=2025-01-10&limit=50`

**Response (200 OK)**:
```json
{
  "count": 45,
  "next": "https://cantina-tita.edu.py/api/v1/portal/hijos/245/consumos/?offset=50",
  "previous": null,
  "results": [
    {
      "id": 3201,
      "fecha_consumo": "2025-01-10T14:30:00Z",
      "productos": [
        {
          "descripcion": "Almuerzo completo",
          "cantidad": 1,
          "precio_unitario": 15000,
          "subtotal": 15000
        },
        {
          "descripcion": "Jugo de naranja",
          "cantidad": 1,
          "precio_unitario": 5000,
          "subtotal": 5000
        }
      ],
      "monto_total": 20000,
      "saldo_anterior": 100000,
      "saldo_posterior": 80000
    }
  ],
  "resumen": {
    "total_consumido": 285000,
    "promedio_diario": 28500,
    "dias_con_consumo": 10
  }
}
```

### 3. Realizar Recarga de Saldo

**Endpoint**: `POST /api/v1/portal/recargas/`

**Request**:
```json
{
  "id_hijo": 245,
  "monto": 100000,
  "metodo_pago": "tarjeta",
  "datos_pago": {
    "numero_tarjeta": "4111111111111111",
    "titular": "Juan Perez",
    "vencimiento": "12/26",
    "cvv": "123"
  }
}
```

**Response (201 Created)**:
```json
{
  "id_transaccion": 456,
  "estado": "APROBADA",
  "id_hijo": 245,
  "monto": 100000,
  "comision": 0,
  "total": 100000,
  "metodo_pago": "tarjeta",
  "fecha_transaccion": "2025-01-10T15:30:00Z",
  "numero_recibo": "REC-2025-00145",
  "nuevo_saldo": 180000,
  "mensaje": "Recarga procesada exitosamente"
}
```

### 4. Configurar Restricciones

**Endpoint**: `POST /api/v1/portal/restricciones/`

**Request**:
```json
{
  "id_hijo": 245,
  "tipo_restriccion": "producto",
  "productos_bloqueados": [12, 15, 18],  // IDs de productos
  "categorias_bloqueadas": [3],  // IDs de categorías
  "limite_diario": 50000,
  "limite_semanal": 250000,
  "horarios_permitidos": {
    "lunes_viernes": [
      {"inicio": "09:30", "fin": "10:00"},
      {"inicio": "12:00", "fin": "14:00"}
    ],
    "sabados": [
      {"inicio": "08:00", "fin": "13:00"}
    ]
  }
}
```

**Response (201 Created)**:
```json
{
  "id": 89,
  "id_hijo": 245,
  "fecha_creacion": "2025-01-10T16:00:00Z",
  "activa": true,
  "mensaje": "Restricciones aplicadas exitosamente"
}
```

### 5. Consultar Historial de Recargas

**Endpoint**: `GET /api/v1/portal/recargas/`

**Parámetros**:
- `estado` (opcional): APROBADA, PENDIENTE, RECHAZADA
- `fecha_desde`, `fecha_hasta` (opcional)

**Response (200 OK)**:
```json
{
  "count": 12,
  "results": [
    {
      "id": 456,
      "fecha": "2025-01-10T15:30:00Z",
      "hijo": "Carlos Pérez",
      "monto": 100000,
      "metodo_pago": "tarjeta",
      "estado": "APROBADA",
      "recibo_url": "https://cantina-tita.edu.py/media/recibos/REC-2025-00145.pdf"
    }
  ]
}
```

---

## ENDPOINTS - POS

### 1. Buscar Producto por Código de Barras

**Endpoint**: `GET /api/v1/pos/productos/buscar/`

**Parámetros**:
- `codigo_barra` (requerido): Código de barras del producto

**Ejemplo**: `GET /api/v1/pos/productos/buscar/?codigo_barra=7891234567890`

**Response (200 OK)**:
```json
{
  "id": 123,
  "codigo_barra": "7891234567890",
  "descripcion": "Sándwich de jamón y queso",
  "categoria": "Snacks",
  "precio_venta": 8000,
  "stock_disponible": 45,
  "activo": true,
  "requiere_autorizacion": false,
  "foto_url": "https://cantina-tita.edu.py/media/productos/sandwich_jyq.jpg"
}
```

### 2. Verificar Tarjeta

**Endpoint**: `GET /api/v1/pos/tarjetas/{numero_tarjeta}/`

**Ejemplo**: `GET /api/v1/pos/tarjetas/00001234/`

**Response (200 OK)**:
```json
{
  "numero_tarjeta": "00001234",
  "estado": "ACTIVA",
  "hijo": {
    "id": 245,
    "nombre_completo": "María Pérez",
    "grado": "4to Grado",
    "foto_url": "https://cantina-tita.edu.py/media/fotos/hijo_245.jpg"
  },
  "saldo_actual": 125000,
  "restricciones": {
    "tiene_restricciones": true,
    "productos_bloqueados": [12, 15, 18],
    "limite_diario": 50000,
    "consumido_hoy": 15000,
    "disponible_hoy": 35000
  }
}
```

### 3. Registrar Venta con Tarjeta

**Endpoint**: `POST /api/v1/pos/ventas/`

**Request**:
```json
{
  "tipo_venta": "TARJETA",
  "nro_tarjeta": "00001234",
  "id_cajero": 5,
  "productos": [
    {
      "id_producto": 123,
      "cantidad": 1,
      "precio_unitario": 8000
    },
    {
      "id_producto": 45,
      "cantidad": 1,
      "precio_unitario": 5000
    }
  ],
  "observaciones": "Sin novedad"
}
```

**Response (201 Created)**:
```json
{
  "id_venta": 2451,
  "numero_venta": "V-2025-002451",
  "fecha": "2025-01-10T14:30:00Z",
  "tipo_venta": "TARJETA",
  "monto_total": 13000,
  "estado_pago": "PAGADO",
  "detalle": [
    {
      "producto": "Sándwich de jamón y queso",
      "cantidad": 1,
      "precio_unitario": 8000,
      "subtotal": 8000
    },
    {
      "producto": "Jugo de naranja",
      "cantidad": 1,
      "precio_unitario": 5000,
      "subtotal": 5000
    }
  ],
  "tarjeta": {
    "numero": "00001234",
    "saldo_anterior": 125000,
    "saldo_actual": 112000
  },
  "cajero": "María González",
  "mensaje": "Venta registrada exitosamente"
}
```

### 4. Registrar Venta en Efectivo

**Endpoint**: `POST /api/v1/pos/ventas/`

**Request**:
```json
{
  "tipo_venta": "CONTADO",
  "id_cajero": 5,
  "productos": [
    {
      "id_producto": 123,
      "cantidad": 2,
      "precio_unitario": 8000
    }
  ],
  "monto_recibido": 20000
}
```

**Response (201 Created)**:
```json
{
  "id_venta": 2452,
  "monto_total": 16000,
  "monto_recibido": 20000,
  "vuelto": 4000,
  "estado_pago": "PAGADO",
  "mensaje": "Venta en efectivo registrada"
}
```

### 5. Anular Venta

**Endpoint**: `POST /api/v1/pos/ventas/{id_venta}/anular/`

**Request**:
```json
{
  "motivo": "Cliente devolvió producto",
  "autorizado_por": 1  // ID del supervisor que autoriza
}
```

**Response (200 OK)**:
```json
{
  "id_venta": 2451,
  "estado": "ANULADA",
  "fecha_anulacion": "2025-01-10T15:00:00Z",
  "motivo": "Cliente devolvió producto",
  "saldo_reintegrado": 13000,
  "mensaje": "Venta anulada y saldo reintegrado"
}
```

---

## ENDPOINTS - ALMUERZOS

### 1. Consultar Menú del Día

**Endpoint**: `GET /api/v1/almuerzos/menu-del-dia/`

**Parámetros**:
- `fecha` (opcional): Formato YYYY-MM-DD (default: hoy)

**Response (200 OK)**:
```json
{
  "fecha": "2025-01-10",
  "dia_semana": "Viernes",
  "menu": {
    "entrada": "Sopa de verduras",
    "plato_principal": "Milanesa con puré",
    "guarnicion": "Ensalada mixta",
    "postre": "Fruta del día",
    "bebida": "Jugo natural"
  },
  "precio": 15000,
  "disponible": true,
  "cupos_disponibles": 45,
  "cupos_totales": 200
}
```

### 2. Inscribir Hijo a Almuerzos

**Endpoint**: `POST /api/v1/almuerzos/inscripciones/`

**Request**:
```json
{
  "id_hijo": 245,
  "fecha_inicio": "2025-01-13",
  "fecha_fin": "2025-01-31",
  "dias_semana": ["lunes", "martes", "miercoles", "jueves", "viernes"],
  "observaciones": "Sin gluten por favor"
}
```

**Response (201 Created)**:
```json
{
  "id_inscripcion": 89,
  "id_hijo": 245,
  "nombre_hijo": "María Pérez",
  "fecha_inicio": "2025-01-13",
  "fecha_fin": "2025-01-31",
  "dias_totales": 15,
  "monto_total": 225000,
  "estado": "ACTIVA",
  "mensaje": "Inscripción registrada. Total a pagar: ₲225.000"
}
```

### 3. Marcar Asistencia a Almuerzo

**Endpoint**: `POST /api/v1/almuerzos/asistencia/`

**Request**:
```json
{
  "id_hijo": 245,
  "fecha": "2025-01-10",
  "asistio": true,
  "hora_consumo": "13:15"
}
```

**Response (200 OK)**:
```json
{
  "id_asistencia": 456,
  "hijo": "María Pérez",
  "fecha": "2025-01-10",
  "asistio": true,
  "hora_consumo": "13:15:00",
  "mensaje": "Asistencia registrada"
}
```

---

## ENDPOINTS - REPORTES

### 1. Reporte de Ventas Diarias

**Endpoint**: `GET /api/v1/reportes/ventas-diarias/`

**Parámetros**:
- `fecha` (opcional): YYYY-MM-DD (default: hoy)

**Response (200 OK)**:
```json
{
  "fecha": "2025-01-10",
  "resumen": {
    "total_ventas": 1250000,
    "cantidad_transacciones": 145,
    "ticket_promedio": 8620
  },
  "por_forma_pago": {
    "efectivo": {
      "monto": 450000,
      "porcentaje": 36
    },
    "tarjeta": {
      "monto": 650000,
      "porcentaje": 52
    },
    "debito_credito": {
      "monto": 150000,
      "porcentaje": 12
    }
  },
  "top_productos": [
    {
      "producto": "Almuerzo completo",
      "cantidad": 85,
      "monto_total": 680000
    },
    {
      "producto": "Jugo de naranja",
      "cantidad": 45,
      "monto_total": 135000
    }
  ]
}
```

### 2. Reporte de Stock

**Endpoint**: `GET /api/v1/reportes/stock/`

**Parámetros**:
- `categoria` (opcional): Filtrar por categoría
- `bajo_stock` (opcional): true/false - solo productos con stock bajo

**Response (200 OK)**:
```json
{
  "fecha_reporte": "2025-01-10T16:00:00Z",
  "total_productos": 150,
  "valor_total_stock": 10360000,
  "alertas": {
    "stock_bajo": 12,
    "agotados": 3,
    "proximos_vencer": 5
  },
  "por_categoria": [
    {
      "categoria": "Bebidas",
      "cantidad_productos": 25,
      "stock_total": 850,
      "valor_total": 2125000
    }
  ],
  "productos_bajo_stock": [
    {
      "id": 45,
      "descripcion": "Coca Cola 500ml",
      "stock_actual": 8,
      "stock_minimo": 20,
      "estado": "BAJO"
    }
  ]
}
```

### 3. Exportar Reporte en Excel

**Endpoint**: `GET /api/v1/reportes/{tipo_reporte}/exportar/`

**Tipos de reporte**: `ventas`, `stock`, `consumos`, `financiero`

**Parámetros**:
- `fecha_desde`, `fecha_hasta` (opcional)
- `formato`: `excel` o `pdf`

**Response (200 OK)**:
```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="reporte_ventas_20250110.xlsx"

[Archivo Excel binario]
```

---

## MODELOS DE DATOS

### Cliente
```json
{
  "id_cliente": 123,
  "nombres": "Juan",
  "apellidos": "Pérez",
  "ruc_ci": "1234567-8",
  "email": "juan.perez@email.com",
  "telefono": "0981-123456",
  "direccion": "Av. España 123",
  "activo": true
}
```

### Hijo
```json
{
  "id_hijo": 245,
  "nombre": "María",
  "apellido": "Pérez",
  "grado": "4to Grado",
  "fecha_nacimiento": "2014-05-15",
  "id_cliente_responsable": 123,
  "foto_url": "https://..."
}
```

### Producto
```json
{
  "id_producto": 123,
  "codigo_barra": "7891234567890",
  "descripcion": "Sándwich de jamón y queso",
  "categoria": "Snacks",
  "precio_costo": 5000,
  "precio_venta": 8000,
  "stock_actual": 45,
  "stock_minimo": 10,
  "activo": true,
  "requiere_autorizacion": false
}
```

### Venta
```json
{
  "id_venta": 2451,
  "fecha": "2025-01-10T14:30:00Z",
  "tipo_venta": "TARJETA",
  "monto_total": 13000,
  "estado_pago": "PAGADO",
  "id_cajero": 5,
  "nro_tarjeta": "00001234"
}
```

### Tarjeta
```json
{
  "nro_tarjeta": "00001234",
  "id_hijo": 245,
  "saldo_actual": 125000,
  "estado": "ACTIVA",
  "tipo_autorizacion": "LIBRE",
  "fecha_emision": "2024-01-01"
}
```

---

## CÓDIGOS DE ERROR

### HTTP Status Codes

| Código | Significado | Descripción |
|--------|-------------|-------------|
| 200 | OK | Solicitud exitosa |
| 201 | Created | Recurso creado exitosamente |
| 204 | No Content | Exitoso pero sin contenido |
| 400 | Bad Request | Datos inválidos en request |
| 401 | Unauthorized | Token inválido o no proporcionado |
| 403 | Forbidden | Sin permisos para el recurso |
| 404 | Not Found | Recurso no encontrado |
| 429 | Too Many Requests | Rate limit excedido |
| 500 | Internal Server Error | Error del servidor |

### Respuestas de Error

**Formato estándar**:
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Usuario o contraseña incorrectos",
    "details": {
      "field": "password",
      "reason": "Contraseña inválida"
    }
  }
}
```

### Códigos de Error Personalizados

| Código | Descripción |
|--------|-------------|
| `INVALID_CREDENTIALS` | Credenciales incorrectas |
| `TOKEN_EXPIRED` | Token expirado |
| `INSUFFICIENT_BALANCE` | Saldo insuficiente |
| `PRODUCT_RESTRICTED` | Producto restringido para este usuario |
| `STOCK_UNAVAILABLE` | Sin stock disponible |
| `DAILY_LIMIT_EXCEEDED` | Límite diario excedido |
| `CARD_INACTIVE` | Tarjeta inactiva o bloqueada |
| `INVALID_AMOUNT` | Monto inválido |
| `DUPLICATE_TRANSACTION` | Transacción duplicada |
| `AUTHORIZATION_REQUIRED` | Se requiere autorización del padre |

**Ejemplo de error con saldo insuficiente**:
```json
{
  "error": {
    "code": "INSUFFICIENT_BALANCE",
    "message": "Saldo insuficiente para completar la compra",
    "details": {
      "saldo_actual": 5000,
      "monto_requerido": 13000,
      "diferencia": 8000
    }
  }
}
```

---

## EJEMPLOS DE USO

### Python (requests)

```python
import requests

# 1. Login
url = "https://cantina-tita.edu.py/api/v1/auth/login/"
data = {
    "username": "1234567",
    "password": "mi_password"
}
response = requests.post(url, json=data)
token = response.json()['token']

# 2. Consultar hijos
headers = {"Authorization": f"Token {token}"}
url = "https://cantina-tita.edu.py/api/v1/portal/hijos/"
response = requests.get(url, headers=headers)
hijos = response.json()['results']

# 3. Ver consumos del primer hijo
id_hijo = hijos[0]['id']
url = f"https://cantina-tita.edu.py/api/v1/portal/hijos/{id_hijo}/consumos/"
params = {
    "fecha_desde": "2025-01-01",
    "fecha_hasta": "2025-01-10"
}
response = requests.get(url, headers=headers, params=params)
consumos = response.json()['results']

print(f"Total consumido: {response.json()['resumen']['total_consumido']}")
```

### JavaScript (Fetch API)

```javascript
// 1. Login
const login = async () => {
  const response = await fetch('https://cantina-tita.edu.py/api/v1/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      username: '1234567',
      password: 'mi_password'
    })
  });
  
  const data = await response.json();
  return data.token;
};

// 2. Realizar recarga
const recargarSaldo = async (token, idHijo, monto) => {
  const response = await fetch('https://cantina-tita.edu.py/api/v1/portal/recargas/', {
    method: 'POST',
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      id_hijo: idHijo,
      monto: monto,
      metodo_pago: 'tarjeta',
      datos_pago: {
        numero_tarjeta: '4111111111111111',
        titular: 'Juan Perez',
        vencimiento: '12/26',
        cvv: '123'
      }
    })
  });
  
  return await response.json();
};

// Uso
const token = await login();
const recarga = await recargarSaldo(token, 245, 100000);
console.log(recarga.mensaje);
```

### cURL

```bash
# 1. Login
curl -X POST https://cantina-tita.edu.py/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"1234567","password":"mi_password"}'

# Respuesta: {"token":"9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",...}

# 2. Consultar hijos
curl -X GET https://cantina-tita.edu.py/api/v1/portal/hijos/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"

# 3. Registrar venta
curl -X POST https://cantina-tita.edu.py/api/v1/pos/ventas/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_venta": "TARJETA",
    "nro_tarjeta": "00001234",
    "id_cajero": 5,
    "productos": [
      {"id_producto": 123, "cantidad": 1, "precio_unitario": 8000}
    ]
  }'
```

---

## RATE LIMITING

Para prevenir abuso, la API implementa límites de tasa:

### Límites por Endpoint

| Endpoint | Límite |
|----------|--------|
| `/auth/login/` | 5 requests / minuto |
| `/portal/*` | 60 requests / minuto |
| `/pos/*` | 120 requests / minuto |
| `/reportes/*` | 30 requests / minuto |

### Headers de Rate Limit

Cada response incluye:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1641825600
```

### Respuesta cuando se excede el límite

**Status: 429 Too Many Requests**

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Demasiadas solicitudes. Intente nuevamente en 30 segundos.",
    "retry_after": 30
  }
}
```

---

## WEBHOOKS (Futuro)

*Funcionalidad en desarrollo para versión 2.0*

Permitirá recibir notificaciones en tiempo real de eventos:
- Recarga aprobada
- Consumo realizado
- Saldo bajo
- Restricción activada

---

## CHANGELOG

### v1.0 (Enero 2025)
- Lanzamiento inicial
- Endpoints de Portal de Padres
- Endpoints de POS
- Endpoints de Almuerzos
- Endpoints de Reportes
- Autenticación por Token

### Futuras versiones

**v1.1** (Planeado: Marzo 2025)
- Webhooks
- Notificaciones push
- Autenticación OAuth2

**v2.0** (Planeado: Junio 2025)
- GraphQL API
- WebSockets para tiempo real
- Soporte para múltiples instituciones

---

## SOPORTE

**Documentación Interactiva (Swagger)**:  
https://cantina-tita.edu.py/api/docs/

**Contacto para Desarrolladores**:  
Email: api@cantina-tita.edu.py  
Slack: #api-support

**Issues y Feature Requests**:  
GitHub: https://github.com/cantina-tita/api/issues

---

*Documentación API REST - Sistema Cantina Tita v1.0*  
*Última actualización: Enero 2025*  
*© 2025 - Todos los derechos reservados*
