"""
Views para el sistema de notificaciones
"""
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models_notificaciones import NotificacionSistema, ConfiguracionNotificacionesSistema


@login_required
@require_http_methods(["GET"])
def notificaciones_api(request):
    """
    API endpoint para obtener notificaciones del usuario
    
    Query params:
        - no_leidas: true/false (filtrar solo no leídas)
        - limit: número máximo de notificaciones (default: 10)
        - tipo: filtrar por tipo de notificación
    """
    usuario = request.user
    
    # Obtener parámetros
    solo_no_leidas = request.GET.get('no_leidas', 'false').lower() == 'true'
    limit = int(request.GET.get('limit', 10))
    tipo = request.GET.get('tipo', None)
    
    # Query base
    queryset = NotificacionSistema.objects.filter(usuario=usuario)
    
    # Filtros
    if solo_no_leidas:
        queryset = queryset.filter(leida=False)
    
    if tipo:
        queryset = queryset.filter(tipo=tipo)
    
    # Excluir expiradas
    queryset = queryset.exclude(
        expira_en__lt=timezone.now()
    )
    
    # Limitar resultados
    notificaciones = queryset[:limit]
    
    # Contar no leídas
    count_no_leidas = NotificacionSistema.count_no_leidas(usuario)
    
    return JsonResponse({
        'success': True,
        'count_no_leidas': count_no_leidas,
        'notificaciones': [notif.to_dict() for notif in notificaciones]
    })


@login_required
@require_http_methods(["POST"])
def marcar_como_leida(request, notificacion_id):
    """
    Marca una notificación como leída
    """
    NotificacionSistema = get_object_or_404(
        NotificacionSistema, 
        id=notificacion_id, 
        usuario=request.user
    )
    
    NotificacionSistema.marcar_como_leida()
    
    return JsonResponse({
        'success': True,
        'message': 'Notificación marcada como leída'
    })


@login_required
@require_http_methods(["POST"])
def marcar_todas_leidas(request):
    """
    Marca todas las notificaciones del usuario como leídas
    """
    notificaciones = NotificacionSistema.objects.filter(
        usuario=request.user,
        leida=False
    )
    
    count = notificaciones.count()
    
    for notif in notificaciones:
        notif.marcar_como_leida()
    
    return JsonResponse({
        'success': True,
        'message': f'{count} notificaciones marcadas como leídas'
    })


@login_required
@require_http_methods(["DELETE"])
def eliminar_notificacion(request, notificacion_id):
    """
    Elimina una notificación
    """
    NotificacionSistema = get_object_or_404(
        NotificacionSistema,
        id=notificacion_id,
        usuario=request.user
    )
    
    NotificacionSistema.delete()
    
    return JsonResponse({
        'success': True,
        'message': 'Notificación eliminada'
    })


@login_required
def panel_notificaciones(request):
    """
    Renderiza el panel completo de notificaciones
    """
    notificaciones = NotificacionSistema.objects.filter(
        usuario=request.user
    ).exclude(
        expira_en__lt=timezone.now()
    )[:50]
    
    count_no_leidas = NotificacionSistema.count_no_leidas(request.user)
    
    # Agrupar por tipo
    por_tipo = {}
    for tipo_key, tipo_label in NotificacionSistema.TIPO_CHOICES:
        notifs_tipo = [n for n in notificaciones if n.tipo == tipo_key]
        if notifs_tipo:
            por_tipo[tipo_label] = notifs_tipo
    
    context = {
        'notificaciones': notificaciones,
        'count_no_leidas': count_no_leidas,
        'por_tipo': por_tipo,
    }
    
    return render(request, 'notificaciones/panel.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def configuracion_notificaciones(request):
    """
    Vista para configurar preferencias de notificaciones
    """
    config = ConfiguracionNotificacionesSistema.get_or_create_for_user(request.user)
    
    if request.method == 'POST':
        # Actualizar configuración
        config.notif_ventas = request.POST.get('notif_ventas') == 'on'
        config.notif_recargas = request.POST.get('notif_recargas') == 'on'
        config.notif_stock = request.POST.get('notif_stock') == 'on'
        config.notif_sistema = request.POST.get('notif_sistema') == 'on'
        config.solo_criticas = request.POST.get('solo_criticas') == 'on'
        config.sonido_habilitado = request.POST.get('sonido_habilitado') == 'on'
        config.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Configuración guardada exitosamente'
        })
    
    context = {
        'config': config,
    }
    
    return render(request, 'notificaciones/configuracion.html', context)


@login_required
def notificaciones_badge(request):
    """
    Endpoint HTMX para el badge de notificaciones
    Solo retorna el número de no leídas
    """
    count = NotificacionSistema.count_no_leidas(request.user)
    
    return render(request, 'notificaciones/badge.html', {
        'count': count
    })


@login_required
def notificaciones_dropdown(request):
    """
    Endpoint HTMX para el dropdown de notificaciones
    """
    notificaciones = NotificacionSistema.objects.filter(
        usuario=request.user
    ).exclude(
        expira_en__lt=timezone.now()
    )[:5]  # Solo las 5 más recientes
    
    count_no_leidas = NotificacionSistema.count_no_leidas(request.user)
    
    return render(request, 'notificaciones/dropdown.html', {
        'notificaciones': notificaciones,
        'count_no_leidas': count_no_leidas
    })
