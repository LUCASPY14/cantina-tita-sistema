# Configuración Regional para Paraguay

Este sistema está configurado para funcionar en Paraguay con las siguientes características:

## 🇵🇾 Configuración Regional

### Zona Horaria
- **Zona horaria:** America/Asuncion (GMT-3/GMT-4)
- **Horario de verano:** Se ajusta automáticamente según el calendario paraguayo

### Idioma
- **Código de idioma:** es-py (Español de Paraguay)
- **Formato de fecha:** DD/MM/AAAA (25/11/2025)
- **Formato de hora:** 24 horas (14:30)

### Formatos Numéricos
- **Separador de miles:** punto (.)
- **Separador decimal:** coma (,)
- **Ejemplo:** 1.234.567,89

## 💰 Moneda: Guaraníes (PYG)

### Formato de Moneda
```python
# En código Python
from gestion.utils_moneda import formatear_guaranies

monto = 1500000
print(formatear_guaranies(monto))  # Output: Gs. 1.500.000
```

### En Templates Django
```django
{% load paraguay_filters %}

<!-- Formato estándar -->
{{ monto|guaranies }}  {# Output: Gs. 1.500.000 #}

<!-- Formato corto -->
{{ monto|guaranies_corto }}  {# Output: Gs. 1.5M #}
```

### Características de los Guaraníes
- **Símbolo:** Gs. o ₲
- **Código ISO:** PYG
- **Subdivisions:** No tiene (moneda entera, sin centavos)
- **Billetes:** 2.000, 5.000, 10.000, 20.000, 50.000, 100.000
- **Monedas:** 50, 100, 500, 1.000 Gs.

## 🧾 Impuestos en Paraguay

### IVA (Impuesto al Valor Agregado)
```python
from gestion.utils_moneda import calcular_iva, extraer_iva

# Calcular IVA 10%
monto_base = 100000
monto_con_iva, iva = calcular_iva(monto_base, tasa='10')
# monto_con_iva = 110000, iva = 10000

# Calcular IVA 5%
monto_con_iva, iva = calcular_iva(monto_base, tasa='5')
# monto_con_iva = 105000, iva = 5000

# Extraer IVA de un monto total
monto_total = 110000
monto_sin_iva, iva = extraer_iva(monto_total, tasa='10')
# monto_sin_iva = 100000, iva = 10000
```

### Tasas de IVA
- **IVA 10%:** Tasa general (la mayoría de productos)
- **IVA 5%:** Tasa reducida (productos básicos)
- **Exento:** Sin IVA (algunos servicios y productos)

## 📄 Documentos de Identidad

### RUC (Registro Único de Contribuyentes)
```django
{% load paraguay_filters %}

{{ ruc|ruc_format }}  {# Output: 12345678-9 #}
```

**Formato:**
- Personas físicas: 8 dígitos + 1 verificador (12345678-9)
- Personas jurídicas: 7 dígitos + 1 verificador (1234567-8)

### Cédula de Identidad
```django
{% load paraguay_filters %}

{{ cedula|ci_format }}  {# Output: 1.234.567 #}
```

**Formato:** Con puntos como separadores de miles

## 📞 Teléfonos

### Formato de Teléfonos Paraguayos
```django
{% load paraguay_filters %}

<!-- Celular -->
{{ "0981123456"|telefono_py }}  {# Output: 0981 123 456 #}

<!-- Fijo -->
{{ "021123456"|telefono_py }}  {# Output: (021) 123-456 #}
```

### Códigos de Área Principales
- **021** - Asunción
- **0961, 0971, 0981, 0982, 0983, 0984, 0985, 0986, 0991, 0992, 0994, 0995** - Celulares

## 📅 Fechas

### Formato de Fechas
```django
{% load paraguay_filters %}

<!-- Fecha -->
{% fecha_py fecha_objeto %}  {# Output: 25/11/2025 #}

<!-- Fecha y hora -->
{% fecha_hora_py datetime_objeto %}  {# Output: 25/11/2025 14:30 #}
```

### Formatos Aceptados en Formularios
- DD/MM/AAAA (25/11/2025)
- DD/MM/AA (25/11/25)
- DD-MM-AAAA (25-11-2025)
- AAAA-MM-DD (2025-11-25) - ISO

### Días de la Semana
- **Primera día:** Lunes
- **Nombres:** Lunes, Martes, Miércoles, Jueves, Viernes, Sábado, Domingo

### Meses del Año
- Enero, Febrero, Marzo, Abril, Mayo, Junio
- Julio, Agosto, Septiembre, Octubre, Noviembre, Diciembre

## 🏫 Contexto del Sistema: Cantina Escolar

### Características Específicas para Paraguay

#### Sistema de Tarjetas Recargables
- Tarjetas para estudiantes con saldo en Guaraníes
- Alertas de saldo bajo (configurable por estudiante)
- Recarga de saldo via efectivo, transferencia o tarjeta de débito/crédito

#### Planes de Almuerzo
- Suscripciones mensuales para almuerzo escolar
- Control de asistencia diaria
- Pago mensual anticipado en Guaraníes

#### Tipos de Cliente
- **Estudiante:** Precios preferenciales
- **Profesor:** Descuentos especiales
- **Personal:** Precios diferenciados
- **Externo:** Precio regular

#### Medios de Pago Comunes
- **Efectivo** (Gs.)
- **Tarjeta de débito** (con comisión)
- **Tarjeta de crédito** (con comisión)
- **Transferencia bancaria**
- **Billetera móvil** (Zimple, Tigo Money, Personal Pay)

## 📊 Ejemplos de Uso

### Template de Venta
```django
{% load paraguay_filters %}

<div class="venta">
    <h3>Venta #{{ venta.numero_venta }}</h3>
    <p>Fecha: {% fecha_hora_py venta.fecha %}</p>
    <p>Cliente: {{ venta.cliente.nombres }} {{ venta.cliente.apellidos }}</p>
    <p>RUC/CI: {{ venta.cliente.ruc_ci|ci_format }}</p>
    
    <table>
        {% for detalle in venta.detalles.all %}
        <tr>
            <td>{{ detalle.producto.descripcion }}</td>
            <td>{{ detalle.cantidad }}</td>
            <td>{{ detalle.precio_unitario|guaranies }}</td>
            <td>{{ detalle.subtotal|guaranies }}</td>
        </tr>
        {% endfor %}
    </table>
    
    <p class="total">Total: {{ venta.monto_total|guaranies }}</p>
</div>
```

### Lista de Productos
```django
{% load paraguay_filters %}

{% for producto in productos %}
<div class="producto">
    <h4>{{ producto.descripcion }}</h4>
    <p>Código: {{ producto.codigo }}</p>
    <p>Stock: {{ producto.stock.stock_actual }}</p>
    <p class="precio">{{ producto.precio_unitario|guaranies }}</p>
    <small>(IVA {{ producto.id_impuesto.porcentaje }}% incluido)</small>
</div>
{% endfor %}
```

### Resumen de Caja
```python
from gestion.utils_moneda import formatear_guaranies

total_efectivo = 1250000
total_tarjetas = 850000
total_dia = total_efectivo + total_tarjetas

print(f"Efectivo: {formatear_guaranies(total_efectivo)}")
print(f"Tarjetas: {formatear_guaranies(total_tarjetas)}")
print(f"Total: {formatear_guaranies(total_dia)}")
```

## 🔧 Configuración Adicional

### Variables de Entorno (.env)
```
# Ya configurado en el sistema
LANGUAGE_CODE=es-py
TIME_ZONE=America/Asuncion
```

### Settings.py
```python
# Configuración regional para Paraguay
LANGUAGE_CODE = 'es-py'
TIME_ZONE = 'America/Asuncion'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Formatos de fecha
DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i'

# Formatos de número
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = '.'
DECIMAL_SEPARATOR = ','
```

## 📚 Referencias

### Enlaces Útiles
- **SET (Subsecretaría de Estado de Tributación):** https://www.set.gov.py
- **Banco Central del Paraguay:** https://www.bcp.gov.py
- **Código de trabajo:** Ley N° 213/93

### Datos de Referencia 2025
- **Salario mínimo:** Gs. 2.680.373 (verificar valor actual)
- **IVA:** 10% (tasa general) / 5% (tasa reducida)
- **Año fiscal:** Enero - Diciembre

---

**Sistema configurado para Paraguay 🇵🇾**
