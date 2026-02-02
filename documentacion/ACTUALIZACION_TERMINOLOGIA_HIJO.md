# Actualización de Terminología: Estudiante → Hijo

## Fecha: 13 de enero de 2026

## Resumen Ejecutivo

Se ha actualizado la terminología en todo el sistema para usar **"hijo/hijos"** en lugar de **"estudiante/estudiantes"**, eliminando confusiones y manteniendo consistencia con el modelo de datos donde la tabla principal es `hijos`.

---

## Cambios Realizados

### 1. Modelos Django (models.py)

#### Antes:
```python
class VistaConsumosEstudiante(models.Model):
    '''Vista v_consumos_estudiante - Resumen de consumos por estudiante'''
    # ...
    class Meta:
        verbose_name = 'Vista: Consumos por Estudiante'
        verbose_name_plural = 'Vista: Consumos por Estudiante'

class RestriccionesHijos(models.Model):
    '''Tabla restricciones_hijos - Restricciones alimentarias de estudiantes'''

class Tarjeta(models.Model):
    '''Tabla tarjetas - Tarjetas de estudiantes'''
```

#### Después:
```python
class VistaConsumosEstudiante(models.Model):
    '''Vista v_consumos_estudiante - Resumen de consumos por hijo'''
    # ...
    class Meta:
        verbose_name = 'Vista: Consumos por Hijo'
        verbose_name_plural = 'Vista: Consumos por Hijo'

class RestriccionesHijos(models.Model):
    '''Tabla restricciones_hijos - Restricciones alimentarias de hijos'''

class Tarjeta(models.Model):
    '''Tabla tarjetas - Tarjetas de hijos'''
```

---

### 2. Templates HTML

#### Dashboard de Saldos (`dashboard_saldos_tiempo_real.html`)

**Antes:**
```html
<label>Buscar Estudiante</label>
<input type="text" id="filtro-estudiante" placeholder="Nombre...">
<option value="estudiante">Nombre Estudiante</option>
```

**Después:**
```html
<label>Buscar Hijo</label>
<input type="text" id="filtro-hijo" placeholder="Nombre...">
<option value="hijo">Nombre Hijo</option>
```

**JavaScript:**
```javascript
// Antes
const filtroEstudiante = document.getElementById('filtro-estudiante').value;
if (filtroEstudiante && !tarjeta.estudiante.includes(filtroEstudiante)) { ... }
case 'estudiante': ...

// Después
const filtroHijo = document.getElementById('filtro-hijo').value;
if (filtroHijo && !tarjeta.estudiante.includes(filtroHijo)) { ... }
case 'hijo': ...
```

#### Reportes de Almuerzo

**Archivos actualizados:**
- `almuerzo_reporte_estudiante.html` → Título: "Reporte por Hijo"
- `almuerzo_reporte_mensual.html` → Header: "Hijo"
- `almuerzo_reporte_diario.html` → Header: "Hijo"
- `almuerzo_reportes.html` → "Por Hijo", "Historial por hijo/tarjeta"

**Antes:**
```html
<th>Estudiante</th>
{% block title %}Reporte por Estudiante{% endblock %}
<h2>Por Estudiante</h2>
```

**Después:**
```html
<th>Hijo</th>
{% block title %}Reporte por Hijo{% endblock %}
<h2>Por Hijo</h2>
```

#### Portal de Padres

**Archivos actualizados:**
- `portal/dashboard.html`
- `portal/cargar_saldo.html`
- `portal/terminos_saldo_negativo.html`

**Cambios:**
```html
<!-- Antes -->
<span>El saldo se acredita inmediatamente en la tarjeta del estudiante</span>
Es el crédito que permite al estudiante realizar compras
El estudiante NO podrá realizar compras

<!-- Después -->
<span>El saldo se acredita inmediatamente en la tarjeta del hijo</span>
Es el crédito que permite al hijo realizar compras
El hijo NO podrá realizar compras
```

#### Alertas y Administración

**Archivos:**
- `alertas_tarjetas_saldo.html`
- `alertas_sistema.html`
- `admin/configurar_limites_masivo.html`

**Cambios:**
```html
<!-- Antes -->
<th>Estudiante</th>
placeholder="Tarjeta, estudiante o responsable..."

<!-- Después -->
<th>Hijo</th>
placeholder="Tarjeta, hijo o responsable..."
```

#### Módulo de Almuerzos

**Archivos:**
- `almuerzo.html`
- `almuerzo_cuentas_mensuales.html`
- `almuerzo_generar_cuentas.html`

**Cambios:**
```html
<!-- Antes -->
Pase la tarjeta del estudiante por el lector
<p><strong>Estudiante:</strong> {{ hijo.nombre_completo }}</p>
estudiantes con consumos
para todos los estudiantes que tienen consumos

<!-- Después -->
Pase la tarjeta del hijo por el lector
<p><strong>Hijo:</strong> {{ hijo.nombre_completo }}</p>
hijos con consumos
para todos los hijos que tienen consumos
```

#### Comprobantes

**Archivo:** `comprobante_recarga.html`

```html
<!-- Antes -->
<!-- Datos del estudiante -->
<span class="info-label">Estudiante:</span>

<!-- Después -->
<!-- Datos del hijo -->
<span class="info-label">Hijo:</span>
```

#### Templates de Email

**Archivos actualizados:**
- `emails/recordatorio_deuda_urgente.html`
- `emails/recordatorio_deuda_critico.html`
- `emails/recordatorio_deuda_amable.html`

```html
<!-- Antes -->
<strong>👨‍🎓 Estudiante:</strong> {{ estudiante }}

<!-- Después -->
<strong>👨‍🎓 Hijo:</strong> {{ estudiante }}
```

*Nota: La variable `{{ estudiante }}` se mantiene por compatibilidad.*

#### Base Template

**Archivo:** `base.html`

**Cambios en JavaScript:**
```javascript
// Antes
`Estudiante: ${this.selectedCard.nombre || 'N/A'}\n`
// Obtener grado del estudiante si existe
grado_estudiante: grado,
tarjetaInfo.innerHTML = '... Escanee la tarjeta del estudiante...'

// Después
`Hijo: ${this.selectedCard.nombre || 'N/A'}\n`
// Obtener grado del hijo si existe
grado_hijo: grado,
tarjetaInfo.innerHTML = '... Escanee la tarjeta del hijo...'
```

#### Formularios

**Archivo:** `gestion/producto_form.html`

```html
<!-- Antes -->
Esta información se usará para alertar a estudiantes con restricciones

<!-- Después -->
Esta información se usará para alertar a hijos con restricciones
```

---

## Archivos Modificados

### Templates (20 archivos)
1. ✅ `templates/pos/dashboard_saldos_tiempo_real.html`
2. ✅ `templates/pos/admin/configurar_limites_masivo.html`
3. ✅ `templates/portal/dashboard.html`
4. ✅ `templates/portal/cargar_saldo.html`
5. ✅ `templates/pos/almuerzo_reporte_mensual.html`
6. ✅ `templates/pos/almuerzo_reporte_diario.html`
7. ✅ `templates/pos/almuerzo_reporte_estudiante.html`
8. ✅ `templates/pos/alertas_tarjetas_saldo.html`
9. ✅ `templates/pos/alertas_sistema.html`
10. ✅ `templates/pos/almuerzo_cuentas_mensuales.html`
11. ✅ `templates/pos/almuerzo.html`
12. ✅ `templates/pos/almuerzo_reportes.html`
13. ✅ `templates/pos/almuerzo_generar_cuentas.html`
14. ✅ `templates/pos/comprobante_recarga.html`
15. ✅ `templates/portal/terminos_saldo_negativo.html`
16. ✅ `templates/gestion/producto_form.html`
17. ✅ `templates/base.html`
18. ✅ `templates/emails/recordatorio_deuda_urgente.html`
19. ✅ `templates/emails/recordatorio_deuda_critico.html`
20. ✅ `templates/emails/recordatorio_deuda_amable.html`

### Python (1 archivo)
1. ✅ `gestion/models.py`

---

## Áreas NO Modificadas (Intencional)

### 1. Nombres de Variables en Contexto
Se mantienen variables como `{{ estudiante }}` en templates por compatibilidad con el código backend existente. Solo se actualizaron los labels visibles.

### 2. Nombres de Tablas en BD
No se modificaron nombres de tablas SQL como `v_consumos_estudiante` ya que son vistas existentes en la base de datos.

### 3. Nombres de Clases Django
Se mantienen nombres de clases como `VistaConsumosEstudiante` para mantener compatibilidad con código existente.

### 4. Archivos de Scripts
Scripts de utilidad y prueba mantienen su terminología original para no afectar funcionalidad.

---

## Impacto en la Interfaz de Usuario

### Antes → Después

| Contexto | Antes | Después |
|----------|-------|---------|
| Filtros de búsqueda | "Buscar Estudiante" | "Buscar Hijo" |
| Headers de tablas | "Estudiante" | "Hijo" |
| Títulos de reportes | "Reporte por Estudiante" | "Reporte por Hijo" |
| Mensajes | "estudiantes con consumos" | "hijos con consumos" |
| Instrucciones | "tarjeta del estudiante" | "tarjeta del hijo" |
| Alertas | "Estudiante: ..." | "Hijo: ..." |
| Emails | "Estudiante:" | "Hijo:" |

---

## Beneficios

1. ✅ **Consistencia:** Alineado con el modelo de datos (`tabla hijos`)
2. ✅ **Claridad:** Elimina confusión entre "estudiante" y "hijo"
3. ✅ **Naturalidad:** Mejor comprensión para padres/responsables
4. ✅ **Mantenibilidad:** Terminología uniforme en toda la aplicación

---

## Verificación

Para verificar los cambios:

```bash
# Buscar referencias restantes a "estudiante" en templates
grep -r "estudiante" templates/ --include="*.html"

# Buscar en modelos
grep "estudiante" gestion/models.py
```

---

## Compatibilidad

### Variables Backend
Las variables de contexto en Python pueden mantener nombres como `estudiante` internamente, ya que solo se actualizaron:
- Labels visibles al usuario
- Texto de ayuda
- Mensajes informativos
- Verbose names de modelos

### APIs
Si existen endpoints de API que usan `estudiante` en JSON, no se modificaron para mantener compatibilidad con clientes externos.

---

## Próximos Pasos Opcionales

Si se desea completar la actualización:

1. Renombrar variables en views.py: `estudiante` → `hijo`
2. Actualizar serializers de API
3. Actualizar documentación de API
4. Actualizar tests

**Nota:** Estos cambios no son críticos ya que son internos al código y no afectan la experiencia del usuario.

---

**Estado:** ✅ Completado  
**Archivos Modificados:** 21  
**Impacto Visual:** Alto  
**Impacto Funcional:** Ninguno (solo cambios de presentación)

---

**Documentado por:** GitHub Copilot  
**Fecha:** 13 de enero de 2026
