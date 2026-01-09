# Portal de Padres - API REST
# Endpoints para consultas móviles de saldo, movimientos y recargas

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import timedelta

from .models import (
    Tarjeta, ConsumoTarjeta, CargasSaldo, Hijo,
    UsuarioPortal, TransaccionOnline, Notificacion
)
from .portal_serializers import (
    TarjetaSerializer, ConsumoTarjetaSerializer, CargaSaldoSerializer,
    TransaccionOnlineSerializer, NotificacionSerializer, RecargaTarjetaSerializer
)


# ========== UTILIDADES ==========

def get_usuario_portal_from_session(request):
    """Obtener usuario del portal desde la sesión"""
    usuario_id = request.session.get('portal_usuario_id')
    if not usuario_id:
        return None
    
    try:
        return UsuarioPortal.objects.get(id_usuario_portal=usuario_id, activo=True)
    except UsuarioPortal.DoesNotExist:
        return None


def verificar_acceso_tarjeta(usuario_portal, nro_tarjeta):
    """Verificar que el usuario tiene acceso a la tarjeta"""
    try:
        tarjeta = Tarjeta.objects.select_related('id_hijo__id_cliente').get(
            nro_tarjeta=nro_tarjeta
        )
        
        # Verificar que la tarjeta pertenece al cliente del usuario
        if tarjeta.id_hijo.id_cliente != usuario_portal.cliente:
            return None, {"error": "No tiene permiso para acceder a esta tarjeta"}
        
        return tarjeta, None
    except Tarjeta.DoesNotExist:
        return None, {"error": "Tarjeta no encontrada"}


# ========== ENDPOINTS DE CONSULTA ==========

@api_view(['GET'])
def api_saldo_tarjeta(request, nro_tarjeta):
    """
    GET /api/portal/tarjeta/<nro_tarjeta>/saldo/
    
    Consultar saldo actual de una tarjeta
    
    Response:
    {
        "nro_tarjeta": "1234567890",
        "hijo": {...},
        "saldo_actual": 50000,
        "saldo_formateado": "₲ 50.000",
        "estado": "Activa",
        "saldo_alerta": 5000,
        "alerta_saldo_bajo": true
    }
    """
    usuario = get_usuario_portal_from_session(request)
    if not usuario:
        return Response(
            {"error": "Debe iniciar sesión"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    tarjeta, error = verificar_acceso_tarjeta(usuario, nro_tarjeta)
    if error:
        return Response(error, status=status.HTTP_403_FORBIDDEN)
    
    serializer = TarjetaSerializer(tarjeta)
    data = serializer.data
    
    # Agregar indicador de saldo bajo
    data['alerta_saldo_bajo'] = tarjeta.saldo_actual < (tarjeta.saldo_alerta or 5000)
    
    return Response(data)


@api_view(['GET'])
def api_movimientos_tarjeta(request, nro_tarjeta):
    """
    GET /api/portal/tarjeta/<nro_tarjeta>/movimientos/
    
    Obtener movimientos de una tarjeta (consumos + recargas)
    
    Query params:
    - desde: fecha desde (YYYY-MM-DD)
    - hasta: fecha hasta (YYYY-MM-DD)
    - limit: número de resultados (default: 50)
    
    Response:
    {
        "tarjeta": {...},
        "periodo": {"desde": "2025-01-01", "hasta": "2025-01-08"},
        "resumen": {
            "total_consumos": 15,
            "monto_consumos": 75000,
            "total_recargas": 3,
            "monto_recargas": 100000
        },
        "movimientos": [
            {
                "tipo": "consumo",
                "fecha": "2025-01-08 14:30:00",
                "monto": -5000,
                "descripcion": "Consumo cantina",
                "saldo_resultante": 45000
            },
            ...
        ]
    }
    """
    usuario = get_usuario_portal_from_session(request)
    if not usuario:
        return Response(
            {"error": "Debe iniciar sesión"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    tarjeta, error = verificar_acceso_tarjeta(usuario, nro_tarjeta)
    if error:
        return Response(error, status=status.HTTP_403_FORBIDDEN)
    
    # Parámetros de filtro
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')
    limit = int(request.GET.get('limit', 50))
    
    # Fechas por defecto (últimos 30 días)
    if not hasta:
        hasta = timezone.now()
    else:
        hasta = timezone.datetime.strptime(hasta, '%Y-%m-%d')
    
    if not desde:
        desde = hasta - timedelta(days=30)
    else:
        desde = timezone.datetime.strptime(desde, '%Y-%m-%d')
    
    # Consultar consumos
    consumos = ConsumoTarjeta.objects.filter(
        nro_tarjeta=tarjeta,
        fecha_consumo__range=[desde, hasta]
    ).order_by('-fecha_consumo')[:limit]
    
    # Consultar recargas
    recargas = CargasSaldo.objects.filter(
        nro_tarjeta=tarjeta,
        fecha_carga__range=[desde, hasta]
    ).order_by('-fecha_carga')[:limit]
    
    # Combinar y ordenar movimientos
    movimientos = []
    
    for consumo in consumos:
        movimientos.append({
            'tipo': 'consumo',
            'id': consumo.id_consumo,
            'fecha': consumo.fecha_consumo,
            'monto': -consumo.monto,
            'monto_formateado': f"- ₲ {consumo.monto:,.0f}",
            'descripcion': f"Consumo cantina",
            'cantidad': consumo.cantidad if hasattr(consumo, 'cantidad') else 1
        })
    
    for recarga in recargas:
        movimientos.append({
            'tipo': 'recarga',
            'id': recarga.id_carga,
            'fecha': recarga.fecha_carga,
            'monto': recarga.monto,
            'monto_formateado': f"+ ₲ {recarga.monto:,.0f}",
            'descripcion': f"Recarga de saldo",
            'referencia': recarga.referencia_pago
        })
    
    # Ordenar por fecha descendente
    movimientos.sort(key=lambda x: x['fecha'], reverse=True)
    movimientos = movimientos[:limit]
    
    # Calcular resumen
    total_consumos = consumos.count()
    monto_consumos = consumos.aggregate(Sum('monto'))['monto__sum'] or 0
    
    total_recargas = recargas.count()
    monto_recargas = recargas.aggregate(Sum('monto'))['monto__sum'] or 0
    
    response_data = {
        'tarjeta': TarjetaSerializer(tarjeta).data,
        'periodo': {
            'desde': desde.strftime('%Y-%m-%d'),
            'hasta': hasta.strftime('%Y-%m-%d')
        },
        'resumen': {
            'total_consumos': total_consumos,
            'monto_consumos': monto_consumos,
            'monto_consumos_formateado': f"₲ {monto_consumos:,.0f}",
            'total_recargas': total_recargas,
            'monto_recargas': monto_recargas,
            'monto_recargas_formateado': f"₲ {monto_recargas:,.0f}",
            'saldo_neto': monto_recargas - monto_consumos
        },
        'movimientos': movimientos
    }
    
    return Response(response_data)


@api_view(['GET'])
def api_consumos_tarjeta(request, nro_tarjeta):
    """
    GET /api/portal/tarjeta/<nro_tarjeta>/consumos/
    
    Obtener solo los consumos de una tarjeta
    
    Query params:
    - desde: fecha desde (YYYY-MM-DD)
    - hasta: fecha hasta (YYYY-MM-DD)
    - limit: número de resultados (default: 50)
    """
    usuario = get_usuario_portal_from_session(request)
    if not usuario:
        return Response(
            {"error": "Debe iniciar sesión"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    tarjeta, error = verificar_acceso_tarjeta(usuario, nro_tarjeta)
    if error:
        return Response(error, status=status.HTTP_403_FORBIDDEN)
    
    # Parámetros de filtro
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')
    limit = int(request.GET.get('limit', 50))
    
    # Fechas por defecto
    if not hasta:
        hasta = timezone.now()
    else:
        hasta = timezone.datetime.strptime(hasta, '%Y-%m-%d')
    
    if not desde:
        desde = hasta - timedelta(days=30)
    else:
        desde = timezone.datetime.strptime(desde, '%Y-%m-%d')
    
    consumos = ConsumoTarjeta.objects.filter(
        nro_tarjeta=tarjeta,
        fecha_consumo__range=[desde, hasta]
    ).order_by('-fecha_consumo')[:limit]
    
    serializer = ConsumoTarjetaSerializer(consumos, many=True)
    
    return Response({
        'tarjeta': nro_tarjeta,
        'periodo': {
            'desde': desde.strftime('%Y-%m-%d'),
            'hasta': hasta.strftime('%Y-%m-%d')
        },
        'total': consumos.count(),
        'consumos': serializer.data
    })


@api_view(['GET'])
def api_recargas_tarjeta(request, nro_tarjeta):
    """
    GET /api/portal/tarjeta/<nro_tarjeta>/recargas/
    
    Obtener historial de recargas de una tarjeta
    """
    usuario = get_usuario_portal_from_session(request)
    if not usuario:
        return Response(
            {"error": "Debe iniciar sesión"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    tarjeta, error = verificar_acceso_tarjeta(usuario, nro_tarjeta)
    if error:
        return Response(error, status=status.HTTP_403_FORBIDDEN)
    
    # Parámetros de filtro
    limit = int(request.GET.get('limit', 50))
    
    recargas = CargasSaldo.objects.filter(
        nro_tarjeta=tarjeta
    ).order_by('-fecha_carga')[:limit]
    
    serializer = CargaSaldoSerializer(recargas, many=True)
    
    return Response({
        'tarjeta': nro_tarjeta,
        'total': recargas.count(),
        'recargas': serializer.data
    })


@api_view(['GET'])
def api_tarjetas_usuario(request):
    """
    GET /api/portal/mis-tarjetas/
    
    Obtener todas las tarjetas del usuario autenticado
    """
    usuario = get_usuario_portal_from_session(request)
    if not usuario:
        return Response(
            {"error": "Debe iniciar sesión"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Obtener todas las tarjetas de los hijos del cliente
    tarjetas = Tarjeta.objects.filter(
        id_hijo__id_cliente=usuario.cliente
    ).select_related('id_hijo').order_by('-saldo_actual')
    
    serializer = TarjetaSerializer(tarjetas, many=True)
    
    # Calcular totales
    saldo_total = sum(t.saldo_actual for t in tarjetas)
    tarjetas_activas = tarjetas.filter(estado='Activa').count()
    
    return Response({
        'usuario': usuario.email,
        'total_tarjetas': tarjetas.count(),
        'tarjetas_activas': tarjetas_activas,
        'saldo_total': saldo_total,
        'saldo_total_formateado': f"₲ {saldo_total:,.0f}",
        'tarjetas': serializer.data
    })


@api_view(['GET'])
def api_notificaciones_usuario(request):
    """
    GET /api/portal/notificaciones/
    
    Obtener notificaciones del usuario
    
    Query params:
    - solo_no_leidas: true/false (default: false)
    - limit: número de resultados (default: 20)
    """
    usuario = get_usuario_portal_from_session(request)
    if not usuario:
        return Response(
            {"error": "Debe iniciar sesión"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    solo_no_leidas = request.GET.get('solo_no_leidas', 'false').lower() == 'true'
    limit = int(request.GET.get('limit', 20))
    
    notificaciones = Notificacion.objects.filter(usuario_portal=usuario)
    
    if solo_no_leidas:
        notificaciones = notificaciones.filter(leida=False)
    
    notificaciones = notificaciones.order_by('-fecha_envio')[:limit]
    
    serializer = NotificacionSerializer(notificaciones, many=True)
    
    no_leidas = Notificacion.objects.filter(
        usuario_portal=usuario,
        leida=False
    ).count()
    
    return Response({
        'total_no_leidas': no_leidas,
        'notificaciones': serializer.data
    })


@api_view(['POST'])
def api_marcar_notificacion_leida(request, id_notificacion):
    """
    POST /api/portal/notificaciones/<id>/marcar-leida/
    
    Marcar una notificación como leída
    """
    usuario = get_usuario_portal_from_session(request)
    if not usuario:
        return Response(
            {"error": "Debe iniciar sesión"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    try:
        notificacion = Notificacion.objects.get(
            id_notificacion=id_notificacion,
            usuario_portal=usuario
        )
        
        notificacion.marcar_como_leida()
        
        return Response({
            'success': True,
            'mensaje': 'Notificación marcada como leída'
        })
    except Notificacion.DoesNotExist:
        return Response(
            {"error": "Notificación no encontrada"},
            status=status.HTTP_404_NOT_FOUND
        )
