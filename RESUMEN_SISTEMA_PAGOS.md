# ================================================
# RESUMEN DE IMPLEMENTACIÓN: SISTEMA DE PAGOS
# ================================================
# Fecha: 2025-12-09
# Objetivo: Implementar sistema completo de pagos con CONTADO/CRÉDITO

## ✅ CAMBIOS REALIZADOS

### 1. MODELO DE DATOS (gestion/models.py)
**Clase Ventas - Líneas 1025-1100**

#### Cambios en TIPO_VENTA_CHOICES:
```python
# ANTES:
TIPO_VENTA_CHOICES = [
    ('Venta Directa', 'Venta Directa'),
    ('Consumo Tarjeta', 'Consumo Tarjeta'),
    ('Carga Saldo', 'Carga Saldo'),
    ('Pago Almuerzo', 'Pago Almuerzo'),
]

# AHORA:
TIPO_VENTA_CHOICES = [
    ('CONTADO', 'Contado'),
    ('CREDITO', 'Crédito'),
]
```

#### Nuevos Campos Agregados:
```python
autorizado_por = ForeignKey(
    'Empleado',
    db_column='Autorizado_Por',
    related_name='ventas_autorizadas',
    blank=True, null=True,
    help_text='Supervisor que autorizó la venta'
)

motivo_credito = TextField(
    db_column='Motivo_Credito',
    blank=True, null=True,
    help_text='Justificación de la venta a crédito'
)

genera_factura_legal = BooleanField(
    db_column='Genera_Factura_Legal',
    default=False,
    help_text='True si genera factura contable (solo pagos externos)'
)
```

### 2. MIGRACIÓN SQL (migracion_ventas_contado_credito.sql)
**Archivo creado con ALTER TABLE statements**

```sql
-- Agregar nuevos campos
ALTER TABLE ventas ADD COLUMN Autorizado_Por INT NULL;
ALTER TABLE ventas ADD COLUMN Motivo_Credito TEXT NULL;
ALTER TABLE ventas ADD COLUMN Genera_Factura_Legal TINYINT(1) DEFAULT 0;

-- Foreign key para autorización
ALTER TABLE ventas
ADD CONSTRAINT FK_Ventas_Autorizado_Por
FOREIGN KEY (Autorizado_Por) REFERENCES empleados(ID_Empleado);

-- Índices para optimización
CREATE INDEX IDX_Ventas_Tipo_Venta ON ventas(Tipo_Venta);
CREATE INDEX IDX_Ventas_Autorizado_Por ON ventas(Autorizado_Por);
CREATE INDEX IDX_Ventas_Factura_Legal ON ventas(Genera_Factura_Legal, Tipo_Venta);

-- Actualizar datos existentes
UPDATE ventas SET Tipo_Venta = 'CONTADO' WHERE Tipo_Venta IN (...);
UPDATE ventas SET Genera_Factura_Legal = 0 WHERE Nro_Factura_Venta IS NULL;
UPDATE ventas SET Genera_Factura_Legal = 1 WHERE Nro_Factura_Venta IS NOT NULL;
```

### 3. LÓGICA DE NEGOCIO (gestion/pos_views.py)
**Función procesar_venta() - Líneas 248-700**

#### A) Validación de Saldo Insuficiente (Líneas 360-395):
```python
if usa_solo_tarjeta and tarjeta.saldo_actual < total:
    return JsonResponse({
        'success': False,
        'error': f'Saldo insuficiente. Disponible: Gs. {tarjeta.saldo_actual:,.0f}',
        'requiere_autorizacion_supervisor': True,
        'monto_faltante': int(total - tarjeta.saldo_actual)
    })
```

#### B) Determinación de Tipo de Venta (Líneas 396-450):
```python
# CASO 1: Venta a CRÉDITO con autorización de supervisor
if autorizado_por_id:
    tipo_venta_final = 'CREDITO'
    genera_factura_legal = True

# CASO 2: Venta con pagos externos (efectivo, débito, QR, etc.)
elif tiene_pagos_externos:
    tipo_venta_final = 'CONTADO'
    genera_factura_legal = True

# CASO 3: Venta solo con tarjeta exclusiva
elif tiene_tarjeta_exclusiva:
    tipo_venta_final = 'CONTADO'
    genera_factura_legal = False  # ⚠️ NO emite factura legal

# CASO 4: Venta sin tarjeta (cliente genérico)
else:
    tipo_venta_final = 'CONTADO'
    genera_factura_legal = True
```

#### C) Emisión de Factura Legal (Líneas 450-480):
```python
if genera_factura_legal:
    # Buscar timbrado activo
    timbrado_activo = Timbrados.objects.filter(activo=True).first()
    
    # Crear documento tributario
    documento = DocumentosTributarios.objects.create(
        nro_timbrado=timbrado_activo,
        nro_secuencial=nuevo_secuencial,
        fecha_emision=timezone.now(),
        monto_total=int(total),
        ...
    )
    nro_factura = documento.id_documento
else:
    nro_factura = None  # Consumo con tarjeta exclusiva
```

#### D) Registro de Pagos con Comisiones (Líneas 626-690):
```python
for pago_data in pagos_mixtos:
    medio_pago = MediosPago.objects.get(id_medio_pago=medio_id)
    
    # Calcular comisión si el medio la genera
    if medio_pago.genera_comision:
        tarifa_vigente = TarifasComision.objects.filter(
            id_medio_pago=medio_pago,
            activo=True,
            fecha_inicio_vigencia__lte=timezone.now()
        ).first()
        
        if tarifa_vigente:
            comision_porcentual = monto_pago * tarifa_vigente.porcentaje_comision
            comision_fija = tarifa_vigente.monto_fijo_comision or 0
            comision = comision_porcentual + comision_fija
            
            # Registrar en detalle_comision_venta
            DetalleComisionVenta.objects.create(
                id_pago_venta=pago_venta,
                id_tarifa=tarifa_vigente,
                monto_comision_calculada=comision,
                porcentaje_aplicado=tarifa_vigente.porcentaje_comision
            )
```

### 4. INTERFAZ DE USUARIO (templates/pos/venta.html)

#### A) Botones de Medios de Pago Actualizados (Líneas 440-475):
```html
<!-- 6 botones específicos -->
<button @click="agregarPago(1, 'Efectivo')">💵 Efectivo</button>
<button @click="agregarPago(6, 'Tarjeta Estudiantil')">🎫 Tarjeta</button>
<button @click="agregarPago(2, 'Transferencia')">🏦 Transferencia</button>
<button @click="agregarPago(3, 'Débito/QR')">💳 Débito/QR</button>
<button @click="agregarPago(4, 'Crédito/QR')">💎 Crédito/QR</button>
<button @click="agregarPago(5, 'Giros Tigo')">📱 Giros Tigo</button>
```

#### B) Modal de Autorización de Supervisor (Líneas 600-750):
```html
<dialog id="modal-autorizacion-supervisor" x-data="autorizacionSupervisorModal()">
    <!-- Muestra información de saldo insuficiente -->
    <!-- Input para escanear tarjeta de supervisor -->
    <!-- Textarea para justificación -->
    <!-- Botón para autorizar venta a crédito -->
</dialog>
```

#### C) JavaScript Alpine.js para Modal (Líneas 750-850):
```javascript
function autorizacionSupervisorModal() {
    return {
        nroTarjetaSupervisor: '',
        supervisorValidado: false,
        idSupervisor: null,
        motivoCredito: '',
        
        async validarSupervisor() {
            // Llamada AJAX a /pos/validar-supervisor/
        },
        
        autorizarCredito() {
            // Emite evento 'autorizacionAprobada'
            // con autorizado_por_id y motivo_credito
        }
    }
}
```

### 5. ENDPOINT DE VALIDACIÓN (gestion/pos_views.py)
**Nueva función: validar_supervisor() - vista_validar_supervisor.py**

```python
@login_required
@csrf_exempt
@require_http_methods(["POST"])
def validar_supervisor(request):
    """
    Valida tarjeta de supervisor para autorizar ventas a crédito.
    
    Busca:
    1. Tarjeta con tipo_autorizacion='SUPERVISOR'
    2. Empleado asociado al cliente responsable
    3. Verifica rol: SUPERVISOR, ADMINISTRADOR o GERENTE
    
    Returns:
        - success: bool
        - nombre: Nombre completo del supervisor
        - id_empleado: ID del empleado
        - rol: Nombre del rol
    """
```

### 6. URLS (gestion/pos_urls.py)
**Nueva ruta agregada - Línea 179**
```python
path('validar-supervisor/', pos_views.validar_supervisor, name='validar_supervisor'),
```

---

## 📋 MEDIOS DE PAGO CONFIGURADOS

| ID | Descripción            | Genera Comisión | Uso                           |
|----|------------------------|-----------------|-------------------------------|
| 1  | EFECTIVO               | No              | Pagos en efectivo             |
| 2  | TRANSFERENCIA BANCARIA | No              | Transferencias bancarias      |
| 3  | TARJETA DEBITO /QR     | **Sí**          | Débito, billeteras digitales  |
| 4  | TARJETA CREDITO / QR   | **Sí**          | Crédito, tarjetas bancarias   |
| 5  | GIROS TIGO             | **Sí**          | Giros Tigo Money              |
| 6  | TARJETA ESTUDIANTIL    | No              | Tarjeta exclusiva cantina     |

---

## 🔄 FLUJOS DE VENTA

### FLUJO 1: Venta con Tarjeta Exclusiva (Saldo Suficiente)
1. Escanear tarjeta estudiante
2. Agregar productos al carrito
3. Click "COBRAR"
4. Seleccionar "🎫 Tarjeta"
5. Confirmar venta
6. **Resultado:**
   - `tipo_venta` = 'CONTADO'
   - `genera_factura_legal` = False
   - `nro_factura_venta` = NULL
   - Se descuenta saldo de tarjeta

### FLUJO 2: Venta con Pagos Externos (Efectivo, Débito, etc.)
1. Agregar productos
2. Click "COBRAR"
3. Seleccionar "💵 Efectivo" y/o "💳 Débito/QR"
4. Ingresar montos
5. Confirmar venta
6. **Resultado:**
   - `tipo_venta` = 'CONTADO'
   - `genera_factura_legal` = **True**
   - `nro_factura_venta` = ID_Documento
   - Se calcula comisión si aplica
   - Se registra en `pagos_venta` y `detalle_comision_venta`

### FLUJO 3: Venta a Crédito con Autorización
1. Escanear tarjeta con saldo insuficiente
2. Sistema detecta saldo insuficiente
3. **Modal de Autorización:**
   - Escanear tarjeta de supervisor
   - Ingresar motivo del crédito
4. Click "Autorizar Venta a Crédito"
5. **Resultado:**
   - `tipo_venta` = 'CREDITO'
   - `genera_factura_legal` = **True**
   - `nro_factura_venta` = ID_Documento
   - `autorizado_por` = ID_Empleado (supervisor)
   - `motivo_credito` = Justificación ingresada
   - `saldo_pendiente` = Monto adeudado

### FLUJO 4: Venta Mixta (Tarjeta + Efectivo)
1. Escanear tarjeta
2. Agregar productos (total > saldo)
3. Click "COBRAR"
4. Seleccionar "🎫 Tarjeta" → Usar saldo disponible
5. Seleccionar "💵 Efectivo" → Completar diferencia
6. **Resultado:**
   - `tipo_venta` = 'CONTADO'
   - `genera_factura_legal` = **True** (hay pago externo)
   - 2 registros en `pagos_venta`:
     - Pago con tarjeta (ID_Medio_Pago=6)
     - Pago en efectivo (ID_Medio_Pago=1)

---

## 🧪 PRUEBAS RECOMENDADAS

### Test 1: Venta Solo Tarjeta (Sin Factura)
```
- Tarjeta: 00203 (ROMINA - Saldo: Gs. 50.000)
- Productos: 2 items x Gs. 5.000 = Gs. 10.000
- Medio: Solo tarjeta
- Verificar:
  ✓ tipo_venta = 'CONTADO'
  ✓ genera_factura_legal = False
  ✓ nro_factura_venta IS NULL
  ✓ saldo_actual se reduce a Gs. 40.000
```

### Test 2: Venta Efectivo (Con Factura)
```
- Cliente: Genérico
- Productos: Gs. 25.000
- Medio: Efectivo
- Verificar:
  ✓ tipo_venta = 'CONTADO'
  ✓ genera_factura_legal = True
  ✓ nro_factura_venta = 001-001-XXXXXXX
  ✓ Registro en documentos_tributarios
```

### Test 3: Venta Débito/QR (Con Comisión)
```
- Productos: Gs. 100.000
- Medio: Débito/QR (ID=3)
- Tarifa: 2.5% + Gs. 1.000
- Verificar:
  ✓ Comisión = (100.000 * 0.025) + 1.000 = Gs. 3.500
  ✓ Registro en detalle_comision_venta
  ✓ monto_comision_calculada = 3500
  ✓ porcentaje_aplicado = 0.025
```

### Test 4: Autorización Supervisor (Crédito)
```
- Tarjeta: 00203 (Saldo: Gs. 5.000)
- Productos: Gs. 30.000
- Sistema detecta saldo insuficiente
- Escanear tarjeta supervisor
- Motivo: "Autorizado por padre"
- Verificar:
  ✓ tipo_venta = 'CREDITO'
  ✓ genera_factura_legal = True
  ✓ autorizado_por = ID del supervisor
  ✓ motivo_credito = "Autorizado por padre"
  ✓ saldo_pendiente = Gs. 30.000
```

### Test 5: Pago Mixto (Tarjeta + Efectivo)
```
- Tarjeta: Saldo Gs. 20.000
- Total: Gs. 50.000
- Pagos:
  - Tarjeta: Gs. 20.000
  - Efectivo: Gs. 30.000
- Verificar:
  ✓ 2 registros en pagos_venta
  ✓ genera_factura_legal = True (hay efectivo)
  ✓ Suma de montos = total
```

---

## 📊 TABLAS AFECTADAS

### ventas
- ✅ Tipo_Venta: 'CONTADO' o 'CREDITO'
- ✅ Autorizado_Por: FK a empleados
- ✅ Motivo_Credito: TEXT
- ✅ Genera_Factura_Legal: TINYINT(1)

### pagos_venta
- Registra cada pago aplicado
- Relaciona venta con medio de pago
- Campo: referencia_transaccion para QR/transferencias

### detalle_comision_venta
- Registra comisiones calculadas
- Relaciona pago con tarifa aplicada
- Campos: monto_comision_calculada, porcentaje_aplicado

### documentos_tributarios
- Solo se crea si genera_factura_legal = True
- Contiene: nro_secuencial, monto_total, timbrado

---

## 🚀 PRÓXIMOS PASOS

### 1. Ejecutar Migración SQL
```bash
mysql -u root -p cantinatitadb < migracion_ventas_contado_credito.sql
```

### 2. Copiar Vista de Validación
Agregar contenido de `vista_validar_supervisor.py` al final de `gestion/pos_views.py`

### 3. Reiniciar Servidor
```bash
python manage.py runserver
```

### 4. Configurar Tarifas de Comisión
Ir a Django Admin → Tarifas de Comisión:
- Débito/QR: 2.5% + Gs. 1.000
- Crédito/QR: 3.5% + Gs. 1.500
- Giros Tigo: 1.5% + Gs. 500

### 5. Crear Tarjeta de Supervisor
En Django Admin → Tarjetas:
- Asignar tipo_autorizacion = 'SUPERVISOR'
- Asociar a empleado con rol SUPERVISOR

---

## ⚠️ NOTAS IMPORTANTES

1. **Factura Legal:**
   - SOLO se emite para ventas con pagos externos
   - Consumos con tarjeta exclusiva NO generan factura contable

2. **Comisiones:**
   - Se calculan automáticamente según tarifa vigente
   - Incluyen porcentaje + monto fijo (si existe)
   - Se registran en tabla separada para auditoría

3. **Autorización Supervisor:**
   - Requerida para saldo insuficiente
   - Genera venta a CRÉDITO
   - Debe tener justificación obligatoria

4. **Tipos de Venta:**
   - CONTADO: Pago inmediato (con o sin tarjeta)
   - CREDITO: Pago diferido con autorización

---

## 📞 SOPORTE

Para dudas o problemas:
- Revisar logs del servidor: Terminal → Python output
- Verificar estructura BD: `DESCRIBE ventas;`
- Consultar medios de pago: `SELECT * FROM medios_pago;`
- Ver tarifas: `SELECT * FROM tarifas_comision WHERE activo=1;`

---

**Implementación completada exitosamente ✅**
Fecha: 2025-12-09
Sistema: Cantina Tita POS
