"""
Sistema de control de acceso basado en roles (RBAC)
Decoradores y utilidades para gestionar permisos por rol
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Constantes de roles
ROL_CAJERO = 'CAJERO'
ROL_GERENTE = 'GERENTE'
ROL_ADMINISTRADOR = 'ADMINISTRADOR'
ROL_SISTEMA = 'SISTEMA'

# Jerarquía de roles (de menor a mayor privilegio)
JERARQUIA_ROLES = {
    ROL_CAJERO: 1,
    ROL_GERENTE: 2,
    ROL_ADMINISTRADOR: 3,
    ROL_SISTEMA: 4
}


def obtener_rol_empleado(user):
    """Obtiene el rol del empleado autenticado"""
    try:
        from gestion.models import Empleado
        empleado = Empleado.objects.select_related('id_rol').get(usuario=user.username, activo=True)
        return empleado.id_rol.nombre_rol
    except Empleado.DoesNotExist:
        return None


def tiene_permiso(user, roles_permitidos):
    """Verifica si el usuario tiene uno de los roles permitidos"""
    if not user.is_authenticated:
        return False
    
    # Superusuarios Django tienen acceso total
    if user.is_superuser:
        return True
    
    rol_usuario = obtener_rol_empleado(user)
    if not rol_usuario:
        return False
    
    # Verificar si el rol está en la lista de permitidos
    if isinstance(roles_permitidos, str):
        roles_permitidos = [roles_permitidos]
    
    return rol_usuario in roles_permitidos


def requiere_rol(*roles_permitidos):
    """
    Decorador para restringir acceso a vistas según rol
    
    Uso:
        @requiere_rol(ROL_ADMINISTRADOR)
        def vista_admin(request):
            ...
        
        @requiere_rol(ROL_GERENTE, ROL_ADMINISTRADOR)
        def vista_gerente_o_admin(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            if tiene_permiso(request.user, roles_permitidos):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, f'⛔ Acceso denegado. Se requiere rol: {", ".join(roles_permitidos)}')
                # Redirigir a POS dashboard para evitar bucle de redirecciones
                return redirect('pos:dashboard')
        return wrapped_view
    return decorator


def requiere_rol_minimo(rol_minimo):
    """
    Decorador que permite acceso al rol especificado y todos los superiores en jerarquía
    
    Uso:
        @requiere_rol_minimo(ROL_GERENTE)  # Permite GERENTE y ADMINISTRADOR
        def vista_gerentes(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            rol_usuario = obtener_rol_empleado(request.user)
            
            if not rol_usuario:
                messages.error(request, '⛔ Usuario sin rol asignado. Contacte al administrador.')
                # Redirigir a POS dashboard (accesible) en lugar de gestión (requiere gerente)
                return redirect('pos:dashboard')
            
            # Superusuarios siempre tienen acceso
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verificar jerarquía
            nivel_usuario = JERARQUIA_ROLES.get(rol_usuario, 0)
            nivel_minimo = JERARQUIA_ROLES.get(rol_minimo, 999)
            
            if nivel_usuario >= nivel_minimo:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, f'⛔ Acceso denegado. Se requiere rol mínimo: {rol_minimo}')
                # Redirigir a POS dashboard en lugar de gestión para evitar bucle
                return redirect('pos:dashboard')
        return wrapped_view
    return decorator


def solo_administrador(view_func):
    """Decorador shortcut para vistas solo de administradores"""
    return requiere_rol(ROL_ADMINISTRADOR)(view_func)


def solo_gerente_o_superior(view_func):
    """Decorador shortcut para gerentes y administradores"""
    return requiere_rol_minimo(ROL_GERENTE)(view_func)


def acceso_cajero(view_func):
    """Decorador shortcut para cualquier empleado autenticado (cajero incluido)"""
    return requiere_rol_minimo(ROL_CAJERO)(view_func)
