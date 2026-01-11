"""
Vistas para gestión de empleados (cambio de contraseña, perfil, etc.)
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
import bcrypt

from .models import Empleado
from .permisos import acceso_cajero
from .seguridad_utils import registrar_auditoria


@acceso_cajero
def cambiar_contrasena_empleado(request):
    """
    Vista para que los empleados cambien su propia contraseña
    Acceso: Todos los empleados autenticados
    """
    try:
        empleado = Empleado.objects.get(usuario=request.user.username, activo=True)
    except Empleado.DoesNotExist:
        messages.error(request, 'Empleado no encontrado')
        return redirect('gestion:dashboard')
    
    if request.method == 'POST':
        password_actual = request.POST.get('password_actual', '')
        password_nueva = request.POST.get('password_nueva', '')
        password_confirmar = request.POST.get('password_confirmar', '')
        
        # Validaciones
        if not password_actual or not password_nueva or not password_confirmar:
            messages.error(request, 'Todos los campos son obligatorios')
            return redirect('gestion:cambiar_contrasena_empleado')
        
        # Verificar contraseña actual
        try:
            if not bcrypt.checkpw(password_actual.encode('utf-8'), empleado.contrasena_hash.encode('utf-8')):
                messages.error(request, 'La contraseña actual es incorrecta')
                return redirect('gestion:cambiar_contrasena_empleado')
        except Exception as e:
            messages.error(request, f'Error al verificar contraseña: {str(e)}')
            return redirect('gestion:cambiar_contrasena_empleado')
        
        # Verificar que las nuevas coincidan
        if password_nueva != password_confirmar:
            messages.error(request, 'Las contraseñas nuevas no coinciden')
            return redirect('gestion:cambiar_contrasena_empleado')
        
        # Validar longitud
        if len(password_nueva) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres')
            return redirect('gestion:cambiar_contrasena_empleado')
        
        # Actualizar contraseña
        try:
            with transaction.atomic():
                nuevo_hash = bcrypt.hashpw(password_nueva.encode('utf-8'), bcrypt.gensalt())
                empleado.contrasena_hash = nuevo_hash.decode('utf-8')
                empleado.save(update_fields=['contrasena_hash'])
                
                # Auditoría
                registrar_auditoria(
                    request=request,
                    operacion='CAMBIO_CONTRASENA_EMPLEADO',
                    tipo_usuario='EMPLEADO',
                    descripcion=f'Empleado {empleado.usuario} cambió su contraseña'
                )
                
                messages.success(request, '✓ Contraseña actualizada exitosamente')
                return redirect('gestion:dashboard')
                
        except Exception as e:
            messages.error(request, f'Error al actualizar contraseña: {str(e)}')
            return redirect('gestion:cambiar_contrasena_empleado')
    
    context = {
        'empleado': empleado,
    }
    
    return render(request, 'gestion/cambiar_contrasena_empleado.html', context)


@acceso_cajero
def perfil_empleado(request):
    """
    Vista para ver/editar perfil del empleado
    Acceso: Todos los empleados autenticados
    """
    try:
        empleado = Empleado.objects.select_related('id_rol').get(
            usuario=request.user.username,
            activo=True
        )
    except Empleado.DoesNotExist:
        messages.error(request, 'Empleado no encontrado')
        return redirect('gestion:dashboard')
    
    if request.method == 'POST':
        # Permitir editar email, teléfono, dirección
        empleado.email = request.POST.get('email', empleado.email)
        empleado.telefono = request.POST.get('telefono', empleado.telefono)
        empleado.direccion = request.POST.get('direccion', empleado.direccion)
        empleado.save()
        
        messages.success(request, '✓ Perfil actualizado exitosamente')
        return redirect('gestion:perfil_empleado')
    
    context = {
        'empleado': empleado,
    }
    
    return render(request, 'gestion/perfil_empleado.html', context)
