"""
Context processors para agregar información global a todos los templates
"""
from gestion.permisos import obtener_rol_empleado, ROL_CAJERO, ROL_GERENTE, ROL_ADMINISTRADOR


def rol_usuario(request):
    """
    Agrega información del rol del usuario autenticado a todos los templates
    
    Variables disponibles en templates:
    - usuario_rol: nombre del rol ('CAJERO', 'GERENTE', 'ADMINISTRADOR', etc.)
    - es_cajero: Boolean
    - es_gerente: Boolean  
    - es_administrador: Boolean
    - puede_ver_reportes: Boolean (gerente o superior)
    - puede_administrar: Boolean (solo administrador)
    """
    context = {
        'usuario_rol': None,
        'es_cajero': False,
        'es_gerente': False,
        'es_administrador': False,
        'puede_ver_reportes': False,
        'puede_administrar': False,
    }
    
    if request.user.is_authenticated:
        # Superusuarios Django
        if request.user.is_superuser:
            context['usuario_rol'] = 'SUPERUSUARIO'
            context['es_administrador'] = True
            context['puede_ver_reportes'] = True
            context['puede_administrar'] = True
            return context
        
        # Empleados con rol asignado
        rol = obtener_rol_empleado(request.user)
        if rol:
            context['usuario_rol'] = rol
            context['es_cajero'] = rol == ROL_CAJERO
            context['es_gerente'] = rol == ROL_GERENTE
            context['es_administrador'] = rol == ROL_ADMINISTRADOR
            context['puede_ver_reportes'] = rol in [ROL_GERENTE, ROL_ADMINISTRADOR]
            context['puede_administrar'] = rol == ROL_ADMINISTRADOR
    
    return context
