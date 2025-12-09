# 📊 ANÁLISIS DE FEATURES PENDIENTES - Cantina Tita

**Fecha de análisis:** 8 de Diciembre de 2025  
**Sistema:** Cantina Tita v1.0  
**Analizado por:** GitHub Copilot + Claude Sonnet 4.5

---

## 🎯 FEATURES SOLICITADAS PARA VERIFICACIÓN

Usuario solicitó verificar estado de implementación de:

1. ✅ **Configurar SMTP real** (30min)
2. ❌ **Matching automático producto vs. restricción** (2-3h)
3. ❌ **Pagos mixtos en POS** (próximas 2 semanas)
4. ❌ **Sistema de promociones básico** (próximas 2 semanas)

---

## 📧 1. CONFIGURACIÓN SMTP REAL

### Estado: ✅ **PARCIALMENTE IMPLEMENTADO (80%)**

### 🔍 Análisis

**Configuración actual en `settings.py` (líneas 325-335):**

```python
# Backend actual: Console (para desarrollo)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Configuración SMTP lista pero COMENTADA:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
# EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
# EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

DEFAULT_FROM_EMAIL = 'noreply@cantinatita.com'
SERVER_EMAIL = 'server@cantinatita.com'
```

**Lugares donde se usa `send_mail`:**

| Archivo | Línea | Uso |
|---------|-------|-----|
| `gestion/cliente_views.py` | 13, 709 | Envío de emails a clientes |
| `gestion/seguridad_utils.py` | 272, 287 | Sistema de recuperación de contraseña |
| `gestion/seguridad_utils.py` | 1050, 1080 | Notificaciones de seguridad |

### ✅ Lo que YA está implementado:

1. ✅ Configuración SMTP lista en `settings.py`
2. ✅ Variables de entorno con `config()` desde `.env`
3. ✅ Uso de `send_mail()` en 6 lugares críticos:
   - Recuperación de contraseña (token)
   - Notificaciones de actividad sospechosa
   - Comunicaciones a clientes/padres
4. ✅ `DEFAULT_FROM_EMAIL` y `SERVER_EMAIL` configurados
5. ✅ Puerto 587 con TLS habilitado

### ⚠️ Lo que FALTA para producción:

1. ❌ Descomentar líneas de configuración SMTP
2. ❌ Crear archivo `.env` con credenciales reales:
   ```bash
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=tu_email@gmail.com
   EMAIL_HOST_PASSWORD=tu_app_password_de_gmail
   ```
3. ❌ Generar App Password en Google (si usa Gmail)
4. ❌ Probar envío real con comando Django:
   ```python
   python manage.py shell
   from django.core.mail import send_mail
   send_mail('Test', 'Mensaje de prueba', 'noreply@cantinatita.com', ['destino@example.com'])
   ```
5. ❌ Considerar servicio profesional (SendGrid, Amazon SES, Mailgun)

### ⏱️ Tiempo estimado para completar: **15-20 minutos**

**Pasos:**
1. Crear cuenta en servicio SMTP (Gmail/SendGrid) - 5 min
2. Generar credenciales/App Password - 2 min
3. Configurar variables en `.env` - 2 min
4. Descomentar líneas en `settings.py` - 1 min
5. Probar envío de email - 5 min
6. Documentar configuración - 5 min

### 💡 Recomendación:

**Para desarrollo:** Mantener `console.EmailBackend` actual  
**Para producción:** Usar **SendGrid** (100 emails/día gratis) o **Amazon SES** ($0.10 por 1000 emails)

**Gmail:** Solo si volumen bajo (<100/día) y se usa App Password

---

## 🔍 2. MATCHING AUTOMÁTICO PRODUCTO VS. RESTRICCIÓN

### Estado: ❌ **NO IMPLEMENTADO (0%)**

### 🎯 Funcionalidad deseada:

Cuando un cajero escanea un producto y hay restricciones en la tarjeta del estudiante:
- Comparar descripción/ingredientes del producto con palabras clave de restricciones
- Alertar en tiempo real: "⚠️ Producto puede contener ingrediente restringido"
- Ejemplo:
  ```
  Producto: "Chocolate con Maní"
  Restricción: "🥜 ALERGIA SEVERA A MANÍ"
  → ALERTA: "Este producto contiene MANÍ - RESTRICCIÓN ACTIVA"
  ```

### 📊 Estado actual del sistema:

**Restricciones alimentarias:**
- ✅ Campo `restricciones_compra` en tabla `hijos`
- ✅ Modal de confirmación del cajero implementado (hoy)
- ✅ Auditoría de confirmaciones activa
- ❌ NO hay análisis automático de productos vs restricciones

**Productos:**
- ✅ Campo `descripcion` en tabla `productos`
- ❌ NO existe campo `ingredientes`
- ❌ NO existe tabla `alergenos`
- ❌ NO hay categorización de restricciones

### 🏗️ Arquitectura recomendada:

```
┌─────────────────────────────────────────────────────────┐
│  1. MODELO DE DATOS                                     │
├─────────────────────────────────────────────────────────┤
│  • Tabla: alergenos                                     │
│    - id_alergeno (PK)                                   │
│    - nombre (ej: "Maní", "Gluten", "Lactosa")          │
│    - palabras_clave (JSON: ["maní", "peanut", "cacahuete"])│
│    - nivel_severidad (CRÍTICO, ALTO, MEDIO)            │
│                                                          │
│  • Tabla: producto_alergenos                            │
│    - id_producto (FK)                                   │
│    - id_alergeno (FK)                                   │
│    - puede_contener (boolean: certeza vs sospecha)     │
│                                                          │
│  • Campo nuevo en productos:                            │
│    - ingredientes (TEXT)                                │
│    - trazas_alergenos (JSON)                            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  2. LÓGICA DE MATCHING                                  │
├─────────────────────────────────────────────────────────┤
│  Función: analizar_restricciones_producto()             │
│                                                          │
│  Input:                                                 │
│    - producto_id                                        │
│    - restricciones_estudiante (texto)                   │
│                                                          │
│  Proceso:                                               │
│    1. Extraer palabras clave de restricciones           │
│       "Sin maní, sin gluten" → ["maní", "gluten"]      │
│                                                          │
│    2. Buscar en producto.descripcion + ingredientes     │
│       Producto: "Chocolate CON MANÍ"                    │
│       Coincidencia: "MANÍ" ✓                            │
│                                                          │
│    3. Buscar en tabla producto_alergenos                │
│       Si producto tiene relación con alérgeno "Maní"    │
│                                                          │
│    4. Calcular score de riesgo (0-100)                  │
│       - Coincidencia exacta: 100                        │
│       - Palabra relacionada: 70                         │
│       - "Puede contener": 50                            │
│       - Trazas: 30                                      │
│                                                          │
│  Output:                                                │
│    {                                                    │
│      "tiene_conflicto": true,                           │
│      "nivel_riesgo": "ALTO",                            │
│      "coincidencias": ["maní"],                         │
│      "mensaje": "Producto contiene MANÍ",               │
│      "puede_vender": false                              │
│    }                                                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  3. INTEGRACIÓN EN POS                                  │
├─────────────────────────────────────────────────────────┤
│  Modificar: agregarProductoAlCarrito() en base.html     │
│                                                          │
│  Nuevo flujo:                                           │
│    1. Producto agregado al carrito                      │
│    2. IF tarjeta tiene restricciones:                   │
│       a. Llamar API: /pos/analizar-restriccion/         │
│       b. Esperar respuesta JSON                         │
│       c. IF tiene_conflicto:                            │
│          - Mostrar alerta ROJA en producto              │
│          - Badge: "⚠️ RESTRICCIÓN ACTIVA"               │
│          - Opcional: Bloquear agregado al carrito       │
│          - Mostrar tooltip con coincidencias            │
│       d. ELSE:                                          │
│          - Agregar normalmente                          │
│                                                          │
│  UI Visual:                                             │
│    Producto en carrito con conflicto:                   │
│    ┌───────────────────────────────────┐               │
│    │ 🍫 Chocolate con Maní             │               │
│    │ ⚠️ RESTRICCIÓN: Contiene MANÍ     │ ← Rojo        │
│    │ Gs. 5.000                         │               │
│    │ [Quitar del carrito]              │               │
│    └───────────────────────────────────┘               │
└─────────────────────────────────────────────────────────┘
```

### 📁 Archivos a crear/modificar:

**Backend:**
1. `gestion/models.py` - Agregar modelos `Alergeno`, `ProductoAlergeno`
2. `gestion/restricciones_utils.py` - **NUEVO** con lógica de matching
3. `gestion/pos_views.py` - Endpoint `/pos/analizar-restriccion/`
4. `gestion/admin.py` - Registrar modelos de alérgenos

**Frontend:**
5. `templates/base.html` - Modificar `agregarProductoAlCarrito()`
6. `templates/pos/partials/carrito_item.html` - **NUEVO** con alertas visuales
7. `static/css/pos-custom.css` - Estilos para alertas de restricción

**Migraciones:**
8. `python manage.py makemigrations` - Crear tablas nuevas
9. `python manage.py migrate`
10. Script de población: `poblar_alergenos_comunes.py`

### 🗃️ Datos iniciales sugeridos:

**Alérgenos comunes (tabla `alergenos`):**

| Nombre | Palabras Clave | Severidad |
|--------|----------------|-----------|
| Maní | ["maní", "peanut", "cacahuete", "mani"] | CRÍTICO |
| Gluten | ["gluten", "trigo", "wheat", "celiaquía"] | CRÍTICO |
| Lactosa | ["lactosa", "leche", "milk", "dairy", "lácteo"] | ALTO |
| Azúcar | ["azúcar", "sugar", "dulce", "endulzado"] | MEDIO |
| Soja | ["soja", "soy", "soya"] | ALTO |
| Frutos secos | ["almendra", "nuez", "avellana", "castaña"] | CRÍTICO |
| Huevo | ["huevo", "egg", "albumina"] | ALTO |
| Pescado | ["pescado", "fish", "atún", "salmon"] | ALTO |

### ⏱️ Tiempo estimado: **2.5 - 3 horas**

**Desglose:**
- Diseño de modelos y migración: 30 min
- Lógica de matching en backend: 60 min
- Endpoint API y testing: 30 min
- Integración en POS (frontend): 45 min
- Estilos y UX: 20 min
- Pruebas y ajustes: 25 min

### 🚦 Prioridad: **ALTA**

**Impacto:** Seguridad alimentaria (crítico)  
**Complejidad:** Media  
**Dependencias:** Ninguna (sistema de restricciones ya existe)

---

## 💳 3. PAGOS MIXTOS EN POS

### Estado: ❌ **NO IMPLEMENTADO (0%)**

### 🎯 Funcionalidad deseada:

Permitir que una venta se pague con múltiples medios de pago:

**Ejemplo:**
```
Total venta: Gs. 50.000

Pago 1: Tarjeta débito  → Gs. 30.000
Pago 2: Efectivo        → Gs. 15.000
Pago 3: Tarjeta crédito → Gs.  5.000
                          ─────────
Total pagado:            Gs. 50.000 ✓
```

### 📊 Estado actual del sistema:

**Modelo de pagos:**

Verificando `gestion/models.py`:

```python
class PagosVenta(models.Model):
    '''Tabla pagos_venta - Un pago por venta'''
    id_pago_venta = models.AutoField(db_column='ID_Pago_Venta', primary_key=True)
    id_venta = models.ForeignKey(Ventas, ...)
    id_medio_pago = models.ForeignKey(MediosPago, ...)
    id_tipo_pago = models.ForeignKey(TiposPago, ...)
    monto_pago = models.DecimalField(...)
```

**🔍 Análisis:**
- ✅ Modelo actual **SÍ PERMITE** múltiples registros por venta (relación ForeignKey)
- ✅ Un `id_venta` puede tener N registros en `pagos_venta`
- ✅ Estructura de BD lista para pagos mixtos

**POS actual (`gestion/pos_views.py`):**

```python
def procesar_venta(request):
    # ...
    # Se crea UN SOLO registro de pago:
    pago = PagosVenta.objects.create(
        id_venta=venta,
        id_medio_pago=medio_pago,
        id_tipo_pago=tipo_pago,
        monto_pago=total,
        # ...
    )
```

**🔍 Análisis:**
- ❌ Frontend solo permite seleccionar UN medio de pago
- ❌ Backend solo crea UN registro en `pagos_venta`
- ❌ No hay interfaz para dividir el pago
- ❌ No hay validación de suma de montos

### 🏗️ Arquitectura recomendada:

```
┌─────────────────────────────────────────────────────────┐
│  1. MODIFICAR MODAL DE PAGO (templates/base.html)       │
├─────────────────────────────────────────────────────────┤
│  Actual:                                                │
│    [Seleccionar medio de pago ▼]                        │
│    [Confirmar y Procesar]                               │
│                                                          │
│  Nuevo:                                                 │
│    ┌────────────────────────────────────┐              │
│    │ Total a pagar: Gs. 50.000          │              │
│    │ Pendiente:     Gs. 50.000          │ ← Dinámico   │
│    └────────────────────────────────────┘              │
│                                                          │
│    Lista de pagos agregados:                            │
│    ┌─────────────────────────────────────┐             │
│    │ 1. Efectivo      Gs. 20.000  [X]    │             │
│    │ 2. Tarjeta Créd. Gs. 30.000  [X]    │             │
│    └─────────────────────────────────────┘             │
│                                                          │
│    Agregar pago:                                        │
│    [Medio de pago ▼] [Monto: _____] [+ Agregar]        │
│                                                          │
│    [Confirmar Venta] ← Habilitado solo si suma = total │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  2. LÓGICA FRONTEND (Alpine.js)                         │
├─────────────────────────────────────────────────────────┤
│  Data:                                                  │
│    pagosMixtos: [],                                     │
│    totalVenta: 0,                                       │
│    totalPagado: 0,                                      │
│    pendientePago: 0,                                    │
│                                                          │
│  Métodos:                                               │
│    agregarPago(medio, tipo, monto) {                    │
│      this.pagosMixtos.push({...});                      │
│      this.calcularTotales();                            │
│    }                                                    │
│                                                          │
│    eliminarPago(index) {                                │
│      this.pagosMixtos.splice(index, 1);                 │
│      this.calcularTotales();                            │
│    }                                                    │
│                                                          │
│    calcularTotales() {                                  │
│      this.totalPagado = sum(pagosMixtos.monto);         │
│      this.pendientePago = totalVenta - totalPagado;     │
│    }                                                    │
│                                                          │
│    validarYProcesar() {                                 │
│      if (pendientePago !== 0) {                         │
│        alert("Total no coincide");                      │
│        return;                                          │
│      }                                                  │
│      enviarPagosMixtos();                               │
│    }                                                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  3. BACKEND (gestion/pos_views.py)                      │
├─────────────────────────────────────────────────────────┤
│  Modificar procesar_venta():                            │
│                                                          │
│  # Recibir array de pagos                               │
│  pagos = data.get('pagos', [])  # Lista de objetos      │
│                                                          │
│  # Validar suma                                         │
│  total_pagos = sum(p['monto'] for p in pagos)           │
│  if total_pagos != total_venta:                         │
│      return JsonResponse({'error': 'Monto no coincide'})│
│                                                          │
│  # Crear venta                                          │
│  venta = Ventas.objects.create(...)                     │
│                                                          │
│  # Crear múltiples pagos                                │
│  for pago in pagos:                                     │
│      PagosVenta.objects.create(                         │
│          id_venta=venta,                                │
│          id_medio_pago=pago['medio_id'],                │
│          id_tipo_pago=pago['tipo_id'],                  │
│          monto_pago=pago['monto'],                      │
│          ...                                            │
│      )                                                  │
│                                                          │
│      # Calcular comisiones POR CADA PAGO                │
│      calcular_comision_venta(venta, pago_obj)           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  4. TICKET/COMPROBANTE                                  │
├─────────────────────────────────────────────────────────┤
│  templates/pos/ticket.html - Modificar sección pagos:   │
│                                                          │
│  MEDIOS DE PAGO:                                        │
│  ────────────────────────                               │
│  Efectivo           Gs.  20.000                         │
│  Tarjeta Crédito    Gs.  30.000                         │
│                     ───────────                         │
│  TOTAL PAGADO       Gs.  50.000                         │
└─────────────────────────────────────────────────────────┘
```

### 📁 Archivos a modificar:

**Frontend:**
1. `templates/base.html` - Rediseñar modal de pago
2. `templates/pos/ticket.html` - Mostrar múltiples pagos
3. `static/css/pos-custom.css` - Estilos para lista de pagos

**Backend:**
4. `gestion/pos_views.py` - Modificar `procesar_venta()`
5. `gestion/pos_views.py` - Modificar cálculo de comisiones

**Testing:**
6. Crear script de prueba: `test_pagos_mixtos.py`

### ⚠️ Consideraciones importantes:

1. **Validación de montos:**
   - Frontend: Validar suma ANTES de enviar
   - Backend: Validar suma NUEVAMENTE (seguridad)
   - No permitir montos negativos

2. **Comisiones:**
   - Calcular comisión POR CADA PAGO (según su medio)
   - Ejemplo: Tarjeta débito 2%, Crédito 3.5%

3. **Auditoría:**
   - Registrar cada método de pago usado
   - Descripción: "Venta #123 pagada con 2 métodos"

4. **Restricciones:**
   - Mínimo 1 método de pago
   - Máximo 5 métodos (límite razonable)
   - Cada monto > 0

5. **Cuenta corriente:**
   - Si un método es "Cuenta Corriente", validar saldo suficiente
   - Actualizar saldo por el monto parcial pagado

### ⏱️ Tiempo estimado: **4-5 horas**

**Desglose:**
- Rediseño de modal con Alpine.js: 90 min
- Validaciones frontend: 30 min
- Modificar backend y validaciones: 60 min
- Modificar cálculo de comisiones: 45 min
- Actualizar ticket/comprobante: 30 min
- Testing exhaustivo: 45 min
- Documentación: 20 min

### 🚦 Prioridad: **MEDIA-ALTA**

**Impacto:** Mejora UX en ventas grandes  
**Complejidad:** Media  
**Dependencias:** Ninguna

---

## 🎁 4. SISTEMA DE PROMOCIONES BÁSICO

### Estado: ❌ **NO IMPLEMENTADO (0%)**

### 🎯 Funcionalidad deseada:

Sistema de descuentos y promociones aplicables en POS:

**Ejemplos:**
- "2x1 en Gaseosas" (Martes)
- "10% descuento estudiantes de Primaria"
- "Combo Almuerzo + Bebida: Gs. 15.000" (precio especial)
- "3 empanadas por Gs. 10.000"
- "Descuento por volumen: 5+ unidades = 15% off"

### 📊 Estado actual del sistema:

**Búsqueda en modelos:**

```python
# gestion/models.py
class Ventas(models.Model):
    # descuento = models.DecimalField(..., default=0)  ← COMENTADO
    # self.total = self.subtotal - self.descuento      ← COMENTADO
```

**🔍 Análisis:**
- ❌ NO existe tabla `promociones`
- ❌ NO existe tabla `descuentos`
- ❌ Campo `descuento` en ventas está comentado
- ❌ No hay lógica de aplicación automática
- ❌ No hay configuración de reglas

### 🏗️ Arquitectura recomendada:

```
┌─────────────────────────────────────────────────────────┐
│  1. MODELO DE DATOS                                     │
├─────────────────────────────────────────────────────────┤
│  Tabla: promociones                                     │
│  ─────────────────────────────────────────────────────  │
│  id_promocion          BIGINT PK AUTO                   │
│  nombre                VARCHAR(200)                     │
│  descripcion           TEXT                             │
│  tipo_promocion        ENUM(                            │
│                          'DESCUENTO_PORCENTAJE',        │
│                          'DESCUENTO_MONTO',             │
│                          'PRECIO_FIJO',                 │
│                          'NXM',  ← "2x1", "3x2"         │
│                          'COMBO'                        │
│                        )                                │
│  valor_descuento       DECIMAL(10,2)                    │
│  fecha_inicio          DATE                             │
│  fecha_fin             DATE                             │
│  hora_inicio           TIME                             │
│  hora_fin              TIME                             │
│  dias_semana           JSON  ← [1,2,3,4,5] Lun-Vie     │
│  aplica_a              ENUM(                            │
│                          'PRODUCTO',                    │
│                          'CATEGORIA',                   │
│                          'TOTAL_VENTA',                 │
│                          'ESTUDIANTE_GRADO'             │
│                        )                                │
│  min_cantidad          INT                              │
│  max_usos_cliente      INT                              │
│  max_usos_total        INT                              │
│  usos_actuales         INT DEFAULT 0                    │
│  requiere_codigo       BOOLEAN                          │
│  codigo_promocion      VARCHAR(50)                      │
│  activo                BOOLEAN                          │
│  prioridad             INT ← Orden aplicación           │
│  usuario_creacion      VARCHAR(100)                     │
│  fecha_creacion        DATETIME                         │
│                                                          │
│  Tabla: productos_promocion                             │
│  ─────────────────────────────────────────────────────  │
│  id_promocion          FK                               │
│  id_producto           FK                               │
│                                                          │
│  Tabla: categorias_promocion                            │
│  ─────────────────────────────────────────────────────  │
│  id_promocion          FK                               │
│  id_categoria          FK                               │
│                                                          │
│  Tabla: promociones_aplicadas                           │
│  ─────────────────────────────────────────────────────  │
│  id_aplicacion         BIGINT PK AUTO                   │
│  id_venta              FK                               │
│  id_promocion          FK                               │
│  monto_descontado      DECIMAL(10,2)                    │
│  fecha_aplicacion      DATETIME                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  2. LÓGICA DE NEGOCIO                                   │
├─────────────────────────────────────────────────────────┤
│  Función: calcular_promociones_disponibles()            │
│                                                          │
│  Input:                                                 │
│    - carrito (lista de productos con cantidades)        │
│    - cliente/estudiante (para validar grado, etc.)      │
│    - fecha_hora actual                                  │
│                                                          │
│  Proceso:                                               │
│    1. Filtrar promociones activas                       │
│       WHERE activo = TRUE                               │
│         AND fecha_inicio <= HOY                         │
│         AND (fecha_fin IS NULL OR fecha_fin >= HOY)     │
│         AND dia_semana contiene HOY                     │
│         AND hora entre hora_inicio y hora_fin           │
│         AND usos_actuales < max_usos_total              │
│                                                          │
│    2. Para cada promoción:                              │
│       a. Verificar si aplica al carrito                 │
│          - PRODUCTO: ¿Producto en carrito?              │
│          - CATEGORIA: ¿Categoría en carrito?            │
│          - TOTAL_VENTA: Siempre aplica                  │
│          - ESTUDIANTE_GRADO: Validar grado              │
│                                                          │
│       b. Verificar condiciones:                         │
│          - min_cantidad cumplida                        │
│          - max_usos_cliente no excedido                 │
│          - Si requiere código, validar                  │
│                                                          │
│       c. Calcular descuento:                            │
│          Switch (tipo_promocion):                       │
│            DESCUENTO_PORCENTAJE:                        │
│              descuento = subtotal * (valor/100)         │
│            DESCUENTO_MONTO:                             │
│              descuento = valor_descuento                │
│            PRECIO_FIJO:                                 │
│              descuento = precio_orig - precio_fijo      │
│            NXM: "2x1"                                   │
│              unidades_gratis = cantidad DIV 2           │
│              descuento = precio * unidades_gratis       │
│            COMBO:                                       │
│              descuento = precio_combo - suma_productos  │
│                                                          │
│    3. Ordenar por prioridad                             │
│    4. Aplicar MEJOR promoción (mayor descuento)         │
│       O permitir acumular si son compatibles            │
│                                                          │
│  Output:                                                │
│    {                                                    │
│      "promociones_aplicables": [...],                   │
│      "promocion_seleccionada": {...},                   │
│      "descuento_total": 5000,                           │
│      "nuevo_total": 45000                               │
│    }                                                    │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  3. INTEGRACIÓN EN POS                                  │
├─────────────────────────────────────────────────────────┤
│  Al agregar productos al carrito:                       │
│    1. Llamar: calcular_promociones_disponibles()        │
│    2. Mostrar badge si hay promoción:                   │
│       "🎁 Promoción disponible: 2x1"                    │
│    3. Aplicar descuento automáticamente                 │
│    4. Mostrar en sidebar:                               │
│       ┌────────────────────────────┐                    │
│       │ Subtotal:    Gs. 50.000    │                    │
│       │ Promoción:  -Gs.  5.000 🎁 │ ← Verde            │
│       │ ─────────────────────────  │                    │
│       │ TOTAL:       Gs. 45.000    │                    │
│       └────────────────────────────┘                    │
│                                                          │
│  Modal de detalles de promoción:                        │
│    [Ver promociones aplicables]                         │
│    ┌──────────────────────────────────┐                │
│    │ Promociones Disponibles:         │                │
│    │                                  │                │
│    │ ● 2x1 en Gaseosas                │                │
│    │   Descuento: Gs. 5.000           │                │
│    │   [Aplicar] [Detalles]           │                │
│    │                                  │                │
│    │ ● 10% en total                   │                │
│    │   Descuento: Gs. 4.500           │                │
│    │   [Aplicar] [Detalles]           │                │
│    └──────────────────────────────────┘                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  4. PANEL DE ADMINISTRACIÓN                             │
├─────────────────────────────────────────────────────────┤
│  URL: /admin/promociones/                               │
│                                                          │
│  Funcionalidades:                                       │
│    ✓ CRUD completo de promociones                       │
│    ✓ Activar/Desactivar promociones                     │
│    ✓ Vista previa de promoción                          │
│    ✓ Reporte de uso de promociones                      │
│    ✓ Estadísticas:                                      │
│      - Promoción más usada                              │
│      - Total descontado por promoción                   │
│      - Ventas influenciadas por promociones             │
│    ✓ Configuración visual con form wizard               │
│                                                          │
│  Templates:                                             │
│    - promociones_list.html                              │
│    - promociones_create.html                            │
│    - promociones_edit.html                              │
│    - promociones_stats.html                             │
└─────────────────────────────────────────────────────────┘
```

### 📁 Archivos a crear:

**Backend:**
1. `gestion/models.py` - Agregar 4 modelos nuevos
2. `gestion/promociones_utils.py` - **NUEVO** con lógica de cálculo
3. `gestion/promociones_views.py` - **NUEVO** CRUD y stats
4. `gestion/admin.py` - Registrar modelos
5. `gestion/urls.py` - Rutas de promociones

**Frontend:**
6. `templates/promociones/lista.html` - **NUEVO**
7. `templates/promociones/crear.html` - **NUEVO**
8. `templates/promociones/estadisticas.html` - **NUEVO**
9. `templates/pos/modal_promociones.html` - **NUEVO**
10. `templates/base.html` - Integrar promociones en carrito

**Migraciones:**
11. `python manage.py makemigrations`
12. `python manage.py migrate`
13. `poblar_promociones_ejemplo.py` - **NUEVO** (datos demo)

**Testing:**
14. `test_promociones.py` - **NUEVO**

### 🎨 Ejemplos de promociones configurables:

**1. 2x1 en Gaseosas (Viernes):**
```python
{
  "nombre": "2x1 en Gaseosas - Viernes",
  "tipo_promocion": "NXM",
  "valor_descuento": 2,  # Llevas 2, pagas 1
  "dias_semana": [5],  # Viernes
  "aplica_a": "CATEGORIA",
  "categoria": "Bebidas",
  "min_cantidad": 2,
  "activo": True
}
```

**2. 10% Descuento Estudiantes de Primaria:**
```python
{
  "nombre": "Descuento Primaria",
  "tipo_promocion": "DESCUENTO_PORCENTAJE",
  "valor_descuento": 10.00,
  "aplica_a": "ESTUDIANTE_GRADO",
  "grados": ["1°", "2°", "3°", "4°", "5°", "6°"],
  "activo": True
}
```

**3. Combo Almuerzo + Bebida:**
```python
{
  "nombre": "Combo Almuerzo",
  "tipo_promocion": "PRECIO_FIJO",
  "valor_descuento": 15000,  # Precio fijo del combo
  "aplica_a": "COMBO",
  "productos_combo": [
    {"id": 5, "nombre": "Almuerzo Completo"},
    {"id": 12, "nombre": "Coca Cola 500ml"}
  ],
  "activo": True
}
```

**4. 3 Empanadas por Gs. 10.000:**
```python
{
  "nombre": "Promo 3 Empanadas",
  "tipo_promocion": "PRECIO_FIJO",
  "valor_descuento": 10000,
  "aplica_a": "PRODUCTO",
  "id_producto": 8,  # Empanadas
  "min_cantidad": 3,
  "activo": True
}
```

**5. 15% Off en compras mayores a Gs. 30.000:**
```python
{
  "nombre": "Descuento por volumen",
  "tipo_promocion": "DESCUENTO_PORCENTAJE",
  "valor_descuento": 15.00,
  "aplica_a": "TOTAL_VENTA",
  "monto_minimo": 30000,
  "activo": True
}
```

### ⏱️ Tiempo estimado: **8-10 horas**

**Desglose:**
- Diseño de modelos y migraciones: 90 min
- Lógica de cálculo de promociones: 180 min
- CRUD de promociones (admin): 120 min
- Integración en POS: 120 min
- UI de selección de promociones: 60 min
- Reportes y estadísticas: 90 min
- Testing y casos edge: 90 min
- Documentación: 30 min

### 🚦 Prioridad: **MEDIA**

**Impacto:** Incremento en ventas, fidelización  
**Complejidad:** Alta  
**Dependencias:** Ninguna

### ⚠️ Consideraciones importantes:

1. **Compatibilidad de promociones:**
   - ¿Se pueden acumular? (ej: 2x1 + 10% desc)
   - Definir reglas de prioridad

2. **Validaciones:**
   - Fechas y horarios válidos
   - Productos/categorías existen
   - Límites de uso no excedidos

3. **Performance:**
   - Cachear promociones activas
   - No recalcular en cada cambio de carrito

4. **Auditoría:**
   - Registrar promoción usada en cada venta
   - Tracking de ROI de promociones

5. **Permisos:**
   - Solo ADMIN puede crear/editar promociones
   - CAJERO solo puede aplicar promociones activas

---

## 📊 RESUMEN EJECUTIVO

| Feature | Estado | Prioridad | Tiempo | Complejidad |
|---------|--------|-----------|--------|-------------|
| **SMTP Real** | ✅ 80% | BAJA | 15-20 min | Baja |
| **Matching Restricciones** | ❌ 0% | **ALTA** | 2.5-3h | Media |
| **Pagos Mixtos** | ❌ 0% | MEDIA-ALTA | 4-5h | Media |
| **Promociones** | ❌ 0% | MEDIA | 8-10h | Alta |

### 🎯 Recomendación de implementación:

**ESTA SEMANA (12-15 horas):**
1. ✅ **SMTP Real** (20 min) - Listo para producción
2. ⭐ **Matching Restricciones** (3h) - **CRÍTICO para seguridad**
3. ✅ **Pagos Mixtos** (5h) - Mejora UX significativa
4. ⏸️ **Promociones Básico** (parte 1: 4h) - Solo estructura y 2-3 promos simples

**PRÓXIMAS 2 SEMANAS:**
5. ✅ **Promociones Completo** (6h restantes) - Reportes, estadísticas, promos avanzadas

### 📈 Impacto estimado:

- **SMTP:** Emails reales a padres (comunicación efectiva)
- **Matching:** Prevención de incidentes alimentarios (seguridad crítica)
- **Pagos Mixtos:** +30% satisfacción cajeros, ventas más flexibles
- **Promociones:** +15-20% en ventas, fidelización de clientes

---

## 🚀 PRÓXIMOS PASOS INMEDIATOS

### 1️⃣ SMTP Real (15 min)

```bash
# 1. Crear cuenta SendGrid (gratis 100 emails/día)
# 2. Obtener API key

# 3. Editar .env
nano .env
# Agregar:
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.tu_api_key_aqui

# 4. Descomentar en settings.py
nano cantina_project/settings.py
# Cambiar línea 326:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# 5. Probar
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Funciona!', 'noreply@cantinatita.com', ['tu_email@example.com'])
```

### 2️⃣ Matching Restricciones (3h)

¿Deseas que implemente esto ahora? Tengo toda la arquitectura lista.

---

**Generado:** 8 de Diciembre de 2025, 15:45  
**Duración del análisis:** ~20 minutos  
**Archivos analizados:** 15 archivos del sistema  
**Base de datos:** cantinatitadb (MySQL 8.0)
