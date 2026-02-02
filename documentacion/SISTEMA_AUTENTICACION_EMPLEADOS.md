# Sistema de Autenticación de Empleados - Completado

## ✅ Problema Resuelto

**Error original**: "Usuario o contraseña incorrectos" al intentar login con IDA_CAJA/IDA_CAJA

**Causa**: Django estaba usando solo el modelo User estándar, pero los empleados están en la tabla `empleados` con contraseñas hasheadas con bcrypt.

## 🔧 Solución Implementada

### 1. Backend de Autenticación Personalizado

Archivo: `gestion/backends.py`

```python
class EmpleadoBackend(BaseBackend):
    """
    Backend que autentica empleados contra la tabla empleados
    usando bcrypt para verificar contraseñas.
    """
```

**Características**:
- ✅ Valida usuario y contraseña contra tabla `empleados`
- ✅ Verifica contraseñas con bcrypt
- ✅ Solo permite login a empleados activos
- ✅ Crea automáticamente un User de Django al primer login exitoso
- ✅ Sincroniza permisos según rol:
  - **CAJERO** (id_rol=1): `is_staff=False, is_superuser=False`
  - **GERENTE** (id_rol=2): `is_staff=True, is_superuser=False`
  - **ADMINISTRADOR** (id_rol=3): `is_staff=True, is_superuser=True`

### 2. Configuración en settings.py

```python
AUTHENTICATION_BACKENDS = [
    'gestion.backends.EmpleadoBackend',  # Backend personalizado para empleados
    'django.contrib.auth.backends.ModelBackend',  # Backend por defecto de Django
]
```

El orden es importante:
1. Primero intenta autenticar como empleado
2. Si falla, intenta con usuarios Django normales (superusuarios creados con `createsuperuser`)

### 3. Script de Gestión de Contraseñas

Archivo: `establecer_contrasenas.py`

- Verifica qué empleados tienen contraseña establecida
- Establece contraseñas faltantes usando el usuario como contraseña por defecto
- Útil para inicialización o reseteo de contraseñas

## 📋 Empleados Configurados

Todos con formato: **usuario=contraseña**

| Usuario | Contraseña | Rol | Permisos Django |
|---------|------------|-----|-----------------|
| IDA_CAJA | IDA_CAJA | CAJERO (1) | staff=No, super=No |
| TITA | TITA | GERENTE (2) | staff=Sí, super=No |
| TITA2 | TITA2 | ADMINISTRADOR (3) | staff=Sí, super=Sí |
| CAR_PRUEB | CAR_PRUEB | CAJERO (1) | staff=No, super=No |

## 🔒 Seguridad

1. **Bcrypt**: Todas las contraseñas se almacenan hasheadas con bcrypt (factor 12)
2. **Validación**: Solo empleados con `activo=True` pueden autenticarse
3. **Sincronización**: Los permisos Django se actualizan en cada login
4. **Sin contraseñas en código**: Las contraseñas nunca se almacenan en texto plano

## 🧪 Pruebas

Script de prueba: `probar_autenticacion.py`

Resultados:
```
✅ IDA_CAJA + IDA_CAJA → Autenticación exitosa (CAJERO)
✅ TITA + TITA → Autenticación exitosa (GERENTE)
❌ IDA_CAJA + contraseña_incorrecta → Autenticación fallida
```

## 🚀 Cómo Usar

### Login Web
1. Ir a http://localhost:8000/login/
2. Usuario: `IDA_CAJA` (o cualquier usuario de empleado)
3. Contraseña: `IDA_CAJA` (o la contraseña del empleado)

### Cambiar Contraseña
- **Desde Django Admin**: http://localhost:8000/admin/gestion/empleado/
- **Auto-servicio**: http://localhost:8000/reportes/empleado/cambiar-contrasena/

### Crear Nuevo Empleado con Contraseña
```python
import bcrypt
from gestion.models import Empleado, TipoRolGeneral

# Hashear contraseña
password = "mi_contraseña"
password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Crear empleado
empleado = Empleado.objects.create(
    id_rol=TipoRolGeneral.objects.get(pk=1),  # CAJERO
    nombre="Juan",
    apellido="Pérez",
    usuario="JUAN_P",
    contrasena_hash=password_hash,
    email="juan@example.com",
    activo=True
)
```

### Resetear Contraseña de Empleado
```python
import bcrypt
from gestion.models import Empleado

empleado = Empleado.objects.get(usuario='IDA_CAJA')
nueva_password = "nueva_contraseña"
empleado.contrasena_hash = bcrypt.hashpw(
    nueva_password.encode('utf-8'), 
    bcrypt.gensalt()
).decode('utf-8')
empleado.save()
```

## 📝 Notas Importantes

1. **Al primer login**: Se crea automáticamente un User de Django para el empleado
2. **Sincronización**: Los datos se sincronizan en cada login (nombre, email, permisos)
3. **Desactivar empleado**: Poner `activo=False` en la tabla empleados impide el login
4. **Cambio de rol**: Al cambiar el rol en la tabla empleados, los permisos Django se actualizan en el siguiente login

## 🔄 Próximos Pasos

1. ✅ Reiniciar el servidor Django para cargar el nuevo backend
2. ✅ Probar login web con IDA_CAJA/IDA_CAJA
3. ✅ Probar login web con TITA/TITA (gerente)
4. ✅ Verificar acceso a funciones según rol
5. ⏳ Implementar cambio de contraseña obligatorio en primer login (opcional)
6. ⏳ Agregar política de expiración de contraseñas (opcional)
