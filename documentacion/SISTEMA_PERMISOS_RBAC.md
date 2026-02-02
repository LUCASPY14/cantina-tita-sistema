# Sistema de Control de Acceso Basado en Roles (RBAC)

## Roles Disponibles

1. **CAJERO** - Nivel 1
   - Acceso al punto de venta
   - Registro de ventas y consumos
   - Recargas de saldo
   
2. **GERENTE** - Nivel 2
   - Todo lo del cajero +
   - Acceso a reportes y dashboards
   - Gestión de inventario
   - Visualización de alertas y métricas

3. **ADMINISTRADOR** - Nivel 3
   - Todo lo del gerente +
   - Gestión de clientes y empleados
   - Configuración del sistema
   - Validación de pagos
   - Acceso a admin de Django

## Archivos Creados

### 1. `gestion/permisos.py`
Contiene decoradores y funciones para control de acceso:

```python
from gestion.permisos import (
    requiere_rol,
    requiere_rol_minimo,
    solo_administrador,
    solo_gerente_o_superior,
    acceso_cajero,
    ROL_CAJERO,
    ROL_GERENTE,
    ROL_ADMINISTRADOR
)
```

### 2. `gestion/context_processors.py`
Proporciona variables de contexto a todos los templates:

Variables disponibles:
- `usuario_rol`: Nombre del rol ('CAJERO', 'GERENTE', 'ADMINISTRADOR')
- `es_cajero`: Boolean
- `es_gerente`: Boolean
- `es_administrador`: Boolean
- `puede_ver_reportes`: Boolean (gerente o superior)
- `puede_administrar`: Boolean (solo administrador)

## Uso en Vistas

### Opción 1: Decorador específico por rol
```python
from gestion.permisos import requiere_rol, ROL_ADMINISTRADOR, ROL_GERENTE

@requiere_rol(ROL_ADMINISTRADOR)
def gestionar_empleados(request):
    # Solo administradores
    ...

@requiere_rol(ROL_GERENTE, ROL_ADMINISTRADOR)
def ver_reportes_financieros(request):
    # Gerentes y administradores
    ...
```

### Opción 2: Decorador por nivel jerárquico
```python
from gestion.permisos import requiere_rol_minimo, ROL_GERENTE

@requiere_rol_minimo(ROL_GERENTE)
def dashboard_metricas(request):
    # Gerentes y superiores (incluye ADMINISTRADOR)
    ...
```

### Opción 3: Decoradores shortcuts
```python
from gestion.permisos import solo_administrador, solo_gerente_o_superior, acceso_cajero

@solo_administrador
def configuracion_sistema(request):
    # Solo administradores
    ...

@solo_gerente_o_superior
def reportes_dashboard(request):
    # Gerentes y administradores
    ...

@acceso_cajero
def punto_de_venta(request):
    # Todos los empleados autenticados
    ...
```

## Uso en Templates

### Mostrar/ocultar elementos según rol

```django
{% if es_administrador %}
    <a href="{% url 'gestion:gestionar_empleados' %}">Gestionar Empleados</a>
{% endif %}

{% if puede_ver_reportes %}
    <li><a href="{% url 'gestion:dashboard' %}">Dashboard</a></li>
    <li><a href="{% url 'gestion:reportes' %}">Reportes</a></li>
{% endif %}

{% if es_cajero %}
    <p>Acceso limitado a punto de venta</p>
{% endif %}

<!-- Mostrar rol actual -->
<span class="badge">{{ usuario_rol }}</span>
```

### Menú condicional
```django
<ul>
    <li><a href="{% url 'pos:venta' %}">Punto de Venta</a></li>
    
    {% if puede_ver_reportes %}
        <li><a href="{% url 'pos:dashboard' %}">Dashboard</a></li>
        <li><a href="{% url 'pos:reportes' %}">Reportes</a></li>
    {% endif %}
    
    {% if puede_administrar %}
        <li class="menu-title">Administración</li>
        <li><a href="{% url 'pos:gestionar_clientes' %}">Clientes</a></li>
        <li><a href="{% url 'pos:gestionar_empleados' %}">Empleados</a></li>
    {% endif %}
</ul>
```

## Vistas que Deben Restringirse

### Solo Administrador
- Gestión de empleados
- Configuración del sistema
- Validación de pagos (admin)
- Acceso a logs de auditoría
- Gestión de roles y permisos

### Gerente o Superior
- Dashboards y reportes
- Gestión de inventario
- Alertas del sistema
- Reportes financieros
- Historial de ventas detallado

### Cajero (Todos)
- Punto de venta
- POS Almuerzo
- Recargas de saldo
- Búsqueda de clientes básica

## Ejemplo Completo

```python
# En gestion/views.py

from django.shortcuts import render
from gestion.permisos import solo_administrador, solo_gerente_o_superior, acceso_cajero

@acceso_cajero
def punto_venta(request):
    \"\"\"Todos los empleados pueden acceder\"\"\"
    return render(request, 'gestion/pos.html')

@solo_gerente_o_superior
def dashboard_view(request):
    \"\"\"Solo gerentes y administradores\"\"\"
    # Obtener métricas...
    return render(request, 'gestion/dashboard.html', context)

@solo_administrador
def gestionar_empleados(request):
    \"\"\"Solo administradores\"\"\"
    empleados = Empleado.objects.all()
    return render(request, 'gestion/empleados.html', {'empleados': empleados})
```

## Verificación Manual de Permisos

Si necesitas verificar permisos manualmente dentro de una vista:

```python
from gestion.permisos import obtener_rol_empleado, tiene_permiso, ROL_ADMINISTRADOR

def mi_vista_compleja(request):
    rol = obtener_rol_empleado(request.user)
    
    if rol == ROL_ADMINISTRADOR:
        # Lógica para administradores
        datos_completos = obtener_datos_admin()
    else:
        # Lógica para otros roles
        datos_limitados = obtener_datos_basicos()
    
    return render(request, 'template.html', context)
```

## Próximos Pasos

1. Aplicar decoradores a todas las vistas de reportes
2. Aplicar decoradores a vistas de gestión de clientes/empleados
3. Actualizar templates para mostrar menús según permisos
4. Aplicar restricciones en pagos_admin_views.py
5. Aplicar restricciones en facturacion_views.py
6. Testear acceso con usuarios de cada rol

## Notas Importantes

- Los superusuarios de Django tienen acceso total automáticamente
- El rol 'SISTEMA' es interno, no se debe asignar a empleados reales
- Los decoradores ya incluyen `@login_required`, no es necesario duplicarlo
- Si un usuario no tiene rol asignado, será redirigido con mensaje de error
