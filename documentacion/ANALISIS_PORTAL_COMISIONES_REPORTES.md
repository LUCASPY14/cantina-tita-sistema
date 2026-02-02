# ANÁLISIS DETALLADO: Portal Web, Comisiones y Reportes
## Sistema Cantina Tita - Base de datos: cantinatitadb

**Fecha:** 27 de Noviembre 2025

---

## 📊 RESUMEN EJECUTIVO

### Estado General:
- **Portal Web Clientes:** ❌ 0% - Estructura creada, sin datos
- **Comisiones Bancarias:** ⚠️ 30% - Medios configurados, sin tarifas
- **Reportes Avanzados:** ✅ 70% - 11/16 vistas funcionando

### Potencial Inmediato:
- **14 clientes** con email pueden registrarse en portal web
- **5 medios de pago** requieren configuración de tarifas
- **1 pago** sin comisión calculada
- **5 vistas** necesitan corrección

---

## 1️⃣ PORTAL WEB PARA CLIENTES

### 📋 Estado Actual

#### Tabla: `usuarios_web_clientes`
**Estructura:**
```sql
- ID_Cliente (int, PK, FK → Clientes)
- Usuario (varchar(50), UNIQUE, NOT NULL)
- Contrasena_Hash (char(60), NOT NULL) -- bcrypt
- Ultimo_Acceso (datetime, NULL)
- Activo (tinyint(1), DEFAULT 1)
```

**Registros:** 0 ❌
**Trigger:** ✅ `trg_usuarios_web_contrasena_update` (hash automático de contraseñas)

#### Tabla: `auditoria_usuarios_web`
**Estructura:**
```sql
- ID_Auditoria (bigint, PK, AUTO_INCREMENT)
- ID_Cliente (int, FK)
- Fecha_Cambio (datetime, NOT NULL)
- Campo_Modificado (varchar(50), NOT NULL)
- Valor_Anterior (text, NULL)
- Valor_Nuevo (text, NULL)
- IP_Origen (varchar(45), NULL)
```

**Registros:** 0 ❌

### 👥 Clientes Disponibles para Portal

**Total clientes con email:** 14

Ejemplos:
| ID | Nombre | Email | Hijos | Portal |
|----|--------|-------|-------|--------|
| 9 | JUAN PERÉZ | juan.perez@example.com | 2 | ❌ NO |
| 10 | CARMEN RODRIGUEZ | carmen.rodriguez@example.com | 1 | ❌ NO |
| 11 | MARCOS LOPEZ | ventas@abc.com.py | 1 | ❌ NO |
| 63 | Cliente Test 1 | cliente1@test.com | 2 | ❌ NO |

### 🎯 Funcionalidades a Implementar

#### PRIORIDAD ALTA
1. **Registro de Usuarios**
   - [ ] Formulario de registro (email, contraseña)
   - [ ] Validación de email único
   - [ ] Envío de email de confirmación
   - [ ] Activación de cuenta

2. **Autenticación**
   - [ ] Login con email/usuario y contraseña
   - [ ] Recuperación de contraseña
   - [ ] Sesión segura (JWT o Django sessions)
   - [ ] Logout

3. **Dashboard Cliente**
   - [ ] Vista de hijos/estudiantes vinculados
   - [ ] Saldo de tarjetas estudiantiles
   - [ ] Historial de consumos recientes
   - [ ] Resumen de pagos de almuerzos

#### PRIORIDAD MEDIA
4. **Consulta de Consumos**
   - [ ] Historial detallado por hijo
   - [ ] Filtros por fecha
   - [ ] Exportar a PDF/Excel
   - [ ] Gráficos de consumo mensual

5. **Consulta de Pagos**
   - [ ] Historial de pagos de almuerzos
   - [ ] Estado de suscripciones
   - [ ] Facturas y recibos
   - [ ] Pagos pendientes

6. **Gestión de Perfil**
   - [ ] Actualizar datos personales
   - [ ] Cambiar contraseña
   - [ ] Configurar notificaciones
   - [ ] Agregar métodos de pago

#### PRIORIDAD BAJA
7. **Funcionalidades Avanzadas**
   - [ ] Recarga de tarjetas online
   - [ ] Alertas de saldo bajo (email/SMS)
   - [ ] Chat de soporte
   - [ ] Notificaciones push

### 🛠️ Implementación Técnica

#### Backend Django
```python
# Modelo Django sugerido
class UsuarioWebCliente(models.Model):
    cliente = models.OneToOneField('Cliente', on_delete=models.CASCADE, primary_key=True)
    usuario = models.CharField(max_length=50, unique=True)
    contrasena_hash = models.CharField(max_length=60)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'usuarios_web_clientes'
```

#### Views necesarias
- `portal/registro/` - Registro de nuevo usuario
- `portal/login/` - Autenticación
- `portal/dashboard/` - Panel principal
- `portal/consumos/` - Historial de consumos
- `portal/pagos/` - Historial de pagos
- `portal/perfil/` - Gestión de perfil

#### APIs REST
```python
# APIs sugeridas
/api/portal/auth/register/     POST
/api/portal/auth/login/        POST
/api/portal/auth/logout/       POST
/api/portal/dashboard/         GET
/api/portal/hijos/             GET
/api/portal/consumos/<id>/     GET
/api/portal/pagos/<id>/        GET
/api/portal/saldo/<tarjeta>/   GET
```

### 📊 Estimación de Esfuerzo
- **Registro y autenticación:** 2-3 días
- **Dashboard básico:** 2 días
- **Consultas (consumos/pagos):** 2-3 días
- **Gestión de perfil:** 1-2 días
- **Testing y ajustes:** 2 días

**Total:** ~10-12 días de desarrollo

---

## 2️⃣ SISTEMA DE COMISIONES BANCARIAS

### 📋 Estado Actual

#### Tabla: `medios_pago` ✅
**8 medios configurados:**

| ID | Descripción | Genera Comisión | Requiere Validación | Estado |
|----|-------------|-----------------|---------------------|--------|
| 1 | EFECTIVO | ❌ No | ❌ No | ✅ Activo |
| 2 | TRANSFERENCIA BANCARIA | ❌ No | ✅ Sí | ✅ Activo |
| 3 | TARJETA DEBITO /QR | ✅ Sí | ✅ Sí | ✅ Activo |
| 4 | TARJETA CREDITO / QR | ✅ Sí | ✅ Sí | ✅ Activo |
| 5 | GIROS TIGO | ✅ Sí | ✅ Sí | ✅ Activo |
| 6 | TARJETA ESTUDIANTIL | ❌ No | ❌ No | ✅ Activo |
| 7 | Tarjeta de Crédito | ✅ Sí | ✅ Sí | ✅ Activo |
| 8 | Tarjeta de Débito | ✅ Sí | ✅ Sí | ✅ Activo |

**Análisis:**
- ✅ 5 medios generan comisión
- ❌ 0 tarifas configuradas
- ⚠️ Comisiones no se están calculando

#### Tabla: `tarifas_comision` ❌
**Estructura:**
```sql
- ID_Tarifa (int, PK, AUTO_INCREMENT)
- ID_Medio_Pago (int, FK → Medios_Pago)
- Fecha_Inicio_Vigencia (datetime, NOT NULL)
- Fecha_Fin_Vigencia (datetime, NULL)
- Porcentaje_Comision (decimal(5,4), NOT NULL) -- Ej: 0.0250 = 2.5%
- Monto_Fijo_Comision (decimal(10,2), NULL)    -- Ej: 5000.00
- Activo (tinyint(1), DEFAULT 1)
```

**Registros:** 0 ❌
**Impacto:** Las comisiones no se calculan automáticamente

#### Tabla: `detalle_comision_venta` ❌
**Estructura:**
```sql
- ID_Detalle_Comision (bigint, PK)
- ID_Pago_Venta (bigint, FK → Pagos_Venta)
- ID_Tarifa (int, FK → Tarifas_Comision)
- Monto_Comision_Calculada (decimal(10,2), NOT NULL)
- Porcentaje_Aplicado (decimal(5,4), NOT NULL)
```

**Registros:** 0 ❌
**Estado:** 1 pago sin comisión calculada

#### Tabla: `conciliacion_pagos` ❌
**Estructura:**
```sql
- ID_Conciliacion (bigint, PK)
- ID_Pago_Venta (bigint, FK, UNIQUE)
- Fecha_Acreditacion (datetime, NULL)
- Monto_Acreditado (decimal(10,2), NULL)
- Estado (enum: 'Conciliado', 'Pendiente', 'Rechazado')
- Observaciones (text, NULL)
```

**Registros:** 0 ❌

#### Tabla: `auditoria_comisiones` ❌
**Registros:** 0 ❌

### 🔔 Triggers Implementados

✅ **Sistema robusto de triggers:**
1. `trg_validar_saldo_antes_pago` - Valida saldo antes de pagar con tarjeta
2. `trg_tarjetas_saldo_resta_pago` - Descuenta saldo de tarjeta automáticamente
3. `trg_pago_comision_ai` - **Calcula comisión automáticamente** (AFTER INSERT)
4. `trg_validar_superposicion_tarifas` - Evita tarifas superpuestas
5. `trg_tarifas_comision_update` - Auditoría de cambios
6. `trg_validar_superposicion_tarifas_update` - Validación en UPDATE

### 🎯 Tarifas Sugeridas (Paraguay 2025)

| Medio de Pago | Comisión % | Monto Fijo | Total Ej. (Gs 100,000) |
|---------------|------------|------------|------------------------|
| Tarjeta Débito | 1.8% | Gs 0 | Gs 1,800 |
| Tarjeta Crédito | 3.5% | Gs 0 | Gs 3,500 |
| Giros Tigo | 2.0% | Gs 1,500 | Gs 3,500 |
| QR Débito | 1.5% | Gs 0 | Gs 1,500 |
| QR Crédito | 3.0% | Gs 0 | Gs 3,000 |

### 🛠️ Implementación Requerida

#### 1. Configuración de Tarifas
- [ ] CRUD de tarifas por medio de pago
- [ ] Validación de rangos de fechas
- [ ] Historial de cambios
- [ ] Activación/desactivación

#### 2. Cálculo Automático
**Ya implementado por trigger**, pero necesita:
- [ ] Crear tarifas iniciales
- [ ] Verificar que trigger funciona correctamente
- [ ] Reportes de comisiones

#### 3. Conciliación Bancaria
- [ ] Interfaz de conciliación
- [ ] Importar extractos bancarios
- [ ] Marcar pagos como conciliados
- [ ] Reportes de diferencias

#### 4. Reportes Financieros
- [ ] Reporte de comisiones diarias/mensuales
- [ ] Comisiones por medio de pago
- [ ] Comparativo de costos
- [ ] Exportar a Excel

### 📊 Script para Crear Tarifas Iniciales

```python
# Script sugerido: crear_tarifas_comisiones.py
from gestion.models import TarifasComision, MediosPago
from datetime import datetime
from decimal import Decimal

tarifas_data = [
    # Tarjeta Débito/QR
    {
        'medio': 'TARJETA DEBITO /QR',
        'porcentaje': Decimal('0.0180'),  # 1.8%
        'monto_fijo': None
    },
    # Tarjeta Crédito/QR
    {
        'medio': 'TARJETA CREDITO / QR',
        'porcentaje': Decimal('0.0350'),  # 3.5%
        'monto_fijo': None
    },
    # Giros Tigo
    {
        'medio': 'GIROS TIGO',
        'porcentaje': Decimal('0.0200'),  # 2.0%
        'monto_fijo': Decimal('1500.00')
    },
]

for tarifa_data in tarifas_data:
    medio = MediosPago.objects.get(descripcion=tarifa_data['medio'])
    TarifasComision.objects.create(
        id_medio_pago=medio,
        fecha_inicio_vigencia=datetime.now(),
        porcentaje_comision=tarifa_data['porcentaje'],
        monto_fijo_comision=tarifa_data['monto_fijo'],
        activo=True
    )
```

### 📊 Estimación de Esfuerzo
- **CRUD de tarifas:** 1-2 días
- **Script de tarifas iniciales:** 0.5 días
- **Interfaz de conciliación:** 2-3 días
- **Reportes de comisiones:** 1-2 días
- **Testing:** 1 día

**Total:** ~6-8 días de desarrollo

---

## 3️⃣ REPORTES AVANZADOS

### 📊 Estado de Vistas

**Total vistas:** 16
- ✅ **Funcionales:** 11 (69%)
- ❌ **Con errores:** 5 (31%)

### ✅ Vistas Funcionales

#### 1. `v_ventas_dia_detallado` ✅
**Registros:** 1
**Columnas:** 13

**Información disponible:**
- Datos de la venta (ID, fecha, monto)
- Cliente (nombres, apellidos)
- Empleado que registró
- Documento tributario (timbrado, secuencial)
- Productos vendidos (concatenados)
- Estado de pago (pagado, pendiente)

**Uso:** Reporte diario de ventas detallado

#### 2. `v_productos_mas_vendidos` ✅
**Registros:** 2
**Columnas:** 7

**Información:**
- ID_Producto, Código, Descripción
- Total_Vendido (cantidad)
- Total_Ingresos (monto)
- Numero_Ventas
- Precio_Promedio

**Ejemplo:**
```
- COCA COLA 250 ML: 1 unidad, Gs 5,500, 1 venta
- Almuerzo Completo: 1 unidad, Gs 26,400, 1 venta
```

**Uso:** Análisis de productos top

#### 3. `v_resumen_caja_diario` ✅
**Registros:** 1
**Columnas:** 11

**Información:**
- Fecha
- Total_Ventas, Monto_Total_Ventas
- Total_Recargas, Monto_Total_Recargas
- Total_Ingresos_Dia
- Desglose por medio de pago (efectivo, tarjetas, transferencias)

**Ejemplo:**
```
Fecha: 2025-11-25
- Ventas: 1 (Gs 31,900)
- Recargas: 0 (Gs 0)
- Total: Gs 31,900
```

**Uso:** Cierre de caja diario

#### 4. `v_stock_critico_alertas` ✅
**Registros:** 28
**Columnas:** 6

**Información:**
- ID_Producto, Código, Descripción
- Stock_Minimo
- Nombre_Categoria
- Nivel_Alerta

**Uso:** Alertas de inventario bajo

#### 5. `v_consumos_estudiante` ✅
**Registros:** 18
**Columnas:** 11

**Información:**
- Datos del estudiante
- Responsable
- Nro_Tarjeta, Saldo_Actual
- Total_Consumos, Total_Consumido
- Ultimo_Consumo
- Total_Recargas, Total_Recargado

**Uso:** Resumen de actividad por estudiante

#### 6. `v_saldo_clientes` ✅
**Registros:** 1
**Columnas:** 9

**Información:**
- Datos del cliente
- Saldo_Actual (cuenta corriente)
- Ultima_Actualizacion
- Total_Movimientos

**Ejemplo:**
```
JUAN PERÉZ: Saldo Gs 600,000, RUC: 4567891-2, 4 movimientos
```

**Uso:** Estado de cuentas corrientes

#### 7-11. Otras vistas funcionales:
- `v_alertas_pendientes` (2 registros)
- `v_notas_credito_detallado` (7 registros)
- `v_recargas_historial` (3 registros)
- `v_saldo_proveedores` (13 registros)
- `v_stock_alerta` (10 registros)

### ❌ Vistas Con Errores

**Error común:** `(1356, "View references invalid table(s) or column(s)")`

1. **v_control_asistencia** ❌
2. **v_resumen_silencioso_hijo** ❌
3. **v_saldo_tarjetas_compras** ❌
4. **v_tarjetas_detalle** ❌
5. **v_ventas_dia** ❌

**Causa probable:**
- Referencias a columnas que no existen
- Tablas renombradas
- Permisos de usuario MySQL insuficientes

**Acción requerida:**
```sql
-- Ver definición de vista con error
SHOW CREATE VIEW v_control_asistencia;

-- Eliminar vista con error
DROP VIEW IF EXISTS v_control_asistencia;

-- Recrear con estructura correcta
CREATE VIEW v_control_asistencia AS ...
```

### 🎯 Reportes a Implementar

#### PRIORIDAD ALTA

1. **Dashboard Ejecutivo**
   - [ ] Ventas del día/mes/año
   - [ ] Productos más vendidos
   - [ ] Estado de caja
   - [ ] Alertas de stock
   - [ ] Gráficos de tendencias

2. **Reporte de Ventas**
   - [ ] Por período (diario, semanal, mensual)
   - [ ] Por empleado
   - [ ] Por medio de pago
   - [ ] Por cliente
   - [ ] Exportar a Excel/PDF

3. **Reporte de Inventario**
   - [ ] Stock actual
   - [ ] Productos bajo mínimo
   - [ ] Movimientos de stock
   - [ ] Valorización de inventario

#### PRIORIDAD MEDIA

4. **Reporte de Almuerzos**
   - [ ] Consumos diarios
   - [ ] Por estudiante
   - [ ] Por plan
   - [ ] Facturación mensual
   - [ ] Estadísticas de asistencia

5. **Reporte de Tarjetas**
   - [ ] Recargas por período
   - [ ] Consumos por tarjeta
   - [ ] Saldos actuales
   - [ ] Tarjetas inactivas

6. **Reporte Financiero**
   - [ ] Cuentas por cobrar
   - [ ] Cuentas por pagar (proveedores)
   - [ ] Comisiones bancarias
   - [ ] Estado de resultados básico

#### PRIORIDAD BAJA

7. **Reportes Avanzados**
   - [ ] Análisis ABC de productos
   - [ ] Tendencias de venta
   - [ ] Predicción de demanda
   - [ ] Análisis de rentabilidad

### 🛠️ Implementación Técnica

#### Views Django sugeridas

```python
# views.py
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'reportes/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Datos del día
        hoy = date.today()
        
        # Vista: v_resumen_caja_diario
        context['resumen_caja'] = VResumenCajaDiario.objects.filter(
            fecha=hoy
        ).first()
        
        # Vista: v_productos_mas_vendidos
        context['top_productos'] = VProductosMasVendidos.objects.all()[:10]
        
        # Vista: v_stock_critico_alertas
        context['alertas_stock'] = VStockCriticoAlertas.objects.all()[:5]
        
        return context
```

#### APIs para gráficos

```python
# api/views.py
class VentasDiariasAPI(APIView):
    """API para gráfico de ventas diarias"""
    
    def get(self, request):
        dias = request.GET.get('dias', 30)
        fecha_desde = date.today() - timedelta(days=int(dias))
        
        datos = VResumenCajaDiario.objects.filter(
            fecha__gte=fecha_desde
        ).values('fecha', 'total_ventas', 'monto_total_ventas')
        
        return Response(list(datos))
```

### 📊 Estimación de Esfuerzo

- **Corrección de vistas con error:** 1 día
- **Dashboard ejecutivo:** 2-3 días
- **Reportes de ventas:** 2 días
- **Reportes de inventario:** 1-2 días
- **Reportes de almuerzos:** 1-2 días
- **Exportación (Excel/PDF):** 1-2 días
- **Gráficos interactivos:** 2-3 días

**Total:** ~10-15 días de desarrollo

---

## 🎯 PLAN DE IMPLEMENTACIÓN RECOMENDADO

### Fase 1: Comisiones Bancarias (1 semana)
**Prioridad:** ALTA
**Razón:** Ya está casi implementado, solo falta configuración

**Tareas:**
1. ✅ Crear script de tarifas iniciales
2. ✅ CRUD de tarifas en admin
3. ✅ Verificar cálculo automático (trigger)
4. ✅ Reporte básico de comisiones

**Entregable:**
- Comisiones calculándose automáticamente
- Reporte mensual de comisiones

### Fase 2: Reportes Avanzados (2 semanas)
**Prioridad:** ALTA
**Razón:** Datos ya disponibles, solo falta UI

**Tareas:**
1. ✅ Corregir 5 vistas con error
2. ✅ Dashboard ejecutivo con métricas clave
3. ✅ Reportes de ventas (diario/mensual)
4. ✅ Reportes de inventario
5. ✅ Exportación a Excel

**Entregable:**
- Dashboard funcional con datos reales
- 5-10 reportes descargables

### Fase 3: Portal Web Clientes (2-3 semanas)
**Prioridad:** MEDIA
**Razón:** Requiere más desarrollo, pero alto valor

**Tareas:**
1. ✅ Sistema de registro/login
2. ✅ Dashboard cliente básico
3. ✅ Consulta de consumos
4. ✅ Consulta de pagos
5. ✅ Gestión de perfil

**Entregable:**
- Portal web funcional
- 14 clientes pueden registrarse

---

## 📊 MÉTRICAS DE ÉXITO

### Comisiones:
- [ ] 100% de pagos con tarjeta tienen comisión calculada
- [ ] Reporte mensual generado automáticamente
- [ ] Ahorro de X horas/mes en cálculos manuales

### Reportes:
- [ ] 16/16 vistas funcionando (100%)
- [ ] Dashboard con datos en tiempo real
- [ ] 10+ reportes disponibles para descarga

### Portal Web:
- [ ] 50%+ de clientes registrados (7/14)
- [ ] 100+ consultas de consumos/mes
- [ ] Reducción de llamadas de consulta en 30%

---

## 🚀 PRÓXIMOS PASOS INMEDIATOS

1. **Crear script de tarifas de comisiones** (30 minutos)
   ```bash
   python crear_tarifas_comisiones.py
   ```

2. **Corregir vistas con error** (2-3 horas)
   - Investigar definiciones
   - Corregir referencias
   - Probar cada vista

3. **Crear dashboard básico** (1 día)
   - Template HTML
   - View en Django
   - 4-5 métricas clave

¿Con cuál fase quieres empezar?
