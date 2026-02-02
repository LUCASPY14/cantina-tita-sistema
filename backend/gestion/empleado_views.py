"""
Vistas para gestión de empleados (cambio de contraseña, perfil, etc.)
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import bcrypt

from .models import Empleado, Cajas
from .permisos import acceso_cajero, solo_administrador
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
    from datetime import date
    from django.db.models import Count, Sum
    from .models import Ventas, AuditoriaWeb
    
    try:
        empleado = Empleado.objects.select_related('id_rol', 'id_caja').get(
            usuario=request.user.username,
            activo=True
        )
    except Empleado.DoesNotExist:
        messages.error(request, 'Empleado no encontrado')
        return redirect('dashboard_reportes')
    
    # Estadísticas del día si es cajero
    ventas_hoy = 0
    total_vendido_hoy = 0
    recargas_hoy = 0
    
    if empleado.id_rol.id_rol == 1:  # CAJERO
        hoy = date.today()
        ventas_hoy = Ventas.objects.filter(
            id_empleado_cajero=empleado,
            fecha=hoy
        ).count()
        
        total_vendido = Ventas.objects.filter(
            id_empleado_cajero=empleado,
            fecha=hoy
        ).aggregate(total=Sum('monto_total'))
        total_vendido_hoy = total_vendido['total'] or 0
        
        # Contar recargas del día (ventas de tipo RECARGA)
        recargas_hoy = Ventas.objects.filter(
            id_empleado_cajero=empleado,
            fecha=hoy,
            tipo_venta='RECARGA'
        ).count()
    
    # Últimos 5 logins del empleado
    ultimos_logins = AuditoriaWeb.objects.filter(
        usuario=request.user.username,
        accion__icontains='login'
    ).order_by('-fecha')[:5]
    
    context = {
        'empleado': empleado,
        'ventas_hoy': ventas_hoy,
        'total_vendido_hoy': total_vendido_hoy,
        'recargas_hoy': recargas_hoy,
        'ultimos_logins': ultimos_logins,
    }
    
    return render(request, 'gestion/perfil_empleado.html', context)


@solo_administrador
def gestionar_empleados_view(request):
    """
    Vista para listar y administrar empleados
    Acceso: Solo Administradores
    """
    from .models import Rol
    
    # Filtros
    buscar = request.GET.get('buscar', '')
    rol_filtro = request.GET.get('rol', '')
    activo_filtro = request.GET.get('activo', '')
    
    # Query base
    empleados = Empleado.objects.select_related('id_rol', 'id_caja').all()
    
    # Aplicar filtros
    if buscar:
        empleados = empleados.filter(nombre_usuario__icontains=buscar)
    
    if rol_filtro:
        empleados = empleados.filter(id_rol__id_rol=rol_filtro)
    
    if activo_filtro:
        empleados = empleados.filter(activo=(activo_filtro == '1'))
    
    # Ordenar por rol y nombre
    empleados = empleados.order_by('id_rol__id_rol', 'nombre_usuario')
    
    # Paginación
    paginator = Paginator(empleados, 20)
    page_number = request.GET.get('page', 1)
    empleados_page = paginator.get_page(page_number)
    
    # Obtener cajas para el modal
    cajas = Cajas.objects.filter(activo=True)
    
    context = {
        'empleados': empleados_page,
        'cajas': cajas,
    }
    
    return render(request, 'gestion/gestionar_empleados.html', context)


@solo_administrador
def crear_empleado_view(request):
    """
    Vista para crear un nuevo empleado
    Acceso: Solo Administradores
    """
    if request.method != 'POST':
        return redirect('gestionar_empleados')
    
    nombre_usuario = request.POST.get('nombre_usuario', '').strip()
    password = request.POST.get('password', '')
    password_confirm = request.POST.get('password_confirm', '')
    id_rol = request.POST.get('id_rol')
    id_caja = request.POST.get('id_caja')
    
    # Validaciones
    if not nombre_usuario or not password or not id_rol:
        messages.error(request, 'Todos los campos obligatorios deben completarse')
        return redirect('gestionar_empleados')
    
    if password != password_confirm:
        messages.error(request, 'Las contraseñas no coinciden')
        return redirect('gestionar_empleados')
    
    if Empleado.objects.filter(nombre_usuario=nombre_usuario).exists():
        messages.error(request, f'El usuario "{nombre_usuario}" ya existe')
        return redirect('gestionar_empleados')
    
    try:
        from .models import Rol
        
        # Hash de contraseña
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Crear empleado
        empleado = Empleado(
            nombre_usuario=nombre_usuario,
            contrasena_hash=password_hash,
            id_rol_id=id_rol,
            activo=True
        )
        
        if id_caja:
            empleado.id_caja_id = id_caja
        
        empleado.save()
        
        # Registrar auditoría
        registrar_auditoria(
            usuario=request.user.username,
            accion=f'Empleado creado: {nombre_usuario}',
            detalles=f'Rol: {empleado.id_rol.descripcion}',
            ip=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, f'✓ Empleado "{nombre_usuario}" creado exitosamente')
        
    except Exception as e:
        messages.error(request, f'Error al crear empleado: {str(e)}')
    
    return redirect('gestionar_empleados')


# ==================== ENDPOINTS AJAX PARA GESTIÓN DE EMPLEADOS ====================

@solo_administrador
@require_http_methods(['POST'])
def editar_empleado_ajax(request, empleado_id):
    """
    Endpoint AJAX para editar un empleado existente
    """
    try:
        empleado = Empleado.objects.get(id_empleado=empleado_id)
        
        # Obtener datos del request
        nombre_usuario = request.POST.get('nombre_usuario', '').strip()
        id_rol = request.POST.get('id_rol')
        id_caja = request.POST.get('id_caja')
        
        # Validaciones
        if not nombre_usuario or not id_rol:
            return JsonResponse({
                'success': False,
                'message': 'Nombre de usuario y rol son obligatorios'
            }, status=400)
        
        # Verificar si el nombre de usuario ya existe (excepto el actual)
        if Empleado.objects.filter(nombre_usuario=nombre_usuario).exclude(id_empleado=empleado_id).exists():
            return JsonResponse({
                'success': False,
                'message': f'El usuario "{nombre_usuario}" ya existe'
            }, status=400)
        
        # Actualizar datos
        empleado.nombre_usuario = nombre_usuario
        empleado.id_rol_id = id_rol
        empleado.id_caja_id = id_caja if id_caja else None
        empleado.save()
        
        # Registrar auditoría
        registrar_auditoria(
            usuario=request.user.username,
            accion=f'Empleado editado: {nombre_usuario}',
            detalles=f'ID: {empleado_id}, Rol: {empleado.id_rol.descripcion}',
            ip=request.META.get('REMOTE_ADDR')
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Empleado "{nombre_usuario}" actualizado exitosamente',
            'empleado': {
                'id': empleado.id_empleado,
                'nombre_usuario': empleado.nombre_usuario,
                'rol': empleado.id_rol.descripcion,
                'caja': empleado.id_caja.nombre_caja if empleado.id_caja else 'Sin asignar',
                'activo': empleado.activo
            }
        })
        
    except Empleado.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Empleado no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al editar empleado: {str(e)}'
        }, status=500)


@solo_administrador
@require_http_methods(['POST'])
def resetear_password_empleado_ajax(request, empleado_id):
    """
    Endpoint AJAX para resetear la contraseña de un empleado
    """
    try:
        empleado = Empleado.objects.get(id_empleado=empleado_id)
        
        nueva_password = request.POST.get('nueva_password', '').strip()
        confirmar_password = request.POST.get('confirmar_password', '').strip()
        
        # Validaciones
        if not nueva_password:
            return JsonResponse({
                'success': False,
                'message': 'La nueva contraseña no puede estar vacía'
            }, status=400)
        
        if nueva_password != confirmar_password:
            return JsonResponse({
                'success': False,
                'message': 'Las contraseñas no coinciden'
            }, status=400)
        
        if len(nueva_password) < 4:
            return JsonResponse({
                'success': False,
                'message': 'La contraseña debe tener al menos 4 caracteres'
            }, status=400)
        
        # Hash de la nueva contraseña
        password_hash = bcrypt.hashpw(nueva_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        empleado.contrasena_hash = password_hash
        empleado.save()
        
        # Registrar auditoría
        registrar_auditoria(
            usuario=request.user.username,
            accion=f'Contraseña reseteada para: {empleado.nombre_usuario}',
            detalles=f'ID Empleado: {empleado_id}',
            ip=request.META.get('REMOTE_ADDR')
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Contraseña de "{empleado.nombre_usuario}" actualizada exitosamente'
        })
        
    except Empleado.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Empleado no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al resetear contraseña: {str(e)}'
        }, status=500)


@solo_administrador
@require_http_methods(['POST'])
def toggle_estado_empleado_ajax(request, empleado_id):
    """
    Endpoint AJAX para activar/desactivar un empleado
    """
    try:
        empleado = Empleado.objects.get(id_empleado=empleado_id)
        
        # Cambiar estado
        empleado.activo = not empleado.activo
        empleado.save()
        
        estado_texto = 'activado' if empleado.activo else 'desactivado'
        
        # Registrar auditoría
        registrar_auditoria(
            usuario=request.user.username,
            accion=f'Empleado {estado_texto}: {empleado.nombre_usuario}',
            detalles=f'ID: {empleado_id}, Estado: {empleado.activo}',
            ip=request.META.get('REMOTE_ADDR')
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Empleado "{empleado.nombre_usuario}" {estado_texto} exitosamente',
            'nuevo_estado': empleado.activo
        })
        
    except Empleado.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Empleado no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al cambiar estado: {str(e)}'
        }, status=500)


@solo_administrador
def obtener_empleado_ajax(request, empleado_id):
    """
    Endpoint AJAX para obtener datos de un empleado (para edición)
    """
    try:
        empleado = Empleado.objects.select_related('id_rol', 'id_caja').get(id_empleado=empleado_id)
        
        return JsonResponse({
            'success': True,
            'empleado': {
                'id': empleado.id_empleado,
                'nombre_usuario': empleado.nombre_usuario,
                'id_rol': empleado.id_rol.id_rol,
                'rol_descripcion': empleado.id_rol.descripcion,
                'id_caja': empleado.id_caja.id_caja if empleado.id_caja else None,
                'caja_nombre': empleado.id_caja.nombre_caja if empleado.id_caja else None,
                'activo': empleado.activo
            }
        })
        
    except Empleado.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Empleado no encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener empleado: {str(e)}'
        }, status=500)

