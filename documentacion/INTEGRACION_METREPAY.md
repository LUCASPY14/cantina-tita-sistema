# Integración MetrePay - Portal Web de Clientes

Este documento explica cómo configurar e integrar MetrePay para cargas de saldo y pagos en el portal web de clientes.

## 📋 Requisitos Previos

1. **Cuenta de MetrePay**: Registrarse en [MetrePay](https://metrepay.com)
2. **Colección de Postman**: Compartir la colección de Postman proporcionada por MetrePay
3. **Credenciales API**: Obtener API Key y Merchant ID

## ⚙️ Configuración

### 1. Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto con:

```bash
# MetrePay API Configuration
METREPAY_API_URL=https://api.metrepay.com/v1
METREPAY_API_KEY=tu_api_key_real_aqui
METREPAY_MERCHANT_ID=tu_merchant_id_real_aqui

# Configuración adicional
METREPAY_WEBHOOK_SECRET=tu_webhook_secret_aqui
METREPAY_ENVIRONMENT=sandbox  # Cambiar a 'production' para producción
```

### 2. Configuración en Django Settings

Agregar al archivo `cantina_project/settings.py`:

```python
# MetrePay Configuration
METREPAY_API_URL = os.getenv('METREPAY_API_URL', 'https://api.metrepay.com/v1')
METREPAY_API_KEY = os.getenv('METREPAY_API_KEY', '')
METREPAY_MERCHANT_ID = os.getenv('METREPAY_MERCHANT_ID', '')
METREPAY_WEBHOOK_SECRET = os.getenv('METREPAY_WEBHOOK_SECRET', '')
METREPAY_ENVIRONMENT = os.getenv('METREPAY_ENVIRONMENT', 'sandbox')
```

## 🔧 Funcionalidades Implementadas

### 1. Cargar Saldo a Tarjetas
- **Vista**: `portal_cargar_saldo_view`
- **Template**: `portal/cargar_saldo.html`
- **URL**: `/portal/cargar-saldo/`

**Flujo:**
1. Usuario selecciona hijo
2. Ingresa monto (mínimo Gs. 1.000)
3. Selecciona método de pago
4. Se procesa con MetrePay
5. Se actualiza saldo de tarjeta
6. Se registra en `CargasSaldo`

### 2. Realizar Pagos de Deudas
- **Vista**: `portal_pagos_view`
- **Template**: `portal/pagos.html`
- **URL**: `/portal/pagos/`

**Flujo:**
1. Se muestran deudas pendientes (`Ventas` con `saldo_pendiente > 0`)
2. Usuario selecciona deudas a pagar
3. Se calcula total automáticamente
4. Se procesa con MetrePay
5. Se actualizan saldos de ventas

## 🧪 Pruebas

### Ejecutar Pruebas de MetrePay

```bash
cd d:\anteproyecto20112025
py test_metrepay.py
```

### Modo Desarrollo

Si no hay API Key configurada, el sistema simula transacciones exitosas con referencias como `SIM-XXXXXXXX`.

## 📡 Webhooks y Callbacks

### URLs Requeridas

Configurar en MetrePay las siguientes URLs:

- **Success URL**: `https://tu-dominio.com/portal/pago_exitoso/`
- **Cancel URL**: `https://tu-dominio.com/portal/pago_cancelado/`
- **Webhook URL**: `https://tu-dominio.com/portal/webhook/`

### Implementar Vistas de Callback

Agregar estas vistas en `cliente_views.py`:

```python
def portal_pago_exitoso_view(request):
    """Vista para pagos exitosos"""
    # Procesar pago completado
    pass

def portal_pago_cancelado_view(request):
    """Vista para pagos cancelados"""
    # Procesar cancelación
    pass

def portal_webhook_view(request):
    """Vista para webhooks de MetrePay"""
    # Procesar notificaciones de MetrePay
    pass
```

## 🔒 Seguridad

- Todas las transacciones usan HTTPS
- Validación de sesiones activas
- Auditoría completa de operaciones
- Rate limiting en intentos de pago

## 📊 Monitoreo

### Logs

Los errores de MetrePay se registran en la consola. Para producción, configurar logging apropiado.

### Estados de Transacción

Posibles estados de MetrePay (adaptar según documentación):
- `pending`: Pendiente
- `completed`: Completada
- `failed`: Fallida
- `cancelled`: Cancelada

## 🚀 Despliegue

### Checklist Pre-Despliegue

- [ ] Configurar variables de entorno de producción
- [ ] Cambiar `METREPAY_ENVIRONMENT` a `production`
- [ ] Configurar URLs de callback en MetrePay
- [ ] Probar con transacciones reales en sandbox
- [ ] Configurar webhooks
- [ ] Verificar certificados SSL

## 📞 Soporte

Para soporte técnico:
1. Revisar logs de aplicación
2. Consultar documentación de MetrePay
3. Verificar configuración de API Key
4. Probar con colección de Postman

## 🔄 Actualización de API

Cuando MetrePay actualice su API:

1. Actualizar `procesar_pago_metrepay()` según nueva documentación
2. Modificar payloads y endpoints según requiera
3. Probar exhaustivamente con sandbox
4. Actualizar este documento