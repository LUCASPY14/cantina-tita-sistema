"""
Vistas para Autorización de Saldo Negativo
POS - Cantina Tita
"""

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import json

from gestion.models import Tarjeta, Empleado
from pos.models import Venta as Ventas
from gestion.permisos import acceso_cajero, solo_administrador, solo_gerente_o_superior
from gestion.autorizacion_saldo_utils import (
    puede_autorizar_saldo_negativo,
    validar_limite_credito,
    autorizar_venta_saldo_negativo
)
from gestion.notificaciones_saldo import verificar_saldo_y_notificar


@acceso_cajero
@require_http_methods(["POST"])
def verificar_saldo_venta(request):
    """
    AJAX - Verifica si hay saldo suficiente antes de procesar venta
    
    Si no hay saldo, retorna opciones:
    - Recargar saldo
    - Reducir productos
    - Autorizar saldo negativo (si está habilitado)
    """
    try:
        data = json.loads(request.body)
        nro_tarjeta = data.get('nro_tarjeta')
        total_venta = Decimal(str(data.get('total', 0)))
        
        if not nro_tarjeta:
            return JsonResponse({
                'success': False,
                'error': 'Número de tarjeta requerido'
            })
        
        # Obtener tarjeta
        try:
            tarjeta = Tarjeta.objects.select_related('id_hijo').get(
                nro_tarjeta=nro_tarjeta,
                estado='Activa'
            )
        except Tarjeta.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Tarjeta no encontrada o inactiva'
            })
        
        saldo_actual = tarjeta.saldo_actual
        
        # Caso 1: Saldo suficiente
        if saldo_actual >= total_venta:
            return JsonResponse({
                'success': True,
                'tiene_saldo': True,
                'saldo_actual': int(saldo_actual),
                'total_venta': int(total_venta),
                'mensaje': 'Saldo suficiente'
            })
        
        # Caso 2: Saldo insuficiente
        faltante = total_venta - saldo_actual
        
        # Verificar si puede usar saldo negativo
        puede_negativo, mensaje_limite = validar_limite_credito(tarjeta, total_venta)
        
        response_data = {
            'success': True,
            'tiene_saldo': False,
            'saldo_actual': int(saldo_actual),
            'total_venta': int(total_venta),
            'faltante': int(faltante),
            'hijo_nombre': tarjeta.id_hijo.nombre_completo if tarjeta.id_hijo else '',
            'permite_saldo_negativo': tarjeta.permite_saldo_negativo,
            'limite_credito': int(tarjeta.limite_credito or 0),
            'puede_autorizar': puede_negativo,
            'mensaje': mensaje_limite,
            'opciones': []
        }
        
        # Opciones disponibles
        response_data['opciones'].append({
            'id': 'recargar',
            'texto': 'Recargar Saldo',
            'url': f'/pos/recargas/?tarjeta={nro_tarjeta}',
            'icono': '💳',
            'recomendado': True
        })
        
        response_data['opciones'].append({
            'id': 'reducir',
            'texto': 'Reducir Productos del Carrito',
            'icono': '➖',
            'recomendado': False
        })
        
        if puede_negativo and tarjeta.permite_saldo_negativo:
            response_data['opciones'].append({
                'id': 'autorizar',
                'texto': 'Autorizar Venta con Saldo Negativo',
                'icono': '⚠️',
                'requiere_supervisor': True,
                'recomendado': False
            })
        
        response_data['opciones'].append({
            'id': 'cancelar',
            'texto': 'Cancelar Venta',
            'icono': '❌',
            'recomendado': False
        })
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@solo_gerente_o_superior
@require_http_methods(["POST"])
def autorizar_venta_saldo_negativo_ajax(request):
    """
    AJAX - Autoriza una venta que dejará el saldo en negativo
    
    Requiere:
    - ID del supervisor (gerente o admin)
    - Motivo de la autorización
    - Datos de la venta
    """
    try:
        data = json.loads(request.body)
        nro_tarjeta = data.get('nro_tarjeta')
        total_venta = Decimal(str(data.get('total', 0)))
        motivo = data.get('motivo', '').strip()
        id_empleado_supervisor = data.get('id_supervisor')
        password_supervisor = data.get('password_supervisor', '')
        
        # Validaciones
        if not all([nro_tarjeta, total_venta, motivo, id_empleado_supervisor]):
            return JsonResponse({
                'success': False,
                'error': 'Datos incompletos'
            })
        
        if len(motivo) < 10:
            return JsonResponse({
                'success': False,
                'error': 'El motivo debe tener al menos 10 caracteres'
            })
        
        # Obtener supervisor
        try:
            import bcrypt
            supervisor = Empleado.objects.get(
                id_empleado=id_empleado_supervisor,
                activo=True
            )
            
            # Validar contraseña del supervisor
            if password_supervisor:
                password_correcto = bcrypt.checkpw(
                    password_supervisor.encode('utf-8'),
                    supervisor.password.encode('utf-8')
                )
                if not password_correcto:
                    return JsonResponse({
                        'success': False,
                        'error': 'Contraseña de supervisor incorrecta'
                    })
            
        except Empleado.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Supervisor no encontrado'
            })
        
        # Verificar permisos del supervisor
        if not puede_autorizar_saldo_negativo(supervisor):
            return JsonResponse({
                'success': False,
                'error': 'El empleado no tiene permisos para autorizar saldo negativo'
            })
        
        # Obtener tarjeta
        try:
            tarjeta = Tarjeta.objects.select_for_update().get(nro_tarjeta=nro_tarjeta)
        except Tarjeta.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Tarjeta no encontrada'
            })
        
        # Validar límite de crédito
        puede, mensaje = validar_limite_credito(tarjeta, total_venta)
        if not puede:
            return JsonResponse({
                'success': False,
                'error': mensaje
            })
        
        # Calcular nuevo saldo
        saldo_anterior = tarjeta.saldo_actual
        saldo_nuevo = saldo_anterior - total_venta
        
        # Retornar autorización exitosa
        # La venta real se procesa en procesar_venta() con este token
        return JsonResponse({
            'success': True,
            'autorizado': True,
            'supervisor_nombre': f"{supervisor.nombre} {supervisor.apellido}",
            'saldo_anterior': int(saldo_anterior),
            'saldo_nuevo': int(saldo_nuevo),
            'deuda_generada': int(abs(saldo_nuevo)) if saldo_nuevo < 0 else 0,
            'mensaje': f'Venta autorizada por {supervisor.nombre} {supervisor.apellido}',
            # Token para validar en procesar_venta
            'autorizacion_data': {
                'id_supervisor': id_empleado_supervisor,
                'motivo': motivo,
                'timestamp': timezone.now().isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@acceso_cajero
def modal_autorizar_saldo_negativo(request):
    """
    Renderiza modal para solicitar autorización de supervisor
    """
    nro_tarjeta = request.GET.get('tarjeta')
    total_venta = request.GET.get('total', 0)
    faltante = request.GET.get('faltante', 0)
    
    # Obtener supervisores (gerentes y administradores activos)
    supervisores = Empleado.objects.filter(
        activo=True,
        id_rol__nombre_rol__in=['ADMINISTRADOR', 'GERENTE']
    ).select_related('id_rol')
    
    context = {
        'nro_tarjeta': nro_tarjeta,
        'total_venta': total_venta,
        'faltante': faltante,
        'supervisores': supervisores,
    }
    
    return render(request, 'pos/modales/autorizar_saldo_negativo.html', context)


@solo_gerente_o_superior
def listar_autorizaciones_saldo_negativo(request):
    """
    Lista todas las autorizaciones de saldo negativo realizadas
    """
    from gestion.models import AutorizacionSaldoNegativo
    from django.core.paginator import Paginator
    
    # Filtros
    fecha_desde = request.GET.get('fecha_desde')
    fecha_hasta = request.GET.get('fecha_hasta')
    solo_pendientes = request.GET.get('pendientes') == '1'
    
    autorizaciones = AutorizacionSaldoNegativo.objects.select_related(
        'nro_tarjeta__id_hijo',
        'id_empleado_autoriza',
        'id_venta'
    ).order_by('-fecha_autorizacion')
    
    if fecha_desde:
        autorizaciones = autorizaciones.filter(fecha_autorizacion__gte=fecha_desde)
    
    if fecha_hasta:
        autorizaciones = autorizaciones.filter(fecha_autorizacion__lte=fecha_hasta)
    
    if solo_pendientes:
        autorizaciones = autorizaciones.filter(regularizado=False)
    
    # Paginación
    paginator = Paginator(autorizaciones, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    total_autorizaciones = autorizaciones.count()
    pendientes = autorizaciones.filter(regularizado=False).count()
    monto_total_deuda = sum(
        abs(a.saldo_resultante) for a in autorizaciones.filter(regularizado=False)
        if a.saldo_resultante < 0
    )
    
    context = {
        'page_obj': page_obj,
        'total_autorizaciones': total_autorizaciones,
        'pendientes': pendientes,
        'monto_total_deuda': monto_total_deuda,
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'solo_pendientes': solo_pendientes,
    }
    
    return render(request, 'pos/autorizaciones_saldo_negativo.html', context)
