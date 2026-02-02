# Sistema de Autorización de Saldo Negativo - Documentación

## 📋 Resumen

Sistema completo para permitir que supervisores/administradores autoricen ventas cuando el estudiante tiene saldo insuficiente, permitiendo que la tarjeta quede con saldo negativo. El sistema incluye:

- ✅ Autorización de ventas con saldo negativo por supervisor/gerente
- ✅ Regularización automática del saldo negativo en la próxima recarga
- ✅ Notificaciones automáticas por email a los padres
- ✅ Control de límite de crédito por tarjeta
- ✅ Registro completo de auditoría

---

## 🗄️ Base de Datos

### Nuevos Campos en `tarjetas`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `permite_saldo_negativo` | TINYINT(1) | Indica si la tarjeta puede tener saldo negativo |
| `limite_credito` | BIGINT | Monto máximo de crédito permitido (en guaraníes) |
| `notificar_saldo_bajo` | TINYINT(1) | Si enviar notificaciones de saldo bajo |
| `ultima_notificacion_saldo` | DATETIME | Fecha de la última notificación enviada |

### Nueva Tabla: `autorizacion_saldo_negativo`

Registro de todas las autorizaciones de saldo negativo realizadas.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_autorizacion` | BIGINT (PK) | ID de la autorización |
| `id_venta` | BIGINT (FK → ventas) | Venta autorizada |
| `nro_tarjeta` | VARCHAR(255) (FK → tarjetas) | Tarjeta del estudiante |
| `id_empleado_autoriza` | INT (FK → empleados) | Supervisor que autorizó |
| `saldo_anterior` | BIGINT | Saldo antes de la venta |
| `monto_venta` | BIGINT | Monto de la venta |
| `saldo_resultante` | BIGINT | Saldo después de la venta (negativo) |
| `motivo` | VARCHAR(255) | Justificación de la autorización |
| `fecha_autorizacion` | DATETIME | Cuándo se autorizó |
| `fecha_regularizacion` | DATETIME (NULL) | Cuándo se regularizó |
| `id_carga_regularizacion` | BIGINT (FK → cargas_saldo, NULL) | Recarga que pagó la deuda |
| `regularizado` | TINYINT(1) | Si ya fue pagado |

**Índices:**
- `idx_tarjeta_fecha` (nro_tarjeta, fecha_autorizacion)
- `idx_regularizado` (regularizado)
- `idx_empleado` (id_empleado_autoriza)

### Nueva Tabla: `notificacion_saldo`

Registro de notificaciones de saldo enviadas a los padres.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id_notificacion` | BIGINT (PK) | ID de la notificación |
| `nro_tarjeta` | VARCHAR(255) (FK → tarjetas) | Tarjeta del estudiante |
| `tipo_notificacion` | VARCHAR(50) | SALDO_BAJO, SALDO_NEGATIVO, SALDO_CRITICO, REGULARIZADO |
| `saldo_actual` | BIGINT | Saldo al momento de la notificación |
| `mensaje` | TEXT | Mensaje enviado |
| `enviada_email` | TINYINT(1) | Si se envió por email |
| `enviada_sms` | TINYINT(1) | Si se envió por SMS |
| `leida` | TINYINT(1) | Si el usuario la leyó |
| `email_destinatario` | VARCHAR(255) | Email del padre |
| `fecha_creacion` | DATETIME | Cuándo se creó |
| `fecha_envio` | DATETIME (NULL) | Cuándo se envió |

**Índices:**
- `idx_tarjeta_tipo` (nro_tarjeta, tipo_notificacion)
- `idx_leida` (leida)
- `idx_fecha_creacion` (fecha_creacion)

---

## 🔧 Backend - Módulos Creados

### 1. `gestion/autorizacion_saldo_utils.py` (188 líneas)

**Funciones principales:**

#### `puede_autorizar_saldo_negativo(empleado)` → bool
- Valida si un empleado puede autorizar saldo negativo
- Solo ADMINISTRADOR o GERENTE pueden autorizar

#### `validar_limite_credito(tarjeta, monto_venta)` → (bool, str)
- Valida si una venta puede proceder con saldo negativo
- Verifica que `permite_saldo_negativo = True`
- Verifica que no exceda `limite_credito`
- Retorna tuple (puede_autorizar, mensaje_error)

#### `autorizar_venta_saldo_negativo(venta, tarjeta, empleado_autoriza, motivo)`
- **@transaction.atomic** - Garantiza atomicidad
- Crea registro en `AutorizacionSaldoNegativo`
- Registra operación en auditoría

#### `regularizar_saldo_negativo(tarjeta, carga_saldo)` → dict
- **@transaction.atomic**
- Detecta autorizaciones pendientes (regularizado = False)
- Calcula cuánto de la recarga se aplica a la deuda
- Marca autorizaciones como `regularizado = True`
- Envía notificación de regularización
- Retorna: `{deuda_anterior, monto_aplicado_deuda, saldo_final}`

**Ejemplo de uso:**
```python
from gestion.autorizacion_saldo_utils import regularizar_saldo_negativo

# En procesar_recarga()
if tarjeta.saldo_actual < 0:
    info = regularizar_saldo_negativo(tarjeta, nueva_recarga)
    print(f"Deuda pagada: Gs. {info['monto_aplicado_deuda']:,}")
```

---

### 2. `gestion/notificaciones_saldo.py` (164 líneas)

**Funciones principales:**

#### `verificar_saldo_y_notificar(tarjeta)`
- Evalúa saldo actual:
  - `saldo < 0` → Tipo: SALDO_NEGATIVO
  - `0 <= saldo < saldo_alerta` → Tipo: SALDO_BAJO
- Previene spam: espera 24 horas entre notificaciones
- Busca email del padre en `UsuariosWebClientes`
- Crea registro en `NotificacionSaldo`
- Envía email con `django.core.mail.send_mail`
- Actualiza `tarjeta.ultima_notificacion_saldo`

#### `notificar_regularizacion_saldo(tarjeta, carga_saldo)`
- Notifica cuando la deuda fue pagada completamente
- Tipo: REGULARIZADO
- Mensaje personalizado con monto de recarga

#### `obtener_notificaciones_pendientes(cliente)` → QuerySet
- Retorna notificaciones no leídas de todas las tarjetas del cliente
- Para mostrar en el portal de padres

**Ejemplo de uso:**
```python
from gestion.notificaciones_saldo import verificar_saldo_y_notificar

# Después de procesar una venta
tarjeta.saldo_actual -= monto_venta
tarjeta.save()
verificar_saldo_y_notificar(tarjeta)
```

---

### 3. `gestion/autorizacion_saldo_views.py` (333 líneas)

Vistas AJAX y UI para el proceso de autorización.

#### `verificar_saldo_venta(request)` - POST/AJAX
- **URL:** `/pos/verificar-saldo-venta/`
- **Entrada:** `{nro_tarjeta, total_venta}`
- **Salida:**
  ```json
  {
    "success": true,
    "tiene_saldo": false,
    "faltante": 15000,
    "permite_saldo_negativo": true,
    "puede_autorizar": true,
    "opciones": [
      {"id": "recargar", "texto": "Recargar Saldo"},
      {"id": "autorizar", "texto": "Autorizar con Saldo Negativo", "requiere_supervisor": true}
    ]
  }
  ```

#### `autorizar_venta_saldo_negativo_ajax(request)` - POST/AJAX
- **URL:** `/pos/autorizar-saldo-negativo/`
- **Decorador:** `@solo_gerente_o_superior` (requiere permiso)
- **Entrada:**
  ```json
  {
    "nro_tarjeta": "12345",
    "total": 50000,
    "motivo": "Padre autoriza compra de almuerzo especial",
    "id_supervisor": 1,
    "password_supervisor": "password123"
  }
  ```
- **Salida:**
  ```json
  {
    "success": true,
    "autorizado": true,
    "supervisor_nombre": "Juan Pérez",
    "saldo_anterior": 10000,
    "saldo_nuevo": -40000,
    "deuda_generada": 40000,
    "autorizacion_data": {
      "id_supervisor": 1,
      "motivo": "...",
      "timestamp": "2025-12-01T10:30:00"
    }
  }
  ```

#### `modal_autorizar_saldo_negativo(request)` - GET
- **URL:** `/pos/autorizar-saldo-negativo/modal/`
- Renderiza modal HTML con formulario de autorización
- Lista supervisores activos (GERENTE/ADMINISTRADOR)

#### `listar_autorizaciones_saldo_negativo(request)` - GET
- **URL:** `/pos/autorizaciones-saldo-negativo/`
- **Decorador:** `@solo_gerente_o_superior`
- Lista todas las autorizaciones con filtros:
  - Rango de fechas
  - Solo pendientes
- Estadísticas: Total autorizaciones, pendientes, monto total deuda

---

## 🔄 Integraciones

### Modificación 1: `gestion/pos_views.py::procesar_venta()`

**Línea ~403** - Validación de saldo:
```python
if tarjeta.saldo_actual < total and not autorizado_por_id:
    from gestion.autorizacion_saldo_utils import validar_limite_credito
    puede_negativo, mensaje_limite = validar_limite_credito(tarjeta, total)
    
    return JsonResponse({
        'success': False,
        'error': f'Saldo insuficiente. Disponible: Gs. {tarjeta.saldo_actual:,.0f}',
        'requiere_autorizacion_supervisor': True,
        'permite_saldo_negativo': tarjeta.permite_saldo_negativo,
        'puede_autorizar_negativo': puede_negativo,
        'mensaje_limite': mensaje_limite
    })
```

**Línea ~575** - Registro de autorización:
```python
# Si hay autorización de supervisor y quedará en negativo, registrar autorización
if autorizado_por_id and saldo_posterior < 0:
    from gestion.autorizacion_saldo_utils import autorizar_venta_saldo_negativo
    supervisor = Empleado.objects.get(id_empleado=autorizado_por_id)
    autorizar_venta_saldo_negativo(venta, tarjeta, supervisor, motivo_credito)
```

**Línea ~620** - Notificación de saldo bajo:
```python
# Si el saldo quedó bajo o negativo, enviar notificación
if saldo_posterior <= (tarjeta.saldo_alerta or 0):
    from gestion.notificaciones_saldo import verificar_saldo_y_notificar
    verificar_saldo_y_notificar(tarjeta)
```

---

### Modificación 2: `gestion/pos_views.py::procesar_recarga()`

**Línea ~1812** - Regularización automática:
```python
# Verificar si hay deuda pendiente (saldo negativo)
tiene_deuda = saldo_anterior < 0
deuda_anterior = abs(saldo_anterior) if tiene_deuda else Decimal('0')

# Registrar recarga...

# Si había deuda, regularizar
regularizacion_info = None
if tiene_deuda:
    from gestion.autorizacion_saldo_utils import regularizar_saldo_negativo
    regularizacion_info = regularizar_saldo_negativo(tarjeta, recarga)

# Verificar y enviar notificación de saldo
from gestion.notificaciones_saldo import verificar_saldo_y_notificar
verificar_saldo_y_notificar(tarjeta)

# Agregar información de regularización a la respuesta
if regularizacion_info:
    response_data['regularizacion'] = {
        'deuda_anterior': float(regularizacion_info['deuda_anterior']),
        'monto_aplicado_deuda': float(regularizacion_info['monto_aplicado_deuda']),
        'saldo_disponible': float(regularizacion_info['saldo_final'])
    }
```

---

## 🌐 URLs Agregadas

En `gestion/pos_urls.py`:

```python
# Verificación de saldo antes de venta
path('verificar-saldo-venta/', autorizacion_saldo_views.verificar_saldo_venta, name='verificar_saldo_venta'),

# Autorización de venta con saldo negativo
path('autorizar-saldo-negativo/', autorizacion_saldo_views.autorizar_venta_saldo_negativo_ajax, name='autorizar_saldo_negativo'),
path('autorizar-saldo-negativo/modal/', autorizacion_saldo_views.modal_autorizar_saldo_negativo, name='modal_autorizar_saldo_negativo'),

# Listado de autorizaciones
path('autorizaciones-saldo-negativo/', autorizacion_saldo_views.listar_autorizaciones_saldo_negativo, name='listar_autorizaciones_saldo_negativo'),
```

---

## 📊 Modelos Django Actualizados

### `gestion/models.py::Tarjeta`

Nuevos campos agregados:
```python
permite_saldo_negativo = models.BooleanField(default=False)
limite_credito = models.BigIntegerField(default=0)
notificar_saldo_bajo = models.BooleanField(default=True)
ultima_notificacion_saldo = models.DateTimeField(blank=True, null=True)
```

### `gestion/models.py::AutorizacionSaldoNegativo` (NUEVO)

```python
class AutorizacionSaldoNegativo(models.Model):
    id_autorizacion = models.BigAutoField(primary_key=True)
    id_venta = models.ForeignKey(Ventas, ...)
    nro_tarjeta = models.ForeignKey(Tarjeta, ...)
    id_empleado_autoriza = models.ForeignKey(Empleado, ...)
    saldo_anterior = models.BigIntegerField()
    monto_venta = models.BigIntegerField()
    saldo_resultante = models.BigIntegerField()
    motivo = models.CharField(max_length=255)
    fecha_autorizacion = models.DateTimeField(auto_now_add=True)
    fecha_regularizacion = models.DateTimeField(blank=True, null=True)
    id_carga_regularizacion = models.ForeignKey(CargasSaldo, blank=True, null=True)
    regularizado = models.BooleanField(default=False)
```

### `gestion/models.py::NotificacionSaldo` (NUEVO)

```python
class NotificacionSaldo(models.Model):
    id_notificacion = models.BigAutoField(primary_key=True)
    nro_tarjeta = models.ForeignKey(Tarjeta, ...)
    tipo_notificacion = models.CharField(max_length=50, choices=[...])
    saldo_actual = models.BigIntegerField()
    mensaje = models.TextField()
    enviada_email = models.BooleanField(default=False)
    enviada_sms = models.BooleanField(default=False)
    leida = models.BooleanField(default=False)
    email_destinatario = models.EmailField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(blank=True, null=True)
```

---

## 🔐 Seguridad y Permisos

- **@solo_gerente_o_superior:** Solo GERENTE o ADMINISTRADOR pueden autorizar
- **@acceso_cajero:** Cajeros pueden iniciar la solicitud de autorización
- Validación de contraseña del supervisor en AJAX
- Registro completo en tabla de auditoría
- Límite de crédito configurable por tarjeta

---

## 📧 Notificaciones por Email

### Configuración requerida

En `settings.py`:
```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu_email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu_password'
DEFAULT_FROM_EMAIL = 'Cantina Tita <noreply@cantinatita.com>'
```

### Tipos de notificaciones

1. **SALDO_BAJO** - Cuando saldo < saldo_alerta (pero aún positivo)
2. **SALDO_NEGATIVO** - Cuando saldo < 0 (deuda activa)
3. **SALDO_CRITICO** - Cuando excede 80% del límite de crédito
4. **REGULARIZADO** - Cuando la deuda fue pagada completamente

---

## 🚀 Flujo Completo de Uso

### Caso: Estudiante con Saldo Insuficiente

1. **Cajero escanea tarjeta** → Saldo: Gs. 8.000
2. **Agrega productos** → Total: Gs. 15.500
3. **Click en "Procesar Venta"** → Backend detecta saldo insuficiente
4. **Sistema muestra modal:**
   - "Saldo insuficiente: Faltante Gs. 7.500"
   - Opciones:
     - ✅ Recargar Saldo
     - ⚠️ Autorizar con Saldo Negativo (requiere supervisor)
     - ❌ Cancelar Venta

5. **Cajero solicita autorización** → Modal de supervisor se abre
6. **Supervisor ingresa:**
   - Usuario: admin
   - Contraseña: ********
   - Motivo: "Padre autoriza por teléfono para almuerzo"
7. **Sistema valida:**
   - ✓ Supervisor es GERENTE/ADMINISTRADOR
   - ✓ Tarjeta tiene `permite_saldo_negativo = True`
   - ✓ Saldo resultante (-7.500) < límite_credito (50.000)
8. **Venta aprobada:**
   - Saldo queda en: -Gs. 7.500
   - Registro creado en `autorizacion_saldo_negativo`
   - Email enviado a padre: "Su hijo tiene saldo negativo: -Gs. 7.500"

### Regularización Automática

1. **Padre recarga Gs. 20.000**
2. **Sistema detecta deuda de Gs. 7.500**
3. **Calcula:**
   - Deuda anterior: Gs. 7.500
   - Monto aplicado a deuda: Gs. 7.500
   - Saldo final disponible: Gs. 12.500
4. **Marca autorización como `regularizado = True`**
5. **Envía email:** "Deuda regularizada. Saldo disponible: Gs. 12.500"

---

## 📁 Archivos Creados/Modificados

### Nuevos Archivos
✅ `gestion/autorizacion_saldo_utils.py` (188 líneas)
✅ `gestion/notificaciones_saldo.py` (164 líneas)
✅ `gestion/autorizacion_saldo_views.py` (333 líneas)
✅ `gestion/migrations/0007_add_saldo_negativo_support.py`
✅ `crear_tablas_saldo_negativo.py` (script de instalación)
✅ `crear_tablas_saldo_negativo.sql` (DDL de backup)

### Archivos Modificados
📝 `gestion/models.py` - Agregados campos a Tarjeta + 2 nuevos modelos
📝 `gestion/pos_views.py` - Integración en procesar_venta() y procesar_recarga()
📝 `gestion/pos_urls.py` - 3 nuevas rutas

---

## ✅ Estado de Implementación

- [x] Modelo de datos (tablas MySQL creadas)
- [x] Modelos Django actualizados
- [x] Utilidades de autorización (autorizacion_saldo_utils.py)
- [x] Sistema de notificaciones (notificaciones_saldo.py)
- [x] Vistas AJAX (autorizacion_saldo_views.py)
- [x] Integración en procesar_venta()
- [x] Integración en procesar_recarga()
- [x] URLs configuradas
- [ ] **PENDIENTE:** Templates HTML (modales)
- [ ] **PENDIENTE:** Frontend JavaScript/Alpine.js
- [ ] **PENDIENTE:** Tests unitarios

---

## 🧪 Próximos Pasos

1. **Crear template del modal de autorización:**
   - `templates/pos/modales/autorizar_saldo_negativo.html`
   - Formulario con dropdown de supervisores
   - Input de password
   - Textarea para motivo
   - Integración con Alpine.js

2. **JavaScript del POS:**
   - Llamada a `verificar_saldo_venta()` antes de procesar
   - Mostrar modal si `requiere_autorizacion_supervisor = true`
   - Enviar datos de autorización con la venta

3. **Portal de Padres:**
   - Sección "Notificaciones" en dashboard
   - Mostrar notificaciones de saldo bajo/negativo
   - Botón "Recargar Ahora" directo

4. **Panel de Administración:**
   - Vista de autorizaciones pendientes
   - Reporte de autorizaciones del mes
   - Configuración de límites de crédito por tarjeta

---

## 📞 Soporte

Para consultas sobre esta funcionalidad:
- Revisar logs en `auditoria_operacion` para trazabilidad
- Consultar tabla `autorizacion_saldo_negativo` para historial
- Verificar `notificacion_saldo` para estado de emails

---

**Última actualización:** 12 de Enero de 2026
**Versión:** 1.0.0
**Desarrollado por:** GitHub Copilot
