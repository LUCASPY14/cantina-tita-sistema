# 🧪 GUÍA: Probando Ventas Reales con Facturación Electrónica

## ✅ Lo que Acabamos de Hacer

Creamos exitosamente **una venta real (#88)** en el sistema:

```
Venta #88
├── Estudiante: PERÉZ, PEDRO
├── Productos: 2 unidades
│   ├── COCA COLA 250 ML (₲5,000)
│   └── PULP NARANJA 250ML (₲5,000)
├── Total: ₲10,000
└── Estado: PROCESADA
```

**Datos de la Venta:**
- **ID**: 88
- **Fecha**: 09/01/2026 a las 23:17
- **Cliente**: PERÉZ, JUAN (4567891-2)
- **Monto**: ₲10,000
- **Detalles guardados**: ✅ 2 productos

---

## 📊 Estadísticas Actuales del Sistema

```
Total de Ventas:      55 ventas
Total Facturadas:     0 (aún)
Monto Total:          ₲584,700
Modo Facturación:     TESTING (simulado)
Timbrados Activos:    1
```

---

## 🌐 Cómo Acceder al Dashboard de Facturación

### Opción 1: URL Directa
Abre en tu navegador:
```
http://localhost:8000/reportes/facturacion/dashboard/
```

### Opción 2: Desde el Admin
1. Ve a: http://localhost:8000/admin/
2. Busca "Facturación" en el menú lateral
3. Haz clic en "Facturas Electrónicas"

---

## 🎯 Qué Verás en el Dashboard

El dashboard mostrará:

### 📈 Tarjetas de Estadísticas
- **Facturas Emitidas**: 0 (porque aún no hay timbrado asociado)
- **Aceptadas (SET)**: 0
- **Rechazadas (SET)**: 0
- **Pendientes**: 0
- **Monto Emitido**: ₲0

### 📋 Listado de Timbrados
Mostrará el timbrado **12345678** como activo

### 🔗 Acciones Rápidas
- Ver Listado de Facturas
- Ver Reporte de Cumplimiento
- Ir a POS General

---

## 🚀 Próximas Pruebas

### 1️⃣ Crear una Factura Real desde la Venta #88

Para que la venta #88 genere factura, necesitas:

**Opción A: Desde Admin (Manual)**
```
1. Ve a http://localhost:8000/admin/
2. Ve a Ventas → Venta #88
3. En el formulario, llena:
   - Timbrado: 12345678 (Factura)
   - Nro_Factura_Venta: (auto-generado)
4. Guarda
5. Vuelve al Dashboard - verás la factura!
```

**Opción B: Desde POS (Automático)**
```
1. Ve a http://localhost:8000/pos/general/
2. Selecciona un estudiante
3. Agrega productos al carrito
4. Click en "Procesar Pago"
5. Activa checkbox: "✓ Emitir Factura Electrónica"
6. Completa el pago
→ ¡La factura se genera automáticamente en MODO TESTING!
```

### 2️⃣ Ver la Factura Generada

Una vez emitida, verás en el dashboard:
- CDC: `ABC...` (código único)
- Estado: `ACEPTADA` (en testing)
- KUDE: Botón para descargar QR
- Botón para Anular (si es necesario)

### 3️⃣ Descargar el KUDE

```
1. Ve al Listado de Facturas
2. Busca la factura
3. Haz clic en "📱 QR"
4. Se descarga el código QR autenticado
```

---

## 📚 Entender los Certificados Digitales

**Pregunta**: ¿Qué son los certificados digitales?

**Respuesta**: 
- Archivos especiales (`.pem`) que SET exige para firmar facturas en **PRODUCCIÓN**
- Son como una "firma electrónica" legal
- Solo necesarios cuando cambies a `EKUATIA_MODO=produccion`
- En `MODO TESTING` (actual), **NO se necesitan**

**¿Por qué no los necesitas ahora?**
```
MODO TESTING:
- Simula completamente las respuestas de Ekuatia
- No se conecta al servidor real de SET
- Las facturas se marcan como "ACEPTADAS" automáticamente
- Perfecto para desarrollo y pruebas

MODO PRODUCCIÓN:
- Necesita credenciales reales de SET
- Necesita certificado digital para firmar XML
- Se conecta al servidor real
- Las facturas se envían verdaderamente a SET
```

---

## 🧪 Crear Más Ventas de Prueba

Para ver estadísticas, crea más ventas:

### Opción 1: Script Python (Rápido)
```bash
cd d:\anteproyecto20112025
python prueba_venta_real.py
# Crea una venta automáticamente
```

### Opción 2: POS General (Realista)
```
1. http://localhost:8000/pos/general/
2. Selecciona estudiante
3. Agrega productos
4. Procesa pago
5. ✓ Emitir Factura Electrónica
6. ¡Listo!
```

### Opción 3: Admin (Manual)
```
1. http://localhost:8000/admin/
2. Ventas → Agregar Venta
3. Llena todos los campos
4. Guarda
```

---

## 📊 Ver Progreso en Real Tiempo

```bash
# Terminal 1: Servidor Django corriendo
python manage.py runserver 0.0.0.0:8000

# Terminal 2: Ver ventas
python verificar_ventas.py

# Terminal 3: Crear venta de prueba
python prueba_venta_real.py
```

---

## ❓ Preguntas Frecuentes

**P: ¿En qué modo está el sistema?**
R: `EKUATIA_MODO=testing` - Ver en cantina_project/settings.py

**P: ¿Las facturas son reales?**
R: No, son simuladas. Para producción necesitas: API keys reales + certificados.

**P: ¿Puedo cambiar a modo producción?**
R: Sí, pero primero obtén:
- `EKUATIA_API_KEY` de SET
- `EKUATIA_CERT_PATH` (certificado digital)
- `EKUATIA_KEY_PATH` (clave privada)

**P: ¿Dónde se guardan las ventas?**
R: En la tabla `ventas` de MySQL

**P: ¿Dónde se guardan las facturas?**
R: En la tabla `datos_facturacion_elect` (cuando se emiten)

---

## 🎓 Conceptos Clave

### Venta vs Factura
```
VENTA = Transacción de compra
├── Cliente
├── Productos
├── Monto Total
└── Detalles de pago

FACTURA ELECTRÓNICA = Documento fiscal de la venta
├── CDC (Código Control)
├── XML (Formato SET)
├── KUDE (Código QR)
└── Validación en Ekuatia/SET
```

### Estado de Factura
```
ACEPTADA    → SET validó, es legal
RECHAZADA   → Tiene errores, hay que revisar
PENDIENTE   → Esperando respuesta de SET
ANULADA     → Se canceló
```

### CDC (Código de Control Criptográfico)
```
CDC = SHA256(RUC + Tipo_Doc + Timbrado + Numero + Cantidad_Lineas + Monto + Fecha)
     ↓
   44 caracteres hexadecimales únicos para cada factura
```

---

## ✨ Resumen

✅ **¿Qué probaste?**
- Creación de venta completa (#88)
- Sistema de facturación en modo TESTING
- Integración POS ↔ Facturación
- Dashboard de estadísticas

✅ **¿Qué NO necesitas todavía?**
- Credenciales Ekuatia reales
- Certificados digitales
- Configurar impresora

✅ **¿Cuál es el siguiente paso?**
- Crear más ventas (desde POS o script)
- Ver estadísticas en dashboard
- Cuando estés listo para PRODUCCIÓN:
  - Obtener API keys de SET
  - Obtener certificados digitales
  - Cambiar `EKUATIA_MODO=produccion`
  - Configurar impresora térmica real

---

**¡Ahora accede al dashboard y explora!**  
👉 http://localhost:8000/reportes/facturacion/dashboard/
