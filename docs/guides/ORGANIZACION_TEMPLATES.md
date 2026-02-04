# 📋 ANÁLISIS Y ORGANIZACIÓN DE TEMPLATES

**Fecha:** 3 de febrero de 2026  
**Objetivo:** Estructura ordenada de templates sin duplicados usando sus bases correctas

---

## 🎯 ESTRUCTURA DE BASES CREADAS

```
frontend/templates/
├── base.html              ✅ Base principal (Tailwind + Alpine.js + DaisyUI)
├── base_pos.html          ✅ Extiende base.html (POS - naranja, touch-friendly)
├── base_gestion.html      ✅ Extiende base.html (Admin - turquesa, tablas)
└── auth/
    └── login.html         ✅ Login empleados (extiende base.html)
```

---

## 📊 TEMPLATES NECESARIOS POR MÓDULO

### 🔐 1. AUTENTICACIÓN (Auth)
**Base:** `base.html` (sin header/footer complejo)

| Template | Ruta | Estado | Vista |
|----------|------|--------|-------|
| Login Empleados | `auth/login.html` | ✅ Creado | `auth_views.CustomLoginView` |
| Login Portal Padres | `portal/auth/login.html` | ⏳ Crear | `portal_views.login_view` |
| Registro Portal | `portal/auth/registro.html` | ⏳ Crear | `portal_views.registro_view` |
| Recuperar Password | `portal/auth/recuperar_password.html` | ⏳ Crear | `portal_views.recuperar_password_view` |
| Restablecer Password | `portal/auth/restablecer_password.html` | ⏳ Crear | `portal_views.restablecer_password_view` |
| Verificar Email | `portal/auth/verificar_email.html` | ⏳ Crear | `portal_views.verificar_email_view` |
| Configurar 2FA | `portal/auth/configurar_2fa.html` | ⏳ Crear | `cliente_views.portal_configurar_2fa_view` |
| Verificar 2FA | `portal/auth/verificar_2fa.html` | ⏳ Crear | `cliente_views.portal_verificar_2fa_view` |

---

### 🛒 2. POS (Punto de Venta)
**Base:** `base_pos.html`

#### Dashboard y Ventas
| Template | Ruta | Estado | Vista |
|----------|------|--------|-------|
| Dashboard POS | `pos/dashboard.html` | ⏳ Crear | `pos_views.dashboard` |
| Venta Principal | `pos/venta.html` | ⏳ Crear | `pos_views.venta_view` / `pos_general_views.venta_view` |
| Historial Ventas | `pos/historial.html` | ⏳ Crear | `pos_views.historial_view` |
| Reportes POS | `pos/reportes.html` | ⏳ Crear | `pos_views.reportes_view` |
| Ticket Venta | `pos/ticket.html` | ⏳ Crear | `pos_views.imprimir_ticket` |

#### Recargas
| Template | Ruta | Estado | Vista |
|----------|------|--------|-------|
| Recargas | `pos/recargas.html` | ⏳ Crear | `pos_views.recargas_view` |
| Historial Recargas | `pos/historial_recargas.html` | ⏳ Crear | `pos_views.historial_recargas` |
| Comprobante Recarga | `pos/comprobante_recarga.html` | ⏳ Crear | `pos_views.comprobante_recarga` |
| Validar Carga | `pos/validar_carga.html` | ⏳ Crear | `pos_views_completas.validar_carga` |

#### Clientes (en POS)
| Template | Ruta | Estado | Vista |
|----------|------|--------|-------|
| Gestionar Clientes | `pos/gestionar_clientes.html` | ⏳ Crear | `cliente_views.gestionar_clientes_view` |
| Crear Cliente | `pos/crear_cliente.html` | ⏳ Crear | `cliente_views.crear_cliente_view` |

#### Cuenta Corriente (en POS)
| Template | Ruta | Estado | Vista |
|----------|------|--------|-------|
| Cuenta Corriente | `pos/cuenta_corriente.html` | ⏳ Crear | `pos_views.cuenta_corriente_view` |
| Detalle CC | `pos/cc_detalle.html` | ⏳ Crear | `pos_views.cuenta_corriente_detalle` |

#### Partials (HTMX)
| Template | Ruta | Estado | Vista |
|----------|------|--------|-------|
| Grid Productos | `pos/partials/productos_grid.html` | ⏳ Crear | `pos_views.buscar_productos` |
| Info Tarjeta | `pos/partials/tarjeta_info.html` | ⏳ Crear | `pos_views.buscar_tarjeta` |

---

### ⚙️ 3. GESTIÓN/ADMIN
**Base:** `base_gestion.html`

#### Dashboard
| Template | Ruta | Estado | Vista |
|----------|------|--------|-------|
| Dashboard Admin | `gestion/dashboard.html` | ⏳ Crear | `views.dashboard` |
| Index Gestión | `gestion/index.html` | ⏳ Crear | `views.index` |

#### Productos
| Template | Ruta | Estado | Vista |
|----------|------|--------|-------|
| Lista Productos | `gestion/productos/lista.html` | ⏳ Crear | `views.productos_lista` |
| Crear Producto | `gestion/productos/crear.html` | ⏳ Crear | `views.productos_crear` |
| Editar Producto | `gestion/productos/editar.html` | ⏳ Crear | `views.productos_editar` |
| Importar Productos | `gestion/productos/importar.html` | ⏳ Crear | `views.importar_productos` |

#### Categorías
| Template | Ruta | Estado | Vista |
|----------|------|--------|-------|
| Lista Categorías | `gestion/categorias/lista.html` | ⏳ Crear | `views.categorias_lista` |
| Crear Categoría | `gestion/categorias/crear.html` | ⏳ Crear | `views.categoria_crear` |
| Editar Categoría | `gestion/categorias/editar.html` | ⏳ Crear | `views.categoria_editar` |

#### Empleados
| Template | Ruta | Estado | Vista |
|----------|------|--------|-------|
| Gestionar Empleados | `gestion/empleados/gestionar.html` | ⏳ Crear | `views.gestionar_empleados` |
| Crear Empleado | `gestion/empleados/crear.html` | ⏳ Crear | `views.crear_empleado` |
| Perfil Empleado | `gestion/empleados/perfil.html` | ⏳ Crear | `empleado_views.perfil_empleado` |
| Cambiar Contraseña | `gestion/empleados/cambiar_password.html` | ⏳ Crear | `empleado_views.cambiar_contrasena` |

#### Clientes
| Template | Ruta | Estado | Vista |
|----------|------|--------|-------|
| Lista Clientes | `gestion/clientes/lista.html` | ⏳ Crear | `views.clientes_lista` |
| Crear Cliente | `gestion/clientes/crear.html` | ⏳ Crear | `cliente_views.crear_cliente_view` |

#### Ventas
| Template | Ruta | Estado | Vista |
|----------|------|--------|-------|
| Lista Ventas | `gestion/ventas/lista.html` | ⏳ Crear | `views.ventas_lista` |

#### Reportes
| Template | Ruta | Estado | Vista |
|----------|------|--------|-------|
| Reporte Mensual | `gestion/reportes/mensual.html` | ⏳ Crear | `views.reporte_mensual` |
| Dashboard Ventas | `gestion/reportes/dashboard_ventas.html` | ⏳ Crear | `pos_general_views.dashboard_ventas_dia` |

#### Facturación
| Template | Ruta | Estado | Vista |
|----------|------|--------|-------|
| Listado Facturación | `gestion/facturacion/listado.html` | ⏳ Crear | `views.facturacion_listado` |
| KUDE | `gestion/facturacion/kude.html` | ⏳ Crear | `views.facturacion_kude` |
| Reporte Cumplimiento | `gestion/facturacion/reporte_cumplimiento.html` | ⏳ Crear | `views.reporte_cumplimiento_facturacion` |

---

### 👨‍👩‍👧‍👦 4. PORTAL PADRES
**Base:** `base.html` (con navegación específica de portal)

#### Autenticación (ya listado arriba)

#### Dashboard
| Template | Ruta | Estado | Vista |
|----------|------|--------|-------|
| Dashboard Portal | `portal/dashboard.html` | ⏳ Crear | `portal_views.dashboard_view` |
| Mis Hijos | `portal/mis_hijos.html` | ⏳ Crear | `portal_views.mis_hijos_view` |
| Consumos Hijo | `portal/consumos_hijo.html` | ⏳ Crear | `cliente_views.portal_consumos_hijo_view` |
| Perfil | `portal/perfil.html` | ⏳ Crear | `portal_views.perfil_view` |

#### Recargas y Pagos
| Template | Ruta | Estado | Vista |
|----------|------|--------|-------|
| Recargas Portal | `portal/recargas.html` | ⏳ Crear | `cliente_views.portal_recargas_view` |
| Recargar Tarjeta | `portal/recargar_tarjeta.html` | ⏳ Crear | `portal_views.recargar_tarjeta_view` |
| Estado Recarga | `portal/estado_recarga.html` | ⏳ Crear | `portal_views.estado_recarga_view` |
| Pago Exitoso | `portal/pago_exitoso.html` | ⏳ Crear | `cliente_views.portal_pago_exitoso_view` |
| Pago Cancelado | `portal/pago_cancelado.html` | ⏳ Crear | `cliente_views.portal_pago_cancelado_view` |
| Cargar Saldo | `portal/cargar_saldo.html` | ⏳ Crear | `cliente_views.portal_cargar_saldo_view` |
| Pagos | `portal/pagos.html` | ⏳ Crear | `cliente_views.portal_pagos_view` |

#### Configuración
| Template | Ruta | Estado | Vista |
|----------|------|--------|-------|
| Cambiar Password | `portal/cambiar_password.html` | ⏳ Crear | `cliente_views.portal_cambiar_password_view` |
| Restricciones Hijo | `portal/restricciones_hijo.html` | ⏳ Crear | `cliente_views.portal_restricciones_hijo_view` |
| Términos Saldo Negativo | `portal/terminos_saldo_negativo.html` | ⏳ Crear | `terminos_views.terminos_saldo_negativo_view` |

---

## 📁 ESTRUCTURA FINAL PROPUESTA

```
frontend/templates/
│
├── base.html                           ✅ Base principal
├── base_pos.html                       ✅ Base POS
├── base_gestion.html                   ✅ Base Admin
│
├── auth/                               🔐 AUTENTICACIÓN EMPLEADOS
│   └── login.html                      ✅ Login empleados
│
├── pos/                                🛒 PUNTO DE VENTA
│   ├── dashboard.html                  ⏳ Dashboard POS
│   ├── venta.html                      ⏳ Venta principal
│   ├── historial.html                  ⏳ Historial ventas
│   ├── reportes.html                   ⏳ Reportes POS
│   ├── ticket.html                     ⏳ Ticket impresión
│   │
│   ├── recargas.html                   ⏳ Recargas
│   ├── historial_recargas.html         ⏳ Historial recargas
│   ├── comprobante_recarga.html        ⏳ Comprobante
│   ├── validar_carga.html              ⏳ Validar carga
│   │
│   ├── gestionar_clientes.html         ⏳ Gestión clientes POS
│   ├── crear_cliente.html              ⏳ Crear cliente
│   │
│   ├── cuenta_corriente.html           ⏳ Cuenta corriente
│   ├── cc_detalle.html                 ⏳ Detalle CC
│   │
│   └── partials/                       📦 Componentes HTMX
│       ├── productos_grid.html         ⏳ Grid de productos
│       └── tarjeta_info.html           ⏳ Info tarjeta
│
├── gestion/                            ⚙️ GESTIÓN/ADMIN
│   ├── dashboard.html                  ⏳ Dashboard admin
│   ├── index.html                      ⏳ Índice
│   │
│   ├── productos/
│   │   ├── lista.html                  ⏳ Lista productos
│   │   ├── crear.html                  ⏳ Crear producto
│   │   ├── editar.html                 ⏳ Editar producto
│   │   └── importar.html               ⏳ Importar CSV
│   │
│   ├── categorias/
│   │   ├── lista.html                  ⏳ Lista categorías
│   │   ├── crear.html                  ⏳ Crear categoría
│   │   └── editar.html                 ⏳ Editar categoría
│   │
│   ├── empleados/
│   │   ├── gestionar.html              ⏳ Gestionar empleados
│   │   ├── crear.html                  ⏳ Crear empleado
│   │   ├── perfil.html                 ⏳ Perfil
│   │   └── cambiar_password.html       ⏳ Cambiar contraseña
│   │
│   ├── clientes/
│   │   ├── lista.html                  ⏳ Lista clientes
│   │   └── crear.html                  ⏳ Crear cliente
│   │
│   ├── ventas/
│   │   └── lista.html                  ⏳ Lista ventas
│   │
│   ├── reportes/
│   │   ├── mensual.html                ⏳ Reporte mensual
│   │   └── dashboard_ventas.html       ⏳ Dashboard ventas
│   │
│   └── facturacion/
│       ├── listado.html                ⏳ Listado facturación
│       ├── kude.html                   ⏳ KUDE
│       └── reporte_cumplimiento.html   ⏳ Cumplimiento
│
└── portal/                             👨‍👩‍👧‍👦 PORTAL PADRES
    │
    ├── auth/                           🔐 Autenticación Portal
    │   ├── login.html                  ⏳ Login padres
    │   ├── registro.html               ⏳ Registro
    │   ├── recuperar_password.html     ⏳ Recuperar password
    │   ├── restablecer_password.html   ⏳ Restablecer password
    │   ├── verificar_email.html        ⏳ Verificar email
    │   ├── configurar_2fa.html         ⏳ Configurar 2FA
    │   └── verificar_2fa.html          ⏳ Verificar 2FA
    │
    ├── dashboard.html                  ⏳ Dashboard portal
    ├── mis_hijos.html                  ⏳ Mis hijos
    ├── consumos_hijo.html              ⏳ Consumos
    ├── perfil.html                     ⏳ Perfil padre
    │
    ├── recargas.html                   ⏳ Recargas
    ├── recargar_tarjeta.html           ⏳ Recargar tarjeta
    ├── estado_recarga.html             ⏳ Estado recarga
    ├── cargar_saldo.html               ⏳ Cargar saldo
    ├── pagos.html                      ⏳ Pagos
    ├── pago_exitoso.html               ⏳ Pago exitoso
    ├── pago_cancelado.html             ⏳ Pago cancelado
    │
    ├── cambiar_password.html           ⏳ Cambiar password
    ├── restricciones_hijo.html         ⏳ Restricciones
    └── terminos_saldo_negativo.html    ⏳ Términos
```

---

## 📊 RESUMEN DE TEMPLATES

| Módulo | Templates | Estado |
|--------|-----------|--------|
| **Bases** | 3 | ✅ 3 Creados |
| **Auth Empleados** | 1 | ✅ 1 Creado |
| **Auth Portal** | 7 | ⏳ 0 Creados |
| **POS** | 14 | ⏳ 0 Creados |
| **Gestión** | 23 | ⏳ 0 Creados |
| **Portal Padres** | 17 | ⏳ 0 Creados |
| **TOTAL** | **65** | **4 (6%)** |

---

## 🎯 ORDEN DE IMPLEMENTACIÓN RECOMENDADO

### Sprint 1 - Core POS (Prioridad ⭐⭐⭐⭐⭐)
1. **pos/venta.html** - Pantalla principal de ventas
2. **pos/dashboard.html** - Dashboard POS
3. **pos/partials/productos_grid.html** - Grid de productos HTMX
4. **pos/partials/tarjeta_info.html** - Info tarjeta HTMX
5. **pos/gestionar_clientes.html** - Gestión rápida de clientes

**Estimado:** 6-8 horas

---

### Sprint 2 - Portal Padres Básico (Prioridad ⭐⭐⭐⭐)
1. **portal/auth/login.html** - Login portal
2. **portal/auth/registro.html** - Registro
3. **portal/dashboard.html** - Dashboard padres
4. **portal/mis_hijos.html** - Ver hijos y tarjetas
5. **portal/recargar_tarjeta.html** - Recargar saldo

**Estimado:** 6-8 horas

---

### Sprint 3 - Gestión Básica (Prioridad ⭐⭐⭐)
1. **gestion/dashboard.html** - Dashboard admin
2. **gestion/productos/lista.html** - Lista productos
3. **gestion/productos/crear.html** - Crear producto
4. **gestion/productos/editar.html** - Editar producto
5. **gestion/clientes/lista.html** - Lista clientes

**Estimado:** 6-8 horas

---

### Sprint 4 - Recargas y Reportes (Prioridad ⭐⭐⭐)
1. **pos/recargas.html** - Recargas POS
2. **pos/historial_recargas.html** - Historial
3. **pos/reportes.html** - Reportes POS
4. **gestion/reportes/dashboard_ventas.html** - Dashboard ventas
5. **gestion/reportes/mensual.html** - Reporte mensual

**Estimado:** 6-8 horas

---

### Sprint 5 - Funcionalidades Avanzadas (Prioridad ⭐⭐)
1. **portal/auth/recuperar_password.html**
2. **portal/auth/configurar_2fa.html**
3. **pos/cuenta_corriente.html**
4. **gestion/empleados/gestionar.html**
5. **gestion/facturacion/listado.html**

**Estimado:** 8-10 horas

---

## 🔧 COMPONENTES COMPARTIDOS

Estos elementos se reutilizarán en múltiples templates:

### Componentes Alpine.js (ya creados)
- ✅ notifications (toast)
- ✅ loadingState
- ✅ formValidation
- ✅ searchWithDebounce
- ✅ modal
- ✅ darkMode
- ✅ keyboardNav
- ✅ clipboard

### Partials a crear
- ⏳ `partials/pagination.html` - Paginación reutilizable
- ⏳ `partials/search_bar.html` - Barra de búsqueda
- ⏳ `partials/table_actions.html` - Acciones de tabla
- ⏳ `partials/breadcrumbs.html` - Migas de pan
- ⏳ `partials/filters.html` - Filtros avanzados

---

## ✅ PRÓXIMO PASO

**Crear templates del Sprint 1 (POS Core):**
1. pos/venta.html
2. pos/dashboard.html
3. pos/partials/productos_grid.html
4. pos/partials/tarjeta_info.html
5. pos/gestionar_clientes.html

¿Deseas que comience con estos 5 templates del Sprint 1?
