# 🧪 Guía Rápida de Testing - Features Nuevas

**Versión:** 1.0  
**Fecha:** 2025-01-21

---

## 🎯 Objetivo

Verificar que las 3 features implementadas funcionan correctamente antes de desplegar en producción.

---

## 📋 Pre-requisitos

1. **Base de datos actualizada:**
   ```bash
   python aplicar_features_nuevas.py
   ```
   ✅ Debe mostrar: "6 tablas creadas, 10 alérgenos insertados, 1 promoción creada"

2. **Servidor de desarrollo corriendo:**
   ```bash
   python manage.py runserver
   ```

3. **Acceso al admin:**
   http://localhost:8000/admin/
   Usuario: (tu usuario admin)

---

## 🧪 Test 1: SMTP Real (5 minutos)

### Configurar SMTP

**Opción más fácil: Gmail con App Password**

1. Ir a: https://myaccount.google.com/apppasswords
2. Crear App Password llamada "Cantina Tita"
3. Copiar el password de 16 caracteres

4. Crear archivo `.env` en raíz del proyecto:
   ```env
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=tu_email@gmail.com
   EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
   ```

5. Reiniciar servidor Django

### Probar envío

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail

send_mail(
    subject='🎉 Test desde Cantina Tita',
    message='Si recibes este email, SMTP está configurado correctamente.',
    from_email='cantina.tita@gmail.com',
    recipient_list=['tu_email_personal@gmail.com'],
    fail_silently=False,
)
```

**✅ Resultado esperado:**
- No debe mostrar error
- En 1-2 minutos debe llegar el email a tu bandeja de entrada
- Si va a spam, marcar como "No es spam"

**❌ Errores comunes:**
- `SMTPAuthenticationError`: App Password incorrecto
- `ConnectionRefusedError`: EMAIL_HOST o EMAIL_PORT incorrectos
- `SMTPSenderRefused`: EMAIL_HOST_USER no coincide con credenciales

---

## 🧪 Test 2: Matching Restricciones (15 minutos)

### Paso 1: Verificar alérgenos en admin

1. Ir a: http://localhost:8000/admin/
2. En sidebar: **Gestión** → **Alergenos**
3. ✅ Debe haber 10 alérgenos:
   - Maní (CRÍTICO) 🥜
   - Gluten (ALTO) 🌾
   - Lactosa (MEDIO) 🥛
   - Soja (ALTO)
   - Mariscos (CRÍTICO) 🦐
   - Huevo (MEDIO) 🥚
   - Pescado (ALTO) 🐟
   - Frutos secos (CRÍTICO) 🌰
   - Mostaza (BAJO)
   - Apio (BAJO)

### Paso 2: Asociar productos a alérgenos

1. En admin: **Gestión** → **Producto alergenos** → **Agregar producto alergeno**

2. Crear 3 asociaciones de prueba:

   **Asociación 1:**
   - Producto: Buscar "Galleta" o cualquier producto con harina
   - Alérgeno: Gluten
   - Contiene: ✅ Sí
   - Guardar

   **Asociación 2:**
   - Producto: Buscar "Chocolate" o "Leche"
   - Alérgeno: Lactosa
   - Contiene: ✅ Sí
   - Guardar

   **Asociación 3:**
   - Producto: Buscar "Galleta Pepito" o "Maní"
   - Alérgeno: Maní
   - Contiene: ✅ Sí
   - Guardar

### Paso 3: Crear tarjeta con restricciones

1. En admin: **Gestión** → **Hijos** → Seleccionar un hijo existente (o crear uno)

2. Editar el hijo:
   - **Tiene restricciones de compra:** ✅ Sí
   - **Restricciones de compra:**
     ```
     Alérgico al maní y gluten. Intolerante a lactosa.
     ```
   - **Guardar**

3. Verificar que tiene tarjeta asociada:
   - En admin: **Gestión** → **Tarjetas**
   - Buscar por nombre del hijo
   - Anotar el **Nro de tarjeta** (ej: 100001)

### Paso 4: Probar en POS

1. Ir a: http://localhost:8000/pos/venta/

2. **Escanear tarjeta:**
   - En campo "Buscar tarjeta"
   - Escribir el nro de tarjeta (ej: 100001)
   - Presionar Enter
   - ✅ Debe mostrar: Nombre del hijo + "⚠️ Restricciones activas"

3. **Test con producto CRÍTICO (Maní):**
   - Hacer clic en "Galleta Pepito" (o producto asociado a Maní)
   - **✅ Resultado esperado:**
     - Modal de alerta roja aparece
     - Mensaje: "🚫 VENTA BLOQUEADA - Producto contiene Maní (CRÍTICO)"
     - Lista de coincidencias detectadas
     - Botón "OK" para cerrar
     - **Producto NO se agrega al carrito**

4. **Test con producto MEDIO (Lactosa):**
   - Hacer clic en "Chocolate" (o producto asociado a Lactosa)
   - **✅ Resultado esperado:**
     - Modal de confirmación amarilla aparece
     - Mensaje: "⚠️ ADVERTENCIA - Producto contiene Lactosa (MEDIO)"
     - Botones: "Aceptar" / "Cancelar"
     - Si acepta → Producto se agrega al carrito
     - Si cancela → Producto NO se agrega

5. **Test con producto ALTO (Gluten):**
   - Hacer clic en producto con gluten
   - **✅ Resultado esperado:**
     - Similar a MEDIO, pero con color naranja
     - Requiere confirmación del cajero

### Paso 5: Verificar auditoría

1. Agregar producto con restricción (aceptando la advertencia)
2. Completar venta
3. En admin: **Gestión** → **Auditoria empleados**
4. Buscar última entrada con operación "VENTA_CON_RESTRICCIONES"
5. ✅ Debe tener:
   - Descripción: "Venta #XXX procesada con RESTRICCIONES ALIMENTARIAS confirmadas"
   - Estudiante: Nombre del hijo
   - Restricciones: Texto completo

---

## 🧪 Test 3: Promociones (15 minutos)

### Paso 1: Verificar promoción de ejemplo

1. En admin: **Gestión** → **Promociones**
2. ✅ Debe haber 1 promoción:
   - **Nombre:** Descuento por Volumen
   - **Tipo:** DESCUENTO_PORCENTAJE (10%)
   - **Aplica a:** TOTAL_VENTA
   - **Estado:** 🟢 Vigente
   - **Condiciones:**
     - Monto mínimo: Gs. 50.000
     - Mínimo 5 items
   - **Activo:** ✅ Sí

### Paso 2: Probar cálculo de promoción

1. Ir a: http://localhost:8000/pos/venta/

2. **Test: Carrito SIN cumplir condiciones**
   - Agregar 2 productos (total < Gs. 50.000)
   - **✅ Resultado esperado:**
     - Sidebar muestra solo "Subtotal"
     - NO aparece banner de promoción
     - Total = Subtotal (sin descuento)

3. **Test: Carrito cumple monto pero no cantidad**
   - Agregar 3 productos de Gs. 20.000 c/u (total: Gs. 60.000)
   - Solo 3 items → NO cumple min_cantidad (5)
   - **✅ Resultado esperado:**
     - NO aparece promoción

4. **Test: Carrito cumple TODAS las condiciones**
   - Agregar 5 productos (total > Gs. 50.000)
   - **✅ Resultado esperado:**
     - Aparece banner verde con 🎉
     - Texto: "Descuento por Volumen - 10% en compras >5 items"
     - Línea de descuento: "-Gs. [monto]"
     - Subtotal: Gs. 50.000
     - Descuento: -Gs. 5.000 (10%)
     - **Total: Gs. 45.000**

5. **Test: Recálculo dinámico**
   - Quitar 2 productos (quedan 3)
   - **✅ Resultado esperado:**
     - Banner de promoción DESAPARECE
     - Total vuelve a ser = Subtotal

   - Volver a agregar 2 productos
   - **✅ Resultado esperado:**
     - Banner reaparece automáticamente

### Paso 3: Verificar registro en BD

1. Completar venta con promoción aplicada
2. En admin: **Gestión** → **Promociones aplicadas**
3. ✅ Debe aparecer nueva entrada:
   - Venta: #[id]
   - Promoción: Descuento por Volumen
   - Monto descontado: Gs. [monto]
   - Fecha: [ahora]

### Paso 4: Crear promoción personalizada

1. En admin: **Promociones** → **Agregar promoción**

2. Configurar:
   ```
   Nombre: Happy Hour Cantina
   Descripción: 20% de descuento de 9am a 11am
   Tipo: DESCUENTO_PORCENTAJE
   Valor descuento: 20
   Aplica a: TOTAL_VENTA
   
   Fecha inicio: [hoy]
   Fecha fin: [en 30 días]
   Hora inicio: 09:00
   Hora fin: 11:00
   Días semana: [1,2,3,4,5]  ← Lun-Vie
   
   Monto mínimo: 10000
   Mínimo cantidad items: 1
   
   Usos máximos: 100
   Usos actuales: 0
   
   Activo: ✅
   ```

3. Guardar

4. **Probar en POS:**
   - Si es hora permitida (9am-11am) → ✅ Debe aplicar 20%
   - Si NO es hora permitida → ❌ No debe aparecer

---

## 🧪 Test 4: Integración Completa (10 minutos)

### Scenario: Venta Real Completa

**Contexto:**
- Estudiante: Juan Pérez (alérgico al gluten)
- Carrito: 6 productos
- Total: Gs. 55.000
- Promoción aplicable: 10% desc.

**Pasos:**

1. **Escanear tarjeta de Juan**
   - ✅ Aparece: "Juan Pérez - ⚠️ Restricciones activas"

2. **Agregar productos SIN gluten:**
   - Jugo → ✅ Agregado sin alerta
   - Chocolate → ⚠️ Advertencia lactosa (MEDIO) → Aceptar
   - Chips → ✅ Agregado sin alerta

3. **Intentar agregar producto CON gluten:**
   - Galleta → 🚫 BLOQUEADO
   - No se agrega al carrito

4. **Agregar más productos:**
   - Total: 6 items, Gs. 55.000

5. **Verificar promoción:**
   - ✅ Banner aparece: "Descuento por Volumen"
   - ✅ Descuento: -Gs. 5.500
   - ✅ Total final: Gs. 49.500

6. **Procesar venta:**
   - Clic en "COBRAR"
   - Seleccionar "Débito de saldo"
   - Confirmar
   - ✅ Venta exitosa
   - ✅ Ticket se abre automáticamente

7. **Verificar en admin:**
   - **Ventas:** Nueva venta con monto Gs. 49.500
   - **Promociones aplicadas:** Registro con descuento Gs. 5.500
   - **Auditoria:** Entrada con "VENTA_CON_RESTRICCIONES"
   - **Consumo tarjeta:** Saldo descontado

---

## 📊 Checklist de Validación

### SMTP
- [ ] `.env` configurado con credenciales
- [ ] Email de prueba enviado exitosamente
- [ ] Email recibido en bandeja de entrada

### Restricciones
- [ ] 10 alérgenos visibles en admin
- [ ] 3+ productos asociados a alérgenos
- [ ] Tarjeta con restricciones creada
- [ ] Bloqueo CRÍTICO funciona (no agrega producto)
- [ ] Advertencia MEDIO/ALTO funciona (pide confirmación)
- [ ] Auditoría se registra al confirmar restricción

### Promociones
- [ ] Promoción de ejemplo visible en admin
- [ ] Promoción NO aparece si no cumple condiciones
- [ ] Promoción APARECE si cumple condiciones
- [ ] Descuento se calcula correctamente
- [ ] Recálculo dinámico funciona al agregar/quitar items
- [ ] Registro en promociones_aplicadas después de venta

### Integración
- [ ] Flujo completo funciona sin errores
- [ ] UI responde correctamente
- [ ] Datos se guardan en todas las tablas
- [ ] No hay errores en consola del navegador
- [ ] No hay errores en logs de Django

---

## 🐛 Errores Comunes y Soluciones

### Error: "posAppInstance no está disponible"

**Causa:** Alpine.js no cargó correctamente

**Solución:**
1. Verificar que en `<html>` tag tiene: `x-data="posApp()"`
2. Verificar en DevTools → Console que no hay errores de JS
3. Recargar página con Ctrl+F5 (hard refresh)

### Error: "Promoción no aparece"

**Soluciones:**
1. Verificar en admin que está **Activa: ✅**
2. Verificar **Fecha inicio** ≤ hoy ≤ **Fecha fin**
3. Verificar **Hora actual** está entre hora_inicio y hora_fin
4. Verificar `dias_semana` JSON incluye día actual (1=Lun, 7=Dom)
5. Verificar carrito cumple `monto_minimo` y `min_cantidad`

### Error: "CSRF token missing"

**Solución:**
```html
<!-- Verificar que existe en templates/base.html -->
{% csrf_token %}
```

### Error: "Fetch failed" al llamar API

**Solución:**
1. Verificar URL está registrada en `pos_urls.py`
2. Verificar servidor Django está corriendo
3. Verificar en Network tab del navegador la respuesta del server
4. Verificar logs de Django: `python manage.py runserver --noreload`

---

## ✅ Testing Completado

Si todos los tests pasan:

1. **Marcar como completo** en `IMPLEMENTACION_COMPLETA_FEATURES.md`
2. **Hacer commit** de todos los cambios
3. **Preparar deploy a producción:**
   - Configurar `.env` en servidor
   - Ejecutar SQL migration
   - Capacitar al personal
   - Monitorear primera semana

---

**🎉 ¡Excelente trabajo! El sistema está listo para producción.**

**Tiempo total de testing:** ~45 minutos  
**Próximo paso:** Implementar Pagos Mixtos (5h)

---

**Última actualización:** 2025-01-21 23:50
