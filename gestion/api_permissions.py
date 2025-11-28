"""
Permisos personalizados para la API REST
Control de acceso basado en roles de empleados
"""

from rest_framework import permissions


class IsAdministrador(permissions.BasePermission):
    """
    Permiso: Solo administradores
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Verificar si es superusuario de Django
        if request.user.is_superuser:
            return True
        
        # Verificar rol en modelo Empleado
        try:
            from .models import Empleado
            empleado = Empleado.objects.get(usuario=request.user.username)
            return empleado.id_rol and 'ADMIN' in empleado.id_rol.nombre_rol.upper()
        except:
            return False


class IsGerente(permissions.BasePermission):
    """
    Permiso: Gerentes y Administradores
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        try:
            from .models import Empleado
            empleado = Empleado.objects.get(usuario=request.user.username)
            if empleado.id_rol:
                rol = empleado.id_rol.nombre_rol.upper()
                return 'ADMIN' in rol or 'GERENTE' in rol
        except:
            return False
        
        return False


class IsCajero(permissions.BasePermission):
    """
    Permiso: Cajeros, Gerentes y Administradores
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        try:
            from .models import Empleado
            empleado = Empleado.objects.get(usuario=request.user.username)
            if empleado.id_rol:
                rol = empleado.id_rol.nombre_rol.upper()
                return 'ADMIN' in rol or 'GERENTE' in rol or 'CAJERO' in rol
        except:
            return False
        
        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso: El propietario puede editar, otros solo leer
    """
    def has_object_permission(self, request, view, obj):
        # Lectura permitida para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura solo para el propietario
        return obj.usuario == request.user.username


class ReadOnlyOrAuthenticated(permissions.BasePermission):
    """
    Permiso: Lectura para todos, escritura solo autenticados
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated


class CanManageVentas(permissions.BasePermission):
    """
    Permiso: Puede gestionar ventas (Cajeros+)
    """
    def has_permission(self, request, view):
        # GET permitido para todos los autenticados
        if request.method == 'GET':
            return request.user.is_authenticated
        
        # POST, PUT, DELETE requieren ser cajero o superior
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        try:
            from .models import Empleado
            empleado = Empleado.objects.get(usuario=request.user.username)
            if empleado.id_rol:
                rol = empleado.id_rol.nombre_rol.upper()
                return 'ADMIN' in rol or 'GERENTE' in rol or 'CAJERO' in rol
        except:
            return False
        
        return False


class CanManageStock(permissions.BasePermission):
    """
    Permiso: Puede gestionar stock (Gerentes+)
    """
    def has_permission(self, request, view):
        # GET permitido para todos los autenticados
        if request.method == 'GET':
            return request.user.is_authenticated
        
        # Modificaciones requieren ser gerente o admin
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        try:
            from .models import Empleado
            empleado = Empleado.objects.get(usuario=request.user.username)
            if empleado.id_rol:
                rol = empleado.id_rol.nombre_rol.upper()
                return 'ADMIN' in rol or 'GERENTE' in rol
        except:
            return False
        
        return False


class CanManageEmpleados(permissions.BasePermission):
    """
    Permiso: Puede gestionar empleados (Solo Admin)
    """
    def has_permission(self, request, view):
        # GET permitido para gerentes y admin
        if request.method == 'GET':
            if request.user.is_superuser:
                return True
            
            try:
                from .models import Empleado
                empleado = Empleado.objects.get(usuario=request.user.username)
                if empleado.id_rol:
                    rol = empleado.id_rol.nombre_rol.upper()
                    return 'ADMIN' in rol or 'GERENTE' in rol
            except:
                return False
        
        # Modificaciones solo admin
        return IsAdministrador().has_permission(request, view)
