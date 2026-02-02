# Integración con Base de Datos Existente

## Resumen

Este sistema Django está integrado con una base de datos MySQL existente (`cantinatitadb`) que contiene 63 tablas y 11 vistas.

## Estructura de la Base de Datos

### Tablas Principales

#### **Clientes y Usuarios**
- `clientes` - Información de clientes (estudiantes, profesores, personal)
- `tipos_cliente` - Clasificación de clientes
- `hijos` - Hijos de clientes responsables
- `tarjetas` - Tarjetas de estudiantes con saldo
- `usuarios_web_clientes` - Acceso web para clientes

#### **Productos e Inventario**
- `productos` - Catálogo de productos
- `categorias` - Categorías jerárquicas de productos
- `stock_unico` - Stock actual de cada producto
- `unidades_medida` - Unidades (kg, litro, unidad, etc.)
- `impuestos` - Tasas de IVA (5%, 10%, exento)
- `movimientos_stock` - Historial de movimientos de inventario
- `ajustes_inventario` - Ajustes manuales de stock

#### **Ventas**
- `ventas` - Registro de ventas
- `detalle_venta` - Items de cada venta
- `pagos_venta` - Pagos asociados a ventas
- `medios_pago` - Efectivo, tarjeta, transferencia, etc.
- `tipos_pago` - Clasificación de formas de pago
- `documentos_tributarios` - Facturas y documentos

#### **Compras**
- `compras` - Compras a proveedores
- `detalle_compra` - Items de cada compra
- `proveedores` - Información de proveedores
- `cta_corriente_prov` - Cuenta corriente de proveedores
- `costos_historicos` - Historial de costos de productos

#### **Precios**
- `listas_precios` - Diferentes listas de precios
- `precios_por_lista` - Precio de cada producto por lista
- `historico_precios` - Cambios de precios en el tiempo

#### **Empleados**
- `empleados` - Personal de la cantina
- `tipos_rol_general` - Roles (administrador, cajero, etc.)
- `cajas` - Cajas registradoras
- `cierres_caja` - Cierres diarios de caja

#### **Sistema de Almuerzos**
- `planes_almuerzo` - Planes mensuales de almuerzo
- `suscripciones_almuerzo` - Suscripciones activas
- `registro_consumo_almuerzo` - Control de asistencia
- `pagos_almuerzo_mensual` - Pagos mensuales

#### **Cuenta Corriente**
- `cta_corriente` - Movimientos de cuenta corriente de clientes
- `cargas_saldo` - Recargas de saldo en tarjetas

#### **Facturación**
- `timbrados` - Timbrados fiscales
- `puntos_expedicion` - Puntos de expedición
- `datos_facturacion_elect` - Datos de facturación electrónica (CDC)
- `datos_facturacion_fisica` - Numeración de facturas físicas
- `notas_credito` - Devoluciones y notas de crédito

#### **Comisiones**
- `tarifas_comision` - Tarifas por medio de pago
- `detalle_comision_venta` - Comisiones calculadas
- `conciliacion_pagos` - Conciliación bancaria

#### **Auditoría y Seguridad**
- `auditoria_empleados` - Log de cambios de empleados
- `auditoria_usuarios_web` - Log de accesos web
- `auditoria_comisiones` - Cambios en tarifas

#### **Notificaciones**
- `alertas_sistema` - Alertas generales del sistema
- `solicitudes_notificacion` - Cola de notificaciones (SMS, WhatsApp, Email)

### Vistas de Consulta

- `v_stock_alerta` - Productos con stock bajo
- `v_saldo_clientes` - Saldos de cuenta corriente
- `v_saldo_proveedores` - Saldos de proveedores
- `v_ventas_dia` - Resumen de ventas del día
- `v_productos_mas_vendidos` - Top productos
- `v_resumen_caja_diario` - Resumen de caja
- `v_control_asistencia` - Asistencia de almuerzos
- `v_tarjetas_detalle` - Detalle de tarjetas y saldos
- `v_alertas_pendientes` - Alertas sin resolver
- `v_resumen_silencioso_hijo` - Resumen por hijo
- `v_saldo_tarjetas_compras` - Saldo de tarjetas de compras

## Modelos Django

### Configuración `managed = False`

Los modelos en `models_existentes.py` usan `managed = False` para:
- Leer y escribir en tablas existentes
- No intentar crear/modificar tablas
- Mantener compatibilidad con el sistema existente

### Modelos Disponibles

```python
# Tablas existentes (models_existentes.py)
ClienteExistente
ProductoExistente
StockUnico
Categoria
Proveedor
Empleado
Hijo
Tarjeta
TipoCliente
ListaPrecios
UnidadMedida
Impuesto
TipoRolGeneral
VistaStockAlerta (vista)
VistaSaldoClientes (vista)

# Nuevos modelos Django (models.py)
Cliente (sistema Django)
Producto (sistema Django)
Venta (sistema Django)
```

## Relaciones Importantes

### Cliente → Hijo → Tarjeta
```
clientes (responsable)
    ↓
hijos (estudiantes)
    ↓
tarjetas (tarjeta de saldo)
```

### Producto → Stock → Movimientos
```
productos (catálogo)
    ↓
stock_unico (cantidad actual)
    ↓
movimientos_stock (historial)
```

### Venta → Documento → Pago
```
ventas (transacción)
    ↓
documentos_tributarios (factura)
    ↓
pagos_venta (forma de pago)
```

### Compra → Costo → Stock
```
compras (adquisición)
    ↓
detalle_compra (productos)
    ↓
costos_historicos (precio de costo)
    ↓
movimientos_stock (entrada a inventario)
```

## Panel de Administración

### Secciones Disponibles

1. **Gestión de Tablas Existentes**
   - Clientes Existentes
   - Productos Existentes
   - Stock
   - Empleados
   - Proveedores
   - Tarjetas
   - Hijos

2. **Nuevas Funcionalidades Django**
   - Sistema de ventas Django
   - Gestión moderna de productos
   - Control de usuarios Django

3. **Vistas de Solo Lectura**
   - Alertas de Stock
   - Saldos de Clientes
   - Reportes en tiempo real

## Uso Recomendado

### Para Consultas
```python
# Ver productos con stock bajo
from gestion.models_existentes import VistaStockAlerta
productos_bajos = VistaStockAlerta.objects.all()

# Consultar clientes existentes
from gestion.models_existentes import ClienteExistente
clientes = ClienteExistente.objects.filter(activo=True)

# Ver stock actual
from gestion.models_existentes import StockUnico
stock = StockUnico.objects.select_related('id_producto')
```

### Para Modificaciones
```python
# Actualizar stock
producto = ProductoExistente.objects.get(codigo='P001')
stock = StockUnico.objects.get(id_producto=producto)
stock.stock_actual += 10
stock.save()

# Crear nuevo cliente
from gestion.models_existentes import ClienteExistente, TipoCliente
tipo = TipoCliente.objects.get(nombre_tipo='Estudiante')
cliente = ClienteExistente(
    nombres='Juan',
    apellidos='Pérez',
    ruc_ci='1234567',
    id_tipo_cliente=tipo,
    # ... otros campos
)
cliente.save()
```

## Migraciones

### No afectar tablas existentes
Las tablas con `managed = False` no se ven afectadas por:
- `python manage.py makemigrations`
- `python manage.py migrate`

### Crear solo tablas Django
Django creará únicamente:
- Tablas de autenticación (auth_user, auth_group, etc.)
- Tablas de sesiones
- Tablas de admin
- Tus modelos nuevos en `models.py` (si los hay)

## Comandos Útiles

```bash
# Ver análisis completo de la BD
python analyze_database.py

# Verificar conexión
python test_db_connection.py

# Aplicar migraciones (solo tablas Django)
python manage.py migrate

# Acceder al shell con los modelos
python manage.py shell
```

## Consideraciones Importantes

1. **No modificar estructura de tablas existentes** - El sistema actual depende de ellas
2. **Usar transacciones** - Para operaciones críticas en cuenta corriente
3. **Validar saldos** - Antes de permitir ventas con tarjeta
4. **Respetar foreign keys** - Mantener integridad referencial
5. **No eliminar datos** - Usar campos `activo` en su lugar

## Próximos Pasos

- [ ] Crear APIs REST para integración
- [ ] Desarrollar frontend moderno
- [ ] Implementar reportes avanzados
- [ ] Agregar autenticación JWT
- [ ] Crear sistema de permisos granular
- [ ] Implementar caché para consultas pesadas
- [ ] Agregar tests automatizados
