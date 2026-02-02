"""
Vistas para administración de configuración masiva de límites de crédito

Este módulo contiene vistas para gestionar límites de crédito
en múltiples tarjetas simultáneamente.

Autor: CantiTita
Fecha: 2026-01-12
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
import json

from gestion.models import Tarjeta, Hijo, AuditoriaOperacion
from gestion.permisos import solo_gerente_o_superior


@login_required
@solo_gerente_o_superior
def configurar_limites_masivo_view(request):
    """
    Vista principal para configuración masiva de límites
    """
    # Obtener filtros
    filtro_grado = request.GET.get('grado', '')
    filtro_seccion = request.GET.get('seccion', '')
    filtro_estado = request.GET.get('estado', '')
    filtro_permite = request.GET.get('permite_saldo_negativo', '')
    
    # Query base
    tarjetas = Tarjeta.objects.select_related('id_hijo').all()
    
    # Aplicar filtros
    if filtro_grado:
        tarjetas = tarjetas.filter(id_hijo__grado=filtro_grado)
    
    if filtro_seccion:
        tarjetas = tarjetas.filter(id_hijo__seccion=filtro_seccion)
    
    if filtro_estado:
        tarjetas = tarjetas.filter(estado=filtro_estado)
    
    if filtro_permite in ['0', '1']:
        tarjetas = tarjetas.filter(permite_saldo_negativo=(filtro_permite == '1'))
    
    # Obtener valores únicos para filtros
    grados = Hijo.objects.values_list('grado', flat=True).distinct().order_by('grado')
    secciones = Hijo.objects.values_list('seccion', flat=True).distinct().order_by('seccion')
    
    context = {
        'tarjetas': tarjetas,
        'grados': grados,
        'secciones': secciones,
        'filtro_grado': filtro_grado,
        'filtro_seccion': filtro_seccion,
        'filtro_estado': filtro_estado,
        'filtro_permite': filtro_permite,
    }
    
    return render(request, 'pos/admin/configurar_limites_masivo.html', context)


@login_required
@solo_gerente_o_superior
@require_http_methods(["POST"])
def aplicar_configuracion_masiva(request):
    """
    Aplicar configuración masiva de límites a tarjetas seleccionadas
    """
    try:
        # Parsear datos JSON
        data = json.loads(request.body)
        
        tarjetas_ids = data.get('tarjetas', [])
        nuevo_limite = data.get('nuevo_limite')
        habilitar_saldo_negativo = data.get('habilitar_saldo_negativo', False)
        motivo = data.get('motivo', '')
        
        # Validaciones
        if not tarjetas_ids:
            return JsonResponse({
                'success': False,
                'mensaje': 'Debe seleccionar al menos una tarjeta'
            })
        
        if not nuevo_limite or not motivo:
            return JsonResponse({
                'success': False,
                'mensaje': 'Complete todos los campos requeridos'
            })
        
        try:
            nuevo_limite = float(nuevo_limite)
            if nuevo_limite < 0:
                raise ValueError("Límite no puede ser negativo")
        except ValueError as e:
            return JsonResponse({
                'success': False,
                'mensaje': f'Límite inválido: {str(e)}'
            })
        
        # Aplicar cambios en transacción atómica
        with transaction.atomic():
            tarjetas = Tarjeta.objects.filter(nro_tarjeta__in=tarjetas_ids)
            
            tarjetas_actualizadas = 0
            
            for tarjeta in tarjetas:
                # Guardar valores anteriores para auditoría
                limite_anterior = tarjeta.limite_credito
                permite_anterior = tarjeta.permite_saldo_negativo
                
                # Aplicar cambios
                tarjeta.limite_credito = nuevo_limite
                
                if habilitar_saldo_negativo:
                    tarjeta.permite_saldo_negativo = True
                
                tarjeta.save()
                
                # Registrar en auditoría
                registrar_auditoria_configuracion_masiva(
                    tarjeta=tarjeta,
                    usuario=request.user,
                    limite_anterior=limite_anterior,
                    limite_nuevo=nuevo_limite,
                    permite_anterior=permite_anterior,
                    permite_nuevo=tarjeta.permite_saldo_negativo,
                    motivo=motivo
                )
                
                tarjetas_actualizadas += 1
        
        return JsonResponse({
            'success': True,
            'tarjetas_actualizadas': tarjetas_actualizadas,
            'mensaje': f'Se actualizaron {tarjetas_actualizadas} tarjetas exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'mensaje': 'Error al parsear datos JSON'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'mensaje': f'Error al aplicar cambios: {str(e)}'
        })


def registrar_auditoria_configuracion_masiva(tarjeta, usuario, limite_anterior, 
                                            limite_nuevo, permite_anterior, 
                                            permite_nuevo, motivo):
    """
    Registrar cambio en auditoría
    """
    try:
        descripcion = f"""
        Configuración Masiva de Límite de Crédito
        
        Tarjeta: {tarjeta.nro_tarjeta}
        Límite Anterior: Gs. {limite_anterior:,.0f}
        Límite Nuevo: Gs. {limite_nuevo:,.0f}
        Permite Saldo Negativo Anterior: {permite_anterior}
        Permite Saldo Negativo Nuevo: {permite_nuevo}
        
        Motivo: {motivo}
        """
        
        AuditoriaOperacion.objects.create(
            tipo_operacion='CONFIGURACION_MASIVA_LIMITE',
            descripcion=descripcion,
            id_usuario=usuario,
            fecha_hora=timezone.now(),
            tabla_afectada='tarjetas',
            registro_afectado=tarjeta.nro_tarjeta,
            datos_anteriores=json.dumps({
                'limite_credito': float(limite_anterior or 0),
                'permite_saldo_negativo': permite_anterior
            }),
            datos_nuevos=json.dumps({
                'limite_credito': float(limite_nuevo),
                'permite_saldo_negativo': permite_nuevo
            })
        )
    except Exception as e:
        # No fallar si no se puede registrar auditoría
        print(f"Error registrando auditoría: {e}")


@login_required
@solo_gerente_o_superior
def historial_configuraciones_masivas(request):
    """
    Ver historial de configuraciones masivas aplicadas
    """
    historial = AuditoriaOperacion.objects.filter(
        tipo_operacion='CONFIGURACION_MASIVA_LIMITE'
    ).order_by('-fecha_hora')[:100]
    
    context = {
        'historial': historial
    }
    
    return render(request, 'pos/admin/historial_configuraciones.html', context)
