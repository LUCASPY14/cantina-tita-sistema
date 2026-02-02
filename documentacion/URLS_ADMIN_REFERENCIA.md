# 🔗 URLs CORRECTAS DEL ADMIN - CANTINA TITA

## 📋 URLs Principales del Admin

### Acceso Principal
- **Admin Home**: http://127.0.0.1:8000/admin/
- **Dashboard Custom**: http://127.0.0.1:8000/admin/dashboard/

---

## 🏪 URLs por Módulo

### 👥 CLIENTES Y USUARIOS
- **Clientes**: http://127.0.0.1:8000/admin/gestion/cliente/
- **Hijos**: http://127.0.0.1:8000/admin/gestion/hijo/
- **Tarjetas**: http://127.0.0.1:8000/admin/gestion/tarjeta/
- **Usuarios Portal**: http://127.0.0.1:8000/admin/gestion/usuarioportal/
- **Tipos de Cliente**: http://127.0.0.1:8000/admin/gestion/tipocliente/

### 🛒 VENTAS Y TRANSACCIONES
- **Ventas**: http://127.0.0.1:8000/admin/gestion/ventas/ ⭐ (NOTA: plural)
- **Detalle de Ventas**: http://127.0.0.1:8000/admin/gestion/detalleventa/
- **Pagos de Ventas**: http://127.0.0.1:8000/admin/gestion/pagosventa/
- **Recargas de Saldo**: http://127.0.0.1:8000/admin/gestion/cargassaldo/
- **Consumos con Tarjeta**: http://127.0.0.1:8000/admin/gestion/consumotarjeta/

### 📦 PRODUCTOS E INVENTARIO
- **Productos**: http://127.0.0.1:8000/admin/gestion/producto/
- **Categorías**: http://127.0.0.1:8000/admin/gestion/categoria/
- **Stock**: http://127.0.0.1:8000/admin/gestion/stockunico/
- **Proveedores**: http://127.0.0.1:8000/admin/gestion/proveedor/
- **Compras**: http://127.0.0.1:8000/admin/gestion/compras/
- **Ajustes de Inventario**: http://127.0.0.1:8000/admin/gestion/ajustesinventario/

### 👨‍💼 EMPLEADOS Y ROLES
- **Empleados**: http://127.0.0.1:8000/admin/gestion/empleado/
- **Roles**: http://127.0.0.1:8000/admin/gestion/tiporolgeneral/
- **Auditoría Empleados**: http://127.0.0.1:8000/admin/gestion/auditoriaempleados/

### 💰 CAJA Y FINANZAS
- **Cajas**: http://127.0.0.1:8000/admin/gestion/cajas/
- **Cierres de Caja**: http://127.0.0.1:8000/admin/gestion/cierrescaja/
- **Medios de Pago**: http://127.0.0.1:8000/admin/gestion/mediospago/
- **Tipos de Pago**: http://127.0.0.1:8000/admin/gestion/tipospago/
- **Conciliación de Pagos**: http://127.0.0.1:8000/admin/gestion/conciliacionpagos/

### 🍽️ ALMUERZOS
- **Planes de Almuerzo**: http://127.0.0.1:8000/admin/gestion/planesalmuerzo/
- **Suscripciones**: http://127.0.0.1:8000/admin/gestion/suscripcionesalmuerzo/
- **Registros de Consumo**: http://127.0.0.1:8000/admin/gestion/registroconsumoalmuerzo/
- **Pagos Mensuales**: http://127.0.0.1:8000/admin/gestion/pagosalmuerzomensual/

### 📊 PRECIOS Y COMISIONES
- **Listas de Precios**: http://127.0.0.1:8000/admin/gestion/listaprecios/
- **Precios por Lista**: http://127.0.0.1:8000/admin/gestion/preciosporlista/
- **Tarifas de Comisión**: http://127.0.0.1:8000/admin/gestion/tarifascomision/
- **Histórico de Precios**: http://127.0.0.1:8000/admin/gestion/historicoprecios/

### 🔔 ALERTAS Y NOTIFICACIONES
- **Alertas del Sistema**: http://127.0.0.1:8000/admin/gestion/alertassistema/
- **Solicitudes de Notificación**: http://127.0.0.1:8000/admin/gestion/solicitudesnotificacion/

### 📄 FACTURACIÓN
- **Datos Empresa**: http://127.0.0.1:8000/admin/gestion/datosempresa/
- **Timbrados**: http://127.0.0.1:8000/admin/gestion/timbrados/
- **Puntos de Expedición**: http://127.0.0.1:8000/admin/gestion/puntosexpedicion/
- **Facturación Electrónica**: http://127.0.0.1:8000/admin/gestion/datosfacturacionelect/
- **Facturación Física**: http://127.0.0.1:8000/admin/gestion/datosfacturacionfisica/

### 📈 VISTAS Y REPORTES
- **Vista Ventas del Día**: http://127.0.0.1:8000/admin/gestion/vistaventasdiadetallado/
- **Vista Consumos Estudiante**: http://127.0.0.1:8000/admin/gestion/vistaconsumosestudiante/
- **Vista Stock Crítico**: http://127.0.0.1:8000/admin/gestion/vistastockcriticoalertas/
- **Vista Historial Recargas**: http://127.0.0.1:8000/admin/gestion/vistarecargashistorial/
- **Vista Resumen Caja**: http://127.0.0.1:8000/admin/gestion/vistaresumencajadiario/

---

## ⚠️ NOTA IMPORTANTE

**La URL de Ventas es PLURAL**: `/admin/gestion/ventas/`

Esto es porque Django genera las URLs basándose en el nombre de la clase del modelo (`Ventas`). 
Aunque el `verbose_name` sea "Venta" (singular), la URL siempre será plural.

---

## 🚀 Otros Portales del Sistema

### Sistema POS
- **URL**: http://127.0.0.1:8000/pos/

### Portal de Clientes
- **URL**: http://127.0.0.1:8000/portal/
- **Login Alternativo**: http://127.0.0.1:8000/clientes/login/

### Dashboard Unificado
- **URL**: http://127.0.0.1:8000/dashboard/

---

## 📝 Credenciales por Defecto

### Admin Django
- Usuario: `admin`
- Contraseña: `admin123`

### Empleados
- IDA_CAJA / IDA_CAJA
- TITA / TITA
- TITA2 / TITA2

### Portal Clientes
- Usuario: Email del cliente
- Contraseña: RUC/CI del cliente (por defecto)
