# MANUAL DE ADMINISTRADOR
## Sistema de Gestión de Cantina Escolar "Tita"

**Versión:** 1.0  
**Fecha:** Enero 2025  
**Dirigido a:** Administradores del sistema, gerentes y personal IT

---

## ÍNDICE

1. [Introducción](#introducción)
2. [Acceso al Panel de Administración](#acceso-al-panel-de-administración)
3. [Gestión de Usuarios](#gestión-de-usuarios)
4. [Configuración del Sistema](#configuración-del-sistema)
5. [Gestión de Productos y Precios](#gestión-de-productos-y-precios)
6. [Control de Inventario](#control-de-inventario)
7. [Reportes Gerenciales](#reportes-gerenciales)
8. [Facturación y Contabilidad](#facturación-y-contabilidad)
9. [Backup y Restauración](#backup-y-restauración)
10. [Seguridad y Auditoría](#seguridad-y-auditoría)
11. [Mantenimiento](#mantenimiento)
12. [Troubleshooting](#troubleshooting)

---

## INTRODUCCIÓN

Este manual describe las funcionalidades administrativas del sistema de gestión de cantina escolar. Está dirigido a usuarios con permisos de administrador que requieren gestionar configuraciones, usuarios, productos, reportes y mantenimiento del sistema.

### Módulos Principales

1. **Administración Django**: Gestión completa de datos
2. **Panel Gerencial**: Reportes y métricas
3. **Configuración**: Parámetros del sistema
4. **Auditoría**: Logs y trazabilidad
5. **Mantenimiento**: Backup, optimización, diagnóstico

### Perfiles de Usuario Administrativo

- **Superusuario**: Acceso total al sistema
- **Gerente**: Reportes, configuración, usuarios
- **Contador**: Facturación, contabilidad, reportes financieros
- **Supervisor**: Consulta de datos, sin modificación

---

## ACCESO AL PANEL DE ADMINISTRACIÓN

### URL de Acceso

```
Producción: https://cantina-tita.edu.py/admin/
Desarrollo: http://localhost:8000/admin/
```

### Primera Configuración

#### Crear Superusuario (Desde Servidor)

```powershell
# En el servidor, ejecutar:
cd D:\anteproyecto20112025
.\.venv\Scripts\activate
python manage.py createsuperuser

# Ingresar:
Usuario: admin
Email: admin@cantina-tita.edu.py
Contraseña: [contraseña segura]
Confirmar contraseña: [repetir]
```

#### Login Inicial

```
┌─────────────────────────────────────┐
│  ADMINISTRACIÓN DJANGO              │
│                                     │
│  Usuario: [____________]            │
│  Contraseña: [____________]         │
│                                     │
│  [Iniciar sesión]                   │
│                                     │
│  Powered by Django 5.2.8            │
└─────────────────────────────────────┘
```

### Panel Principal

```
═══════════════════════════════════════════════════════════════
 ADMINISTRACIÓN DEL SITIO
═══════════════════════════════════════════════════════════════

Bienvenido, admin | Ver sitio | Cambiar contraseña | Cerrar sesión

GESTIÓN
├── Clientes
│   ├── Clientes (120)                              [+ Agregar]
│   ├── Hijos (245)                                 [+ Agregar]
│   └── Tipos de Cliente (3)                        [+ Agregar]
│
├── Productos y Stock
│   ├── Productos (150)                             [+ Agregar]
│   ├── Categorías (12)                             [+ Agregar]
│   ├── Stock Único (150)                           [+ Agregar]
│   └── Movimientos de Stock (1,250)                [Ver]
│
├── Ventas
│   ├── Ventas (2,450)                              [+ Agregar]
│   ├── Detalle de Venta (8,900)                    [Ver]
│   └── Tipos de Pago (5)                           [Configurar]
│
├── Tarjetas
│   ├── Tarjetas (245)                              [+ Agregar]
│   ├── Consumos con Tarjeta (3,200)                [Ver]
│   └── Tipos de Autorización (4)                   [Configurar]
│
├── Personal
│   ├── Empleados (15)                              [+ Agregar]
│   ├── Roles (5)                                   [Configurar]
│   └── Turnos (3)                                  [Configurar]
│
├── Almuerzos
│   ├── Componentes de Almuerzo (25)                [+ Agregar]
│   ├── Inscripciones (180)                         [Gestionar]
│   └── Días de Servicio (22)                       [Configurar]
│
├── Portal Padres
│   ├── Usuarios Web (120)                          [+ Agregar]
│   ├── Transacciones Online (450)                  [Ver]
│   └── Restricciones (85)                          [Configurar]
│
├── Facturación
│   ├── Facturas (320)                              [+ Generar]
│   ├── Notas de Crédito (12)                       [+ Generar]
│   └── Configuración de Facturación                [Configurar]
│
└── Reportes
    ├── Reporte Diario de Ventas                    [Generar]
    ├── Reporte de Stock                            [Generar]
    ├── Reporte Financiero                          [Generar]
    └── Auditoría de Cambios                        [Ver]

AUTENTICACIÓN Y AUTORIZACIÓN
├── Usuarios del sistema (8)                        [+ Agregar]
└── Grupos (4)                                      [+ Agregar]

═══════════════════════════════════════════════════════════════
```

---

## GESTIÓN DE USUARIOS

### Usuarios del Sistema (Staff)

#### Crear Usuario Administrativo

1. **Ir a**: Autenticación > Usuarios > Agregar usuario

```
┌─────────────────────────────────────────────────────┐
│  AGREGAR USUARIO                                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Nombre de usuario: [________________]             │
│  Contraseña: [________________]                    │
│  Confirmar contraseña: [________________]          │
│                                                     │
│  [Guardar y continuar editando]                    │
└─────────────────────────────────────────────────────┘
```

2. **Configurar permisos**:

```
INFORMACIÓN PERSONAL
  Nombre: [Juan]
  Apellido: [Rodríguez]
  Email: [juan.rodriguez@cantina-tita.edu.py]

PERMISOS
  ☑ Activo
  ☐ Es staff (acceso al admin)
  ☐ Es superusuario (acceso total)

PERMISOS ESPECÍFICOS:
  Grupos:
    ☑ Gerentes
    ☐ Cajeros
    ☐ Contadores

  Permisos de usuario:
    Gestion | cliente | Puede agregar cliente
    Gestion | cliente | Puede cambiar cliente
    Gestion | cliente | Puede eliminar cliente
    Gestion | cliente | Puede ver cliente
    ...

FECHAS IMPORTANTES
  Último login: Nunca
  Fecha de registro: 10/01/2025 14:30

[Guardar] [Guardar y agregar otro] [Guardar y continuar editando]
```

#### Grupos de Usuarios Predefinidos

**1. Gerentes**
- Ver todos los reportes
- Gestionar productos y precios
- Configurar parámetros del sistema
- Ver auditoría
- NO pueden: Eliminar ventas, modificar facturas legales

**2. Cajeros**
- Registrar ventas
- Consultar productos
- Consultar clientes y tarjetas
- NO pueden: Modificar precios, eliminar ventas

**3. Contadores**
- Generar facturas
- Ver reportes financieros
- Exportar datos contables
- NO pueden: Modificar productos, eliminar ventas

**4. Supervisores**
- Solo lectura de todos los módulos
- Generar reportes
- NO pueden: Modificar ningún dato

### Usuarios del Portal (Padres)

#### Crear Usuario de Portal

1. **Ir a**: Portal Padres > Usuarios Web > Agregar

```
┌─────────────────────────────────────────────────────┐
│  AGREGAR USUARIO WEB                                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Cliente asociado: [Juan Pérez (1234567) ▼]       │
│  Usuario: [1234567] (auto-generado desde RUC)     │
│  Email: [juan.perez@email.com]                     │
│  Contraseña temporal: [Auto-generada]              │
│                                                     │
│  ☑ Enviar credenciales por email                  │
│  ☑ Forzar cambio de contraseña en primer login    │
│  ☑ Cuenta activa                                  │
│                                                     │
│  Permisos del portal:                              │
│    ☑ Ver consumos                                 │
│    ☑ Realizar recargas                            │
│    ☑ Configurar restricciones                     │
│    ☑ Descargar reportes                           │
│    ☐ Modificar datos de hijos (requiere admin)    │
│                                                     │
│  [Guardar]                                         │
└─────────────────────────────────────────────────────┘
```

#### Resetear Contraseña de Usuario Portal

```
ACCIONES:
  [Resetear contraseña] → Genera nueva contraseña temporal
  [Enviar credenciales] → Reenvía email con datos de acceso
  [Desactivar cuenta] → Bloquea acceso sin eliminar datos
```

### Empleados (Personal de Cantina)

#### Agregar Empleado

```
┌─────────────────────────────────────────────────────┐
│  AGREGAR EMPLEADO                                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  DATOS PERSONALES                                   │
│    Nombre: [María]                                 │
│    Apellido: [González]                            │
│    RUC/CI: [9876543-2]                             │
│    Teléfono: [0981-555666]                         │
│    Email: [maria.gonzalez@cantina-tita.edu.py]     │
│    Dirección: [___________________________]        │
│    Fecha de nacimiento: [01/05/1990]               │
│                                                     │
│  DATOS LABORALES                                    │
│    Rol: [Cajero ▼]                                 │
│    Turno: [Mañana (7:00-14:00) ▼]                  │
│    Fecha de ingreso: [10/01/2025]                  │
│    Salario: [₲ 2,500,000]                          │
│                                                     │
│  ACCESO AL SISTEMA                                  │
│    Usuario POS: [mgonzalez]                        │
│    ☑ Crear usuario de sistema automáticamente     │
│    ☑ Acceso al POS                                │
│    ☐ Acceso al panel de administración            │
│                                                     │
│  ESTADO                                             │
│    ☑ Activo                                        │
│    Fecha de salida: [_________] (opcional)         │
│                                                     │
│  [Guardar]                                         │
└─────────────────────────────────────────────────────┘
```

---

## CONFIGURACIÓN DEL SISTEMA

### Parámetros Generales

**Ubicación**: Configuración > Parámetros del Sistema

```
┌─────────────────────────────────────────────────────┐
│  CONFIGURACIÓN GENERAL                              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  DATOS DE LA INSTITUCIÓN                            │
│    Nombre comercial: [Cantina Tita]               │
│    Razón social: [Cantina Escolar Tita S.A.]      │
│    RUC: [80012345-6]                               │
│    Dirección: [Av. Principal 123]                  │
│    Ciudad: [Asunción]                              │
│    Teléfono: [021-123456]                          │
│    Email: [info@cantina-tita.edu.py]               │
│    Sitio web: [https://cantina-tita.edu.py]        │
│                                                     │
│  HORARIOS DE OPERACIÓN                              │
│    Lunes a Viernes: [07:00] a [18:00]             │
│    Sábados: [07:00] a [13:00]                      │
│    Domingos: [CERRADO]                             │
│                                                     │
│  MONEDA Y FORMATO                                   │
│    Moneda: [PYG - Guaraníes ▼]                     │
│    Símbolo: [₲]                                    │
│    Separador decimal: [,]                          │
│    Separador de miles: [.]                         │
│    Decimales en precios: [0]                       │
│                                                     │
│  [Guardar Configuración]                           │
└─────────────────────────────────────────────────────┘
```

### Configuración de Email (SMTP)

**Archivo**: `cantina_project/settings.py`

Para configurar el envío de emails, ejecutar el script:

```powershell
python configurar_smtp.py
```

O editar manualmente en `settings.py`:

```python
# Configuración SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'cantina.tita@gmail.com'
EMAIL_HOST_PASSWORD = 'contraseña_de_aplicacion'  # App password, no contraseña normal
DEFAULT_FROM_EMAIL = 'Cantina Tita <cantina.tita@gmail.com>'
```

**Verificar configuración:**

```powershell
python manage.py shell

>>> from django.core.mail import send_mail
>>> send_mail(
...     'Test Email',
...     'Este es un email de prueba.',
...     'cantina.tita@gmail.com',
...     ['admin@cantina-tita.edu.py'],
... )
1  # Retorna 1 si fue exitoso
```

### Configuración de Facturación

```
┌─────────────────────────────────────────────────────┐
│  CONFIGURACIÓN DE FACTURACIÓN                       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  TIMBRADO FISCAL                                    │
│    Número de timbrado: [12345678]                  │
│    Fecha de inicio: [01/01/2025]                   │
│    Fecha de vencimiento: [31/12/2025]              │
│    ☑ Activo                                        │
│                                                     │
│  NUMERACIÓN DE FACTURAS                             │
│    Establecimiento: [001]                          │
│    Punto de expedición: [001]                      │
│    Número inicial: [0000001]                       │
│    Número actual: [0000245]                        │
│    Prefijo: [001-001-]                             │
│                                                     │
│  FORMATO DE FACTURA                                 │
│    Tipo: [Factura Legal ▼]                         │
│    Tamaño papel: [Carta (Letter) ▼]                │
│    ☑ Incluir logo                                  │
│    ☑ Incluir código QR                             │
│    ☑ Incluir pie de página personalizado          │
│                                                     │
│  IVA                                                │
│    IVA general: [10%]                              │
│    IVA reducido: [5%]                              │
│    ☑ Discriminar IVA en facturas                  │
│                                                     │
│  [Guardar]                                         │
└─────────────────────────────────────────────────────┘
```

### Configuración de Backup Automático

```powershell
# Ejecutar script de configuración:
python configurar_backup_tareas.py

# Esto creará una tarea programada en Windows que ejecuta:
# - Backup diario a las 02:00 AM
# - Mantiene últimos 30 backups
# - Ubicación: D:\backups_cantina\
```

Verificar tarea creada:

```powershell
Get-ScheduledTask -TaskName "Backup_Cantina_Diario"
```

---

## GESTIÓN DE PRODUCTOS Y PRECIOS

### Agregar Producto

```
┌─────────────────────────────────────────────────────┐
│  AGREGAR PRODUCTO                                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  INFORMACIÓN BÁSICA                                 │
│    Código de barras: [7891234567890]               │
│    Descripción: [Sándwich de jamón y queso]        │
│    Descripción corta: [Sándwich JyQ]               │
│    Categoría: [Snacks ▼]                           │
│    Unidad de medida: [Unidad ▼]                    │
│                                                     │
│  PRECIOS                                            │
│    Precio de costo: [₲ 5,000]                      │
│    Margen de ganancia: [60%]                       │
│    Precio de venta: [₲ 8,000] (calculado)          │
│    Lista de precios: [Precio Normal ▼]             │
│                                                     │
│  IMPUESTOS                                          │
│    Gravado con IVA: [10% ▼]                        │
│    ☑ Incluido en precio de venta                  │
│                                                     │
│  CONTROL DE STOCK                                   │
│    Stock inicial: [50]                             │
│    Stock mínimo: [10]                              │
│    Stock máximo: [200]                             │
│    ☑ Controlar stock                              │
│    ☑ Generar alerta de stock bajo                 │
│                                                     │
│  RESTRICCIONES                                      │
│    ☐ Requiere autorización especial               │
│    ☐ Producto con restricción de edad             │
│    ☐ Solo disponible en ciertos horarios          │
│                                                     │
│  ESTADO                                             │
│    ☑ Activo                                        │
│    ☑ Visible en POS                               │
│    ☑ Disponible en portal                         │
│                                                     │
│  [Guardar]                                         │
└─────────────────────────────────────────────────────┘
```

### Actualización Masiva de Precios

```
Productos > Acciones masivas:
  [x] Seleccionar todos los productos de categoría "Bebidas"
  Acción: [Aplicar aumento de precio ▼]
  Porcentaje de aumento: [10%]
  
  [Aplicar]
  
Resultado: 25 productos actualizados exitosamente
```

### Importar Productos desde Excel

1. **Descargar plantilla**:

```
Productos > Importar/Exportar > Descargar plantilla Excel
```

2. **Completar plantilla**:

```
| Código Barras | Descripción        | Categoría | Precio Costo | Precio Venta | Stock |
|---------------|-------------------|-----------|--------------|--------------|-------|
| 7891234567890 | Sándwich JyQ      | Snacks    | 5000         | 8000         | 50    |
| 7891234567891 | Jugo de naranja   | Bebidas   | 3000         | 5000         | 100   |
```

3. **Importar archivo**:

```
Productos > Importar/Exportar > Subir archivo Excel

[Seleccionar archivo: productos.xlsx]

Opciones:
  ☑ Actualizar productos existentes (por código de barras)
  ☑ Agregar nuevos productos
  ☐ Eliminar productos no incluidos en archivo
  
[Importar]

Resultado:
  ✓ 120 productos actualizados
  ✓ 15 productos nuevos creados
  ⚠ 3 errores (ver log)
```

---

## CONTROL DE INVENTARIO

### Consultar Stock Actual

```
Stock Único > Filtros:
  Categoría: [Todas ▼]
  Stock: [Menor o igual a stock mínimo]
  
[Aplicar filtros]

RESULTADOS (15 productos):
┌─────────────────────────────────────────────────────────────┐
│ Código      │ Producto           │ Stock │ Mínimo │ Estado │
├─────────────────────────────────────────────────────────────┤
│ 7891234001  │ Coca Cola 500ml    │ 8     │ 20     │ ⚠ BAJO │
│ 7891234002  │ Agua mineral       │ 5     │ 30     │ ⚠ BAJO │
│ 7891234003  │ Pan con manteca    │ 0     │ 10     │ ❌ AGOTADO│
└─────────────────────────────────────────────────────────────┘

Acciones:
  [Exportar lista] [Generar orden de compra] [Enviar alerta]
```

### Registrar Ingreso de Stock (Compra)

```
┌─────────────────────────────────────────────────────┐
│  REGISTRAR COMPRA                                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Proveedor: [Distribuidora ABC ▼]                  │
│  Factura del proveedor: [001-001-0001234]          │
│  Fecha de compra: [10/01/2025]                     │
│  Condición: [Contado ▼]                            │
│                                                     │
│  PRODUCTOS:                                         │
│  ┌───────────────────────────────────────────────┐ │
│  │ Producto      │ Cantidad │ Precio │ Subtotal  │ │
│  ├───────────────────────────────────────────────┤ │
│  │ Coca Cola     │ 50       │ 2,500  │ 125,000   │ │
│  │ Agua mineral  │ 100      │ 1,000  │ 100,000   │ │
│  │ [Agregar producto...]                         │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  Subtotal: ₲ 225,000                               │
│  IVA 10%: ₲ 22,500                                 │
│  TOTAL: ₲ 247,500                                  │
│                                                     │
│  ☑ Actualizar stock automáticamente                │
│  ☑ Generar asiento contable                        │
│                                                     │
│  [Guardar Compra]                                  │
└─────────────────────────────────────────────────────┘
```

### Ajuste Manual de Stock

```
Stock Único > Acciones:
  Producto: [Coca Cola 500ml]
  
  Stock actual sistema: 50
  Stock físico contado: 47
  Diferencia: -3
  
  Motivo del ajuste:
    ⚪ Rotura/Vencimiento
    ⚪ Merma
    ⚪ Corrección de inventario
    ⚪ Otro: [_______________]
  
  Observaciones: [3 botellas rotas durante transporte]
  
  [Aplicar Ajuste]
```

### Inventario Físico

Proceso completo de conteo y ajuste:

```powershell
# 1. Generar planilla de conteo
python manage.py shell

>>> from gestion.reportes import generar_planilla_inventario
>>> generar_planilla_inventario()
Archivo generado: inventario_fisico_20250110.xlsx

# 2. Imprimir y contar físicamente

# 3. Importar conteo
Stock Único > Importar conteo físico
  [Subir archivo: inventario_contado.xlsx]
  
  Resultados:
    120 productos coinciden
    12 productos con diferencias (ajuste automático)
    Total diferencia: -₲ 45,000 (pérdida)
```

---

## REPORTES GERENCIALES

### Reporte Diario de Ventas

**Acceso**: Reportes > Reporte Diario

```
┌─────────────────────────────────────────────────────┐
│  REPORTE DIARIO DE VENTAS - 10/01/2025             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  RESUMEN                                            │
│    Total ventas: ₲ 1,250,000                       │
│    Cantidad de transacciones: 145                   │
│    Ticket promedio: ₲ 8,620                        │
│                                                     │
│  POR FORMA DE PAGO                                  │
│    Efectivo: ₲ 450,000 (36%)                       │
│    Tarjeta de consumo: ₲ 650,000 (52%)             │
│    Débito/Crédito: ₲ 150,000 (12%)                 │
│                                                     │
│  POR CATEGORÍA                                      │
│    Almuerzos: ₲ 700,000 (56%)                      │
│    Bebidas: ₲ 300,000 (24%)                        │
│    Snacks: ₲ 250,000 (20%)                         │
│                                                     │
│  TOP 10 PRODUCTOS VENDIDOS                          │
│    1. Almuerzo completo - 85 unid - ₲ 680,000     │
│    2. Jugo de naranja - 45 unid - ₲ 135,000       │
│    3. Sándwich JyQ - 30 unid - ₲ 120,000          │
│    ...                                              │
│                                                     │
│  CAJEROS                                            │
│    María González - 78 ventas - ₲ 675,000         │
│    Pedro Ramírez - 67 ventas - ₲ 575,000          │
│                                                     │
│  [Descargar PDF] [Exportar Excel] [Imprimir]      │
└─────────────────────────────────────────────────────┘
```

### Reporte de Stock Valorizado

```
┌─────────────────────────────────────────────────────┐
│  STOCK VALORIZADO - 10/01/2025                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  RESUMEN POR CATEGORÍA                              │
│  ┌─────────────────────────────────────────────┐   │
│  │ Categoría  │ Productos │ Stock  │ Valor    │   │
│  ├─────────────────────────────────────────────┤   │
│  │ Bebidas    │ 25        │ 850    │ 2,125,000│   │
│  │ Snacks     │ 40        │ 1,200  │ 4,800,000│   │
│  │ Almuerzos  │ 15        │ 180    │ 1,350,000│   │
│  │ Postres    │ 20        │ 320    │ 960,000  │   │
│  │ Otros      │ 20        │ 450    │ 1,125,000│   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  TOTAL GENERAL: ₲ 10,360,000                       │
│                                                     │
│  ALERTAS:                                           │
│  ⚠ 12 productos con stock bajo                     │
│  ❌ 3 productos agotados                            │
│  ⏰ 5 productos próximos a vencer                   │
│                                                     │
│  [Ver Detalle] [Exportar]                          │
└─────────────────────────────────────────────────────┘
```

### Reporte Financiero Mensual

```
Período: [Enero 2025]

INGRESOS
  Ventas en efectivo: ₲ 8,500,000
  Recargas de tarjetas: ₲ 12,000,000
  Almuerzos prepagos: ₲ 6,500,000
  ───────────────────────────────
  Total ingresos: ₲ 27,000,000

EGRESOS
  Compra de mercadería: ₲ 15,000,000
  Salarios: ₲ 7,500,000
  Servicios (luz, agua, etc): ₲ 800,000
  Otros gastos: ₲ 200,000
  ───────────────────────────────
  Total egresos: ₲ 23,500,000

RESULTADO
  Utilidad bruta: ₲ 3,500,000
  Margen: 13%

[Exportar a Excel] [Generar PDF]
```

---

## FACTURACIÓN Y CONTABILIDAD

### Generar Factura Legal

```
┌─────────────────────────────────────────────────────┐
│  GENERAR FACTURA LEGAL                              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Cliente: [Colegio ABC ▼]                          │
│  RUC: [80012345-6]                                 │
│  Dirección: [Av. España 456]                       │
│                                                     │
│  Fecha de emisión: [10/01/2025]                    │
│  Condición: [Crédito 30 días ▼]                    │
│                                                     │
│  CONCEPTOS A FACTURAR:                              │
│  ☑ Ventas del mes (₲ 2,500,000)                    │
│  ☐ Servicio de almuerzos (₲ 0)                     │
│  ☐ Otros conceptos                                 │
│                                                     │
│  Subtotal: ₲ 2,272,727                             │
│  IVA 10%: ₲ 227,273                                │
│  TOTAL: ₲ 2,500,000                                │
│                                                     │
│  Timbrado: 12345678 (vence: 31/12/2025)            │
│  Factura N°: 001-001-0000246                       │
│                                                     │
│  [Vista Previa] [Generar y Descargar]              │
└─────────────────────────────────────────────────────┘
```

### Notas de Crédito

Para anular o corregir facturas:

```
Facturación > Notas de Crédito > Agregar

  Factura a corregir: [001-001-0000245]
  Cliente: Colegio ABC
  Fecha factura original: 08/01/2025
  Monto original: ₲ 1,200,000
  
  Motivo de NC:
    ⚪ Anulación de factura
    ⚪ Devolución de mercadería
    ⚪ Descuento no aplicado
    ⚪ Error en factura
  
  Descripción: [Error en cantidad facturada]
  
  Monto de NC: [₲ 200,000]
  
  [Generar Nota de Crédito]
```

---

## BACKUP Y RESTAURACIÓN

### Backup Manual

```powershell
# Ejecutar desde terminal:
cd D:\anteproyecto20112025
.\.venv\Scripts\python.exe crear_backup_automatico.py

Resultado:
  ✓ Backup creado: backups\backup_cantinatitadb_20250110_153045.sql
  ✓ Tamaño: 15.2 MB
  ✓ Comprimido: backup_cantinatitadb_20250110_153045.zip (3.8 MB)
```

### Backup Automático Programado

**Verificar configuración**:

```powershell
Get-ScheduledTask -TaskName "Backup_Cantina_Diario"

TaskPath TaskName                   State
-------- --------                   -----
\        Backup_Cantina_Diario      Ready

# Ver detalles:
Get-ScheduledTaskInfo -TaskName "Backup_Cantina_Diario"
```

**Ubicación de backups**: `D:\backups_cantina\`

**Retención**: 30 días (los backups más antiguos se eliminan automáticamente)

### Restaurar Backup

⚠ **IMPORTANTE**: Detener el servidor antes de restaurar

```powershell
# 1. Detener servidor Django
Ctrl+C en la terminal del servidor

# 2. Restaurar desde archivo
mysql -u root -p cantinatitadb < backups\backup_cantinatitadb_20250110_153045.sql

# 3. Reiniciar servidor
python manage.py runserver
```

### Backup de Archivos Media

```powershell
# Backup de archivos subidos (fotos, etc)
Copy-Item -Path "D:\anteproyecto20112025\media" -Destination "D:\backups_cantina\media_20250110" -Recurse
```

---

## SEGURIDAD Y AUDITORÍA

### Ejecutar Auditoría de Seguridad

```powershell
python auditoria_seguridad.py

Resultados:
  Total verificaciones: 27
  Correctas: 18
  Warnings: 7
  Críticos: 2
  
  [CRÍTICOS]:
  - DEBUG desactivado en producción
  - SECRET_KEY es única y segura
  
  Reporte completo: logs/auditoria_seguridad_20250110.json
```

### Ver Logs de Auditoría

```
Panel Admin > Auditoría > Logs de cambios

Filtros:
  Usuario: [Todos ▼]
  Fecha: [Últimos 7 días ▼]
  Tipo de acción: [Todos ▼]
  Modelo: [Productos ▼]

RESULTADOS:
┌──────────────────────────────────────────────────────────────┐
│ Fecha/Hora       │ Usuario  │ Acción   │ Objeto           │
├──────────────────────────────────────────────────────────────┤
│ 10/01 15:30:45   │ admin    │ MODIFICÓ │ Producto #123    │
│ 10/01 14:20:12   │ mgonzalez│ AGREGÓ   │ Venta #456       │
│ 10/01 10:15:30   │ admin    │ ELIMINÓ  │ Promoción #78    │
└──────────────────────────────────────────────────────────────┘

[Ver detalles] para cada registro muestra:
  - Valores anteriores
  - Valores nuevos
  - IP del usuario
  - Navegador utilizado
```

### Cambios en Configuración de Seguridad

**Para producción**, modificar `settings.py`:

```python
# 1. Desactivar DEBUG
DEBUG = False

# 2. Configurar ALLOWED_HOSTS
ALLOWED_HOSTS = ['cantina-tita.edu.py', 'www.cantina-tita.edu.py']

# 3. Habilitar HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# 4. Cambiar SECRET_KEY
SECRET_KEY = 'nueva-clave-super-secreta-de-50-caracteres-minimo-xyz123'
```

---

## MANTENIMIENTO

### Optimizar Base de Datos

```powershell
# Ejecutar script de optimización:
# (primero hacer backup!)
python verificar_indices_explain.py

# Luego ejecutar en MySQL Workbench:
# Abrir archivo: optimizar_performance_bd.sql
# Ejecutar todo el script
```

### Limpiar Archivos Temporales

```powershell
# Limpiar caché de Django
python manage.py clear_cache

# Limpiar sesiones expiradas
python manage.py clearsessions

# Eliminar archivos media huérfanos (no usados en BD)
python manage.py cleanup_unused_media
```

### Actualizar Sistema

```powershell
# 1. Hacer backup completo
python crear_backup_automatico.py

# 2. Actualizar código desde repositorio
git pull origin main

# 3. Actualizar dependencias
.\.venv\Scripts\pip.exe install -r requirements.txt --upgrade

# 4. Aplicar migraciones
python manage.py migrate

# 5. Recolectar archivos estáticos
python manage.py collectstatic --noinput

# 6. Reiniciar servidor
```

---

## TROUBLESHOOTING

### Problemas Comunes

#### 1. No se pueden crear facturas

**Síntoma**: Error al generar factura legal

**Causas posibles**:
- Timbrado vencido
- Numeración agotada
- Permisos de usuario

**Solución**:
```
1. Verificar timbrado en Configuración > Facturación
2. Si está vencido, cargar nuevo timbrado
3. Verificar permisos del usuario
```

#### 2. Stock negativo

**Síntoma**: Productos con stock en negativo

**Solución**:
```powershell
# Ejecutar desde Django shell:
python manage.py shell

>>> from gestion.models import StockUnico
>>> stocks_negativos = StockUnico.objects.filter(stock_actual__lt=0)
>>> for s in stocks_negativos:
...     print(f"{s.id_producto.descripcion}: {s.stock_actual}")
...     s.stock_actual = 0
...     s.save()
```

#### 3. Error de conexión a BD

**Síntoma**: "Can't connect to MySQL server"

**Solución**:
```powershell
# 1. Verificar que MySQL está corriendo
Get-Service -Name MySQL*

# 2. Si está detenido, iniciarlo:
Start-Service -Name MySQL80

# 3. Verificar credenciales en settings.py
```

#### 4. Reportes muy lentos

**Solución**:
```powershell
# Optimizar tablas:
python verificar_indices_explain.py
# Revisar warnings y ejecutar optimizar_performance_bd.sql
```

### Logs del Sistema

**Ubicación de logs**:
```
logs/
├── django.log              # Log general de Django
├── ventas.log             # Log de módulo de ventas
├── errores.log            # Solo errores críticos
└── verificacion_*.json    # Reportes de verificación
```

**Ver últimos errores**:
```powershell
Get-Content .\logs\errores.log -Tail 50
```

---

## CONTACTO Y SOPORTE TÉCNICO

**Desarrollador**:  
Email: soporte.tecnico@cantina-tita.edu.py  
Teléfono: +595 981 999 888

**Horario de soporte**:  
Lun-Vie: 8:00-18:00  
Emergencias: 24/7 (solo incidentes críticos)

---

*Manual de Administrador - Sistema Cantina Tita v1.0*  
*Última actualización: Enero 2025*
