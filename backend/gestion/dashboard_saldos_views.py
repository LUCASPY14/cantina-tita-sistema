"""
Vistas para dashboard de saldos en tiempo real

Este módulo contiene vistas para monitorear saldos de tarjetas
en tiempo real con actualización automática.

Autor: CantiTita
Fecha: 2026-01-12
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from decimal import Decimal

from gestion.models import Tarjeta, Hijo
from gestion.permisos import acceso_cajero


@login_required
@acceso_cajero
def dashboard_saldos_tiempo_real(request):
    """
    Vista principal del dashboard de saldos en tiempo real
    """
    context = {
        'titulo': 'Dashboard de Saldos - Tiempo Real',
        'fecha_actualizacion': 'Al cargar la página'
    }
    
    return render(request, 'dashboard/saldos_tiempo_real.html', context)


@login_required
@acceso_cajero
def api_saldos_tiempo_real(request):
    """
    API JSON para obtener saldos actualizados en tiempo real
    """
    try:
        # Obtener todas las tarjetas activas
        tarjetas = Tarjeta.objects.filter(
            estado='Activa'
        ).select_related('id_hijo').all()
        
        # Preparar datos
        tarjetas_data = []
        
        # Contadores
        count_negativos = 0
        count_bajos = 0
        count_ok = 0
        
        for tarjeta in tarjetas:
            saldo = float(tarjeta.saldo or 0)
            limite_saldo_bajo = float(tarjeta.limite_saldo_bajo or 50000)
            
            # Determinar estado
            if saldo < 0:
                estado = 'negativo'
                count_negativos += 1
            elif saldo < limite_saldo_bajo:
                estado = 'bajo'
                count_bajos += 1
            else:
                estado = 'ok'
                count_ok += 1
            
            # Datos de la tarjeta
            tarjeta_info = {
                'nro_tarjeta': tarjeta.nro_tarjeta,
                'estudiante': tarjeta.id_hijo.nombre_completo if tarjeta.id_hijo else 'Sin asignar',
                'grado': tarjeta.id_hijo.grado if tarjeta.id_hijo else '',
                'seccion': tarjeta.id_hijo.seccion if tarjeta.id_hijo else '',
                'saldo': saldo,
                'saldo_formateado': f'{saldo:,.0f}',
                'limite_saldo_bajo': limite_saldo_bajo,
                'estado': estado,
                'permite_saldo_negativo': tarjeta.permite_saldo_negativo,
                'limite_credito': float(tarjeta.limite_credito or 0) if tarjeta.limite_credito else 0
            }
            
            tarjetas_data.append(tarjeta_info)
        
        # Ordenar por saldo ascendente (más críticos primero)
        tarjetas_data.sort(key=lambda x: x['saldo'])
        
        # Estadísticas
        estadisticas = {
            'total': len(tarjetas_data),
            'negativos': count_negativos,
            'bajos': count_bajos,
            'ok': count_ok
        }
        
        return JsonResponse({
            'success': True,
            'tarjetas': tarjetas_data,
            'estadisticas': estadisticas
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'mensaje': f'Error al obtener saldos: {str(e)}'
        })
