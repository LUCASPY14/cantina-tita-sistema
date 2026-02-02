# 📊 GUÍA DE USO - DASHBOARD POS PARA MONITOREO

## 🚀 Acceso Rápido

**URL:** `http://localhost:8000/pos/dashboard/`

O desde el POS principal:
1. Ingresa a POS: `http://localhost:8000/pos/`
2. Haz clic en botón "📊 Dashboard"

---

## 📈 Componentes Principales

### 1️⃣ **Tarjetas de Estadísticas** (Parte Superior)

Muestran en tiempo real:

```
┌──────────────────────────────────────────────────────────────┐
│ Total de Ventas    │    Monto Total      │  Promedio/Venta   │
│     45 txns        │   ₲1,250,000       │    ₲27,777        │
└──────────────────────────────────────────────────────────────┘
```

**Interpretación:**
- **Total de Ventas:** Cantidad de transacciones registradas hoy
- **Monto Total:** Ingresos brutos acumulados
- **Promedio:** Monto promedio por ticket (útil para análisis de AOV)

---

### 2️⃣ **Gráfica de Evolución por Hora**

📈 Línea dual que muestra:
- **Eje izquierdo (azul):** Cantidad de ventas por hora
- **Eje derecho (verde):** Monto en pesos por hora

**Cómo usarla:**
- Identifica horas pico (mayor actividad)
- Planifica staffing según demanda
- Detecta anomalías en ventas

**Ejemplo:**
```
10:00-11:00 → 3 ventas, ₲75,000
11:00-12:00 → 7 ventas, ₲195,000  ← PICO
12:00-13:00 → 5 ventas, ₲120,000
```

---

### 3️⃣ **Gráfica de Métodos de Pago** (Pastel)

Muestra distribución de ingresos:

```
Efectivo (48%) ████████░░ ₲600,000
Débito (28%)   ████░░░░░░ ₲350,000
Crédito (16%)  ██░░░░░░░░ ₲200,000
Tarjeta Est. (8%) █░░░░░░░░░ ₲100,000
```

**Análisis:**
- Efectivo = Dinero inmediato (mejor para flujo)
- Débito = Confirmación rápida
- Crédito = Riesgo de devolución
- Tarjeta Est. = Control de saldo

---

### 4️⃣ **Top 10 Productos Vendidos**

| Producto | Cantidad | Ingresos |
|----------|----------|----------|
| Agua Mineral 1L | 45 | ₲225,000 |
| Arepa de Queso | 32 | ₲160,000 |
| Sándwich | 28 | ₲140,000 |
| Gaseosa 2L | 25 | ₲125,000 |

**Uso:**
- Identifica productos estrella
- Reordena inventario según demanda
- Detecta productos con baja venta

---

### 5️⃣ **Desglose por Método de Pago**

| Método | Transacciones | Monto |
|--------|---------------|----|
| Efectivo | 30 | ₲600,000 |
| Débito | 12 | ₲350,000 |
| Crédito | 2 | ₲200,000 |

**Acción:** Verificar que los montos coincidan con caja diaria

---

### 6️⃣ **Top 5 Clientes**

| Cliente | Compras | Monto Total |
|---------|---------|------------|
| María López | 5 | ₲250,000 |
| Juan García | 4 | ₲180,000 |

---

## 🔄 Auto-Actualización

El dashboard **se refresca automáticamente cada 5 minutos**.

Para actualizar manualmente:
- Haz clic en botón **"🔄 Actualizar"** (arriba)
- O presiona: `F5` o `Ctrl+Shift+R`

---

## 📊 Análisis e Interpretación

### Ventas Altas
```
✅ POSITIVO:
   • Buena demanda de productos
   • Ingresos saludables
   • Caja activa

📋 ACCIONES:
   • Verificar stock de top productos
   • Asegurar que hay cajeros suficientes
   • Registrar en cuaderno de operaciones
```

### Ventas Bajas
```
⚠️  POSIBLES CAUSAS:
   • Día festivo o no lectivo
   • Problema en POS o caja
   • Falta de productos populares
   • Restricciones (ej: COVID)

📋 ACCIONES:
   • Revisar logs del sistema
   • Verificar stock disponible
   • Hablar con cajeros
```

### Desequilibrio Métodos de Pago
```
⚠️  ALERTA: Si efectivo es <30%:
   • Puede indicar problemas con cambio
   • O preferencia por plástico

⚠️  ALERTA: Si crédito es muy alto:
   • Riesgo de devoluciones
   • Verificar que están aprobadas
```

---

## 💡 Tips de Monitoreo

### 📅 Diariamente
1. **Mañana (8:00 AM):**
   - Revisar dashboard del día anterior
   - Comparar con promedio semanal
   
2. **Tarde (5:00 PM):**
   - Ver evolución hasta ese momento
   - Alertar si algo anómalo

3. **Noche (9:00 PM):**
   - Resumen diario final
   - Comparar con presupuesto/meta

### 📈 Semanalmente
- Comparar lunes vs. viernes
- Ver tendencias de productos
- Analizar métodos de pago

### 📊 Mensualmente
- Tendencia completa del mes
- Productos de mayor rotación
- Horas pico por día

---

## 🔧 Funcionalidades Avanzadas

### Exportar Datos
Si necesitas exportar datos para análisis:

```bash
# Descargar dashboard como JSON (AJAX)
curl -H "X-Requested-With: XMLHttpRequest" \
  http://localhost:8000/pos/dashboard/
```

### Integración con Excel/Sheets

Copiar tabla de productos y pegar en Excel:
1. Haz clic en tabla de productos
2. `Ctrl+A` para seleccionar
3. `Ctrl+C` para copiar
4. Pega en Excel/Google Sheets

### Imprimir Reporte
`Ctrl+P` o clic derecho → Imprimir

Configurar:
- Márgenes: Mínimos
- Orientación: Horizontal
- Escala: 80%

---

## ⚠️ Alertas Automáticas

El sistema muestra alertas si:

1. **Restricciones Bloqueadas:**
   - Si nota muchas ventas con advertencia de restricción
   - Revisar productos más conflictivos

2. **Stock Bajo:**
   - Si Top 10 muestra productos con poco stock
   - Reordenar inmediatamente

3. **Problemas de Método de Pago:**
   - Si un método tiene 0 transacciones (posible falla técnica)
   - Revisar máquina de tarjetas

---

## 📲 Acceso Móvil

El dashboard es responsive y funciona en **tablets y teléfonos:**

```
URL: http://[IP_DEL_SERVIDOR]:8000/pos/dashboard/

Desde tablet en caja:
1. Abre navegador
2. Ve a URL anterior
3. Marca como favorito
4. Pantalla completa (F11)
```

**Ideal para:** Monitoreo en tiempo real durante el día

---

## 🔐 Seguridad

- Dashboard requiere **login** (acceso autenticado)
- Solo usuarios autorizados pueden ver datos
- Los datos son en **tiempo real** desde BD
- Se recarga cada 5 min automáticamente

---

## 📞 Solución de Problemas

### "Dashboard no carga"
```
1. Verifica que Django está corriendo:
   python manage.py runserver 0.0.0.0:8000

2. Revisa la URL:
   http://localhost:8000/pos/dashboard/
```

### "Datos desactualizados"
```
1. Actualiza manualmente: F5 o botón 🔄
2. Espera 5 minutos para auto-refresh
3. Verifica que no hay errores en consola (F12)
```

### "Gráficas no muestran"
```
1. Abre consola: F12 → Console
2. Busca errores de Chart.js
3. Verifica que Chart.js CDN está disponible
```

---

## 📝 Checklist Diario

```
☐ 8:00 AM  - Revisar resumen del día anterior
☐ 12:00 PM - Verificar ventas de la mañana
☐ 5:00 PM  - Ver estado actual
☐ 9:00 PM  - Resumen completo del día
☐ Anotar: Máximo 3 observaciones importante

Observaciones (ejemplo):
├─ Baja venta de "X" producto (revisar con compras)
├─ Alto uso de crédito (verificar aprobaciones)
└─ Pico a las 11:00 AM (necesitar más cajeros)
```

---

## 🎯 Próximas Mejoras

Funcionalidades planificadas:
- ✅ Gráficas por hora
- ✅ Top productos
- ⏳ Exportación a Excel
- ⏳ Alertas por email
- ⏳ Comparación con período anterior
- ⏳ Análisis predictivo

---

**Última actualización:** Enero 9, 2025
**Versión:** 1.0
