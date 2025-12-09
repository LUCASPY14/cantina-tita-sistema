# ================================================
# GUÍA DE IMPLEMENTACIÓN: SISTEMA DE PAGOS
# ================================================
# Cantina Tita - Sistema POS
# Fecha: 2025-12-09

## 🎯 OBJETIVO
Implementar sistema completo de pagos con:
- Tipos de venta: CONTADO y CRÉDITO
- 6 medios de pago específicos
- Cálculo automático de comisiones
- Autorización de supervisor para ventas a crédito
- Control de emisión de factura legal

---

## 📋 PRERREQUISITOS

✅ Django 5.2.8 instalado
✅ MySQL con base de datos `cantinatitadb`
✅ Servidor de desarrollo funcionando
✅ Acceso a Django Admin

---

## 🚀 PASOS DE IMPLEMENTACIÓN

### PASO 1: Ejecutar Migración SQL

**Abrir terminal/PowerShell:**

```powershell
# Activar virtual environment
.venv\Scripts\Activate.ps1

# Ejecutar migración
mysql -u root -p cantinatitadb < migracion_ventas_contado_credito.sql
```

**Verificar columnas agregadas:**
```sql
USE cantinatitadb;
DESCRIBE ventas;

-- Debe mostrar:
-- Autorizado_Por (INT NULL)
-- Motivo_Credito (TEXT NULL)
-- Genera_Factura_Legal (TINYINT(1) DEFAULT 0)
```

---

### PASO 2: Agregar Vista de Validación de Supervisor

**Abrir archivo:** `d:\anteproyecto20112025\gestion\pos_views.py`

**Ir al final del archivo (después de la última función)**

**Copiar y pegar el contenido de:** `vista_validar_supervisor.py`

**Verificar imports al inicio del archivo:**
```python
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
```

---

### PASO 3: Verificar Cambios en Modelos

**El archivo `gestion/models.py` ya tiene los cambios:**
- Clase `Ventas` con TIPO_VENTA_CHOICES actualizado
- Campos nuevos: `autorizado_por`, `motivo_credito`, `genera_factura_legal`

**NO ES NECESARIO hacer cambios manuales** ✅

---

### PASO 4: Reiniciar Servidor Django

```powershell
# Detener servidor actual (Ctrl+C)

# Reiniciar
python manage.py runserver
```

**Verificar en terminal que no hay errores** ✅

---

### PASO 5: Configurar Tarifas de Comisión

**Acceder a Django Admin:**
1. Ir a: http://127.0.0.1:8000/admin/
2. Login con credenciales de superusuario
3. Ir a: **MEDIOS DE PAGO Y CAJAS** → **Tarifas de Comisión**

**Crear tarifas para medios que generan comisión:**

#### Tarifa 1: TARJETA DEBITO /QR (ID=3)
- Medio de Pago: TARJETA DEBITO /QR
- Fecha Inicio Vigencia: 2025-01-01 00:00:00
- Fecha Fin Vigencia: (dejar vacío para vigencia indefinida)
- Porcentaje Comisión: **0.0250** (2.5%)
- Monto Fijo Comisión: **1000.00**
- Activo: ✅

#### Tarifa 2: TARJETA CREDITO / QR (ID=4)
- Medio de Pago: TARJETA CREDITO / QR
- Fecha Inicio Vigencia: 2025-01-01 00:00:00
- Fecha Fin Vigencia: (vacío)
- Porcentaje Comisión: **0.0350** (3.5%)
- Monto Fijo Comisión: **1500.00**
- Activo: ✅

#### Tarifa 3: GIROS TIGO (ID=5)
- Medio de Pago: GIROS TIGO
- Fecha Inicio Vigencia: 2025-01-01 00:00:00
- Fecha Fin Vigencia: (vacío)
- Porcentaje Comisión: **0.0150** (1.5%)
- Monto Fijo Comisión: **500.00**
- Activo: ✅

**Guardar cada tarifa** ✅

---

### PASO 6: Crear/Configurar Tarjeta de Supervisor

**Opción A: Si existe tarjeta de supervisor**
1. Ir a: Django Admin → **TARJETAS** → **Tarjetas**
2. Buscar la tarjeta del supervisor
3. Editar:
   - **Tipo Autorización:** SUPERVISOR
   - **Estado:** ACTIVA
4. Guardar

**Opción B: Si NO existe tarjeta de supervisor**
1. Crear nueva tarjeta
2. Datos:
   - **Nro Tarjeta:** (escanear o ingresar número)
   - **Estado:** ACTIVA
   - **Tipo Autorización:** SUPERVISOR
   - **ID Hijo:** (asociar al hijo del empleado supervisor)
   - **Saldo Actual:** 0 (no se usa para autorización)
3. Guardar

**IMPORTANTE:** Anotar el número de tarjeta para pruebas

---

### PASO 7: Verificar Empleado Supervisor

**En Django Admin:**
1. Ir a: **EMPLEADOS** → **Empleados**
2. Buscar empleado que será supervisor
3. Verificar:
   - **CI:** Debe coincidir con RUC/CI del cliente responsable de la tarjeta
   - **ID Rol:** Debe ser SUPERVISOR, ADMINISTRADOR o GERENTE
   - **Activo:** ✅
4. Si no existe, crear empleado con rol SUPERVISOR

---

### PASO 8: Pruebas del Sistema

#### TEST 1: Venta con Tarjeta Exclusiva (Sin Factura)
1. Ir a: http://127.0.0.1:8000/pos/
2. Escanear tarjeta estudiantil (ej: 00203)
3. Agregar 2 productos (total < saldo disponible)
4. Click **COBRAR**
5. Click **🎫 Tarjeta**
6. Ingresar monto del total
7. Click **✅ Confirmar Venta**

**Verificar:**
```sql
SELECT 
    ID_Venta, 
    Tipo_Venta, 
    Genera_Factura_Legal, 
    Nro_Factura_Venta,
    Monto_Total
FROM ventas 
ORDER BY ID_Venta DESC 
LIMIT 1;

-- Esperado:
-- Tipo_Venta = 'CONTADO'
-- Genera_Factura_Legal = 0
-- Nro_Factura_Venta = NULL
```

#### TEST 2: Venta con Efectivo (Con Factura)
1. Agregar productos (Gs. 25.000)
2. Click **COBRAR**
3. Click **💵 Efectivo**
4. Ingresar Gs. 25.000
5. Click **✅ Confirmar Venta**

**Verificar:**
```sql
SELECT 
    v.ID_Venta, 
    v.Tipo_Venta, 
    v.Genera_Factura_Legal, 
    v.Nro_Factura_Venta,
    d.Nro_Secuencial,
    d.Nro_Timbrado
FROM ventas v
INNER JOIN documentos_tributarios d ON v.Nro_Factura_Venta = d.ID_Documento
ORDER BY v.ID_Venta DESC 
LIMIT 1;

-- Esperado:
-- Tipo_Venta = 'CONTADO'
-- Genera_Factura_Legal = 1
-- Nro_Factura_Venta = [ID del documento]
-- Nro_Secuencial = [número correlativo]
```

#### TEST 3: Venta con Débito/QR (Con Comisión)
1. Agregar productos (Gs. 100.000)
2. Click **COBRAR**
3. Click **💳 Débito/QR**
4. Ingresar Gs. 100.000
5. Click **✅ Confirmar Venta**

**Verificar comisión calculada:**
```sql
SELECT 
    pv.ID_Pago_Venta,
    mp.Descripcion AS Medio_Pago,
    pv.Monto_Aplicado,
    dc.Monto_Comision_Calculada,
    dc.Porcentaje_Aplicado
FROM pagos_venta pv
INNER JOIN medios_pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
LEFT JOIN detalle_comision_venta dc ON pv.ID_Pago_Venta = dc.ID_Pago_Venta
WHERE pv.ID_Venta = (SELECT MAX(ID_Venta) FROM ventas);

-- Esperado:
-- Monto_Aplicado = 100000
-- Monto_Comision_Calculada = 3500 (100000 * 0.025 + 1000)
-- Porcentaje_Aplicado = 0.0250
```

#### TEST 4: Autorización de Supervisor (Venta a Crédito)
1. Escanear tarjeta con saldo Gs. 5.000
2. Agregar productos por Gs. 30.000
3. Click **COBRAR**
4. Click **🎫 Tarjeta**
5. **Debe aparecer error:** "Saldo insuficiente"
6. **Debe abrirse modal de autorización**
7. Escanear **tarjeta de supervisor**
8. Ingresar motivo: "Autorizado por padre"
9. Click **✅ Autorizar Venta a Crédito**

**Verificar:**
```sql
SELECT 
    v.ID_Venta,
    v.Tipo_Venta,
    v.Genera_Factura_Legal,
    v.Autorizado_Por,
    v.Motivo_Credito,
    v.Saldo_Pendiente,
    e.Nombre AS Supervisor_Nombre
FROM ventas v
LEFT JOIN empleados e ON v.Autorizado_Por = e.ID_Empleado
ORDER BY v.ID_Venta DESC 
LIMIT 1;

-- Esperado:
-- Tipo_Venta = 'CREDITO'
-- Genera_Factura_Legal = 1
-- Autorizado_Por = [ID del supervisor]
-- Motivo_Credito = 'Autorizado por padre'
-- Saldo_Pendiente = 30000
```

#### TEST 5: Pago Mixto (Tarjeta + Efectivo)
1. Escanear tarjeta con saldo Gs. 20.000
2. Agregar productos por Gs. 50.000
3. Click **COBRAR**
4. Click **🎫 Tarjeta** → Gs. 20.000
5. Click **💵 Efectivo** → Gs. 30.000
6. Verificar "Pendiente: Gs. 0" en verde
7. Click **✅ Confirmar Venta**

**Verificar múltiples pagos:**
```sql
SELECT 
    pv.ID_Pago_Venta,
    mp.Descripcion AS Medio,
    pv.Monto_Aplicado
FROM pagos_venta pv
INNER JOIN medios_pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
WHERE pv.ID_Venta = (SELECT MAX(ID_Venta) FROM ventas)
ORDER BY pv.ID_Pago_Venta;

-- Esperado: 2 registros
-- 1) TARJETA ESTUDIANTIL - 20000
-- 2) EFECTIVO - 30000
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

- [ ] Migración SQL ejecutada sin errores
- [ ] Columnas nuevas existen en tabla `ventas`
- [ ] Vista `validar_supervisor` agregada a `pos_views.py`
- [ ] Servidor Django reiniciado sin errores
- [ ] 3 tarifas de comisión creadas y activas
- [ ] Tarjeta de supervisor configurada
- [ ] Empleado supervisor existe con rol correcto
- [ ] TEST 1: Venta con tarjeta sin factura ✅
- [ ] TEST 2: Venta con efectivo con factura ✅
- [ ] TEST 3: Comisión calculada correctamente ✅
- [ ] TEST 4: Autorización supervisor funciona ✅
- [ ] TEST 5: Pago mixto registra múltiples pagos ✅

---

## 🐛 TROUBLESHOOTING

### Error: "Column 'Autorizado_Por' doesn't exist"
**Solución:** Ejecutar nuevamente la migración SQL
```bash
mysql -u root -p cantinatitadb < migracion_ventas_contado_credito.sql
```

### Error: "validar_supervisor not found"
**Solución:** Verificar que la función esté en `pos_views.py` y la URL en `pos_urls.py`

### Error: "No se encontró tarifa de comisión vigente"
**Solución:** 
1. Ir a Django Admin → Tarifas de Comisión
2. Verificar que exista tarifa con:
   - Medio de pago correcto
   - Activo = True
   - Fecha inicio <= hoy
   - Fecha fin = NULL o >= hoy

### Error: "Tarjeta de supervisor no válida"
**Solución:**
1. Verificar que la tarjeta tenga `tipo_autorizacion = 'SUPERVISOR'`
2. Verificar que el empleado asociado tenga rol SUPERVISOR/ADMIN/GERENTE
3. Verificar que CI del empleado coincida con RUC/CI del cliente

### Error al confirmar venta
**Revisar console del navegador (F12):**
- Ver errores JavaScript
- Ver respuestas de peticiones AJAX
- Verificar datos enviados al backend

**Revisar terminal del servidor:**
- Ver prints de debugging
- Ver errores Python/Django
- Ver queries SQL ejecutados

---

## 📞 CONTACTO Y SOPORTE

**Archivos de referencia:**
- `RESUMEN_SISTEMA_PAGOS.md` - Documentación completa
- `migracion_ventas_contado_credito.sql` - Script de migración
- `vista_validar_supervisor.py` - Código de validación

**Comandos útiles:**
```bash
# Ver logs en tiempo real
python manage.py runserver --verbosity 2

# Verificar migraciones Django
python manage.py showmigrations

# Crear superusuario si no existe
python manage.py createsuperuser
```

---

**¡Sistema listo para producción! 🎉**
