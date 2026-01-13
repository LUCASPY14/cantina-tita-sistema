"""
Vistas para gestión de términos legales de saldo negativo

Este módulo contiene vistas para mostrar, aceptar y revocar
los términos legales del sistema de saldo negativo.

Autor: CantiTita
Fecha: 2026-01-12
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
import json

from gestion.models import Tarjeta, Cliente
from gestion.terminos_legales_model import AceptacionTerminosSaldoNegativo


def obtener_ip_cliente(request):
    """Obtener IP real del cliente considerando proxies"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def terminos_saldo_negativo(request):
    """
    Mostrar términos legales de saldo negativo
    """
    # Obtener tarjeta del usuario
    nro_tarjeta = request.GET.get('tarjeta')
    
    tarjeta = None
    aceptacion_existente = None
    
    if nro_tarjeta:
        try:
            tarjeta = Tarjeta.objects.get(nro_tarjeta=nro_tarjeta)
            
            # Verificar si ya existe aceptación activa
            aceptacion_existente = AceptacionTerminosSaldoNegativo.objects.filter(
                tarjeta=tarjeta,
                activo=True,
                revocado=False
            ).first()
            
        except Tarjeta.DoesNotExist:
            messages.error(request, 'Tarjeta no encontrada')
    
    context = {
        'tarjeta': tarjeta,
        'aceptacion_existente': aceptacion_existente,
        'fecha_actual': timezone.now(),
    }
    
    return render(request, 'portal/terminos_saldo_negativo.html', context)


@login_required
@require_http_methods(["POST"])
def aceptar_terminos(request):
    """
    Registrar aceptación de términos legales
    """
    try:
        # Parsear datos
        data = json.loads(request.body)
        
        nro_tarjeta = data.get('nro_tarjeta')
        acepta_terminos = data.get('acepta_terminos', False)
        acepta_notificaciones = data.get('acepta_notificaciones', False)
        
        # Validaciones
        if not nro_tarjeta:
            return JsonResponse({
                'success': False,
                'mensaje': 'Número de tarjeta requerido'
            })
        
        if not acepta_terminos or not acepta_notificaciones:
            return JsonResponse({
                'success': False,
                'mensaje': 'Debe aceptar ambos términos'
            })
        
        # Obtener tarjeta
        try:
            tarjeta = Tarjeta.objects.get(nro_tarjeta=nro_tarjeta)
        except Tarjeta.DoesNotExist:
            return JsonResponse({
                'success': False,
                'mensaje': 'Tarjeta no encontrada'
            })
        
        # Verificar si ya existe aceptación activa
        aceptacion_existente = AceptacionTerminosSaldoNegativo.objects.filter(
            tarjeta=tarjeta,
            activo=True,
            revocado=False
        ).first()
        
        if aceptacion_existente:
            return JsonResponse({
                'success': False,
                'mensaje': 'Ya existe una aceptación activa para esta tarjeta'
            })
        
        # Obtener cliente
        cliente = tarjeta.id_cliente
        
        # Obtener contenido completo de los términos (simulado - en producción vendría de un template o DB)
        contenido_terminos = """
        TÉRMINOS Y CONDICIONES - SISTEMA DE SALDO NEGATIVO
        
        1. DEFINICIONES
        - Saldo Negativo: Operación que permite realizar compras aunque el saldo sea insuficiente
        - Límite de Crédito: Monto máximo de deuda permitido
        - Regularización: Pago total de la deuda acumulada
        
        2. CONDICIONES DE USO
        - Plazo máximo: 15 días calendario
        - Requiere autorización de supervisor
        - Sujeto a límite de crédito configurado
        - Bloqueo automático al vencimiento
        
        ... [contenido completo]
        
        Fecha de aceptación: {fecha}
        Versión: 1.0
        """.format(fecha=timezone.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Crear aceptación
        aceptacion = AceptacionTerminosSaldoNegativo.objects.create(
            tarjeta=tarjeta,
            id_cliente=cliente,
            id_usuario_portal=request.user,
            ip_address=obtener_ip_cliente(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:200],
            version_terminos='1.0',
            contenido_aceptado=contenido_terminos,
            activo=True,
            revocado=False
        )
        
        # Generar firma digital
        aceptacion.generar_firma_digital()
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Términos aceptados correctamente',
            'aceptacion_id': aceptacion.id,
            'firma_digital': aceptacion.firma_digital
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'mensaje': 'Error al parsear datos JSON'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'mensaje': f'Error al procesar aceptación: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def revocar_terminos(request):
    """
    Revocar aceptación de términos legales
    """
    try:
        # Parsear datos
        data = json.loads(request.body)
        
        aceptacion_id = data.get('aceptacion_id')
        motivo = data.get('motivo', 'Revocado por el usuario')
        
        # Validaciones
        if not aceptacion_id:
            return JsonResponse({
                'success': False,
                'mensaje': 'ID de aceptación requerido'
            })
        
        # Obtener aceptación
        try:
            aceptacion = AceptacionTerminosSaldoNegativo.objects.get(id=aceptacion_id)
        except AceptacionTerminosSaldoNegativo.DoesNotExist:
            return JsonResponse({
                'success': False,
                'mensaje': 'Aceptación no encontrada'
            })
        
        # Verificar que pertenece al usuario actual
        if aceptacion.id_usuario_portal != request.user:
            return JsonResponse({
                'success': False,
                'mensaje': 'No tiene permisos para revocar esta aceptación'
            })
        
        # Revocar
        aceptacion.revocar()
        
        # Deshabilitar saldo negativo en la tarjeta
        tarjeta = aceptacion.tarjeta
        tarjeta.permite_saldo_negativo = False
        tarjeta.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Términos revocados correctamente. El saldo negativo ha sido deshabilitado para esta tarjeta.'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'mensaje': 'Error al parsear datos JSON'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'mensaje': f'Error al procesar revocación: {str(e)}'
        })
