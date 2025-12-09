"""
Vistas para el dashboard de seguridad (administradores)
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from datetime import timedelta
import csv
import json

from .models import (
    IntentoLogin, AuditoriaOperacion, TokenRecuperacion, 
    BloqueoCuenta, UsuariosWebClientes, AnomaliaDetectada,
    PatronAcceso, SesionActiva, Intento2Fa, RenovacionSesion
)
from .seguridad_utils import obtener_estadisticas_2fa


@login_required
def dashboard_seguridad_view(request):
    """Dashboard principal de seguridad para administradores"""
    
    # Estadísticas generales (últimos 30 días)
    fecha_limite = timezone.now() - timedelta(days=30)
    
    # Intentos de login
    intentos_fallidos_hoy = IntentoLogin.objects.filter(
        exitoso=False,
        fecha_intento__date=timezone.now().date()
    ).count()
    
    intentos_exitosos_hoy = IntentoLogin.objects.filter(
        exitoso=True,
        fecha_intento__date=timezone.now().date()
    ).count()
    
    # Cuentas bloqueadas activas
    cuentas_bloqueadas = BloqueoCuenta.objects.filter(activo=True).count()
    
    # Tokens de recuperación activos
    tokens_activos = TokenRecuperacion.objects.filter(
        usado=False,
        fecha_expiracion__gt=timezone.now()
    ).count()
    
    # Operaciones de auditoría (últimos 7 días)
    operaciones_semana = AuditoriaOperacion.objects.filter(
        fecha_operacion__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Gráfico de intentos por día (últimos 14 días)
    intentos_por_dia = IntentoLogin.objects.filter(
        fecha_intento__gte=timezone.now() - timedelta(days=14)
    ).annotate(
        dia=TruncDate('fecha_intento')
    ).values('dia', 'exitoso').annotate(
        total=Count('id_intento')
    ).order_by('dia')
    
    # Preparar datos para gráfico
    dias_exitosos = {}
    dias_fallidos = {}
    
    for item in intentos_por_dia:
        dia_str = item['dia'].strftime('%Y-%m-%d')
        if item['exitoso']:
            dias_exitosos[dia_str] = item['total']
        else:
            dias_fallidos[dia_str] = item['total']
    
    # Últimas 10 cuentas bloqueadas
    ultimos_bloqueos = BloqueoCuenta.objects.filter(
        activo=True
    ).order_by('-fecha_bloqueo')[:10]
    
    # Top 10 IPs con más intentos fallidos (últimos 7 días)
    top_ips_sospechosas = IntentoLogin.objects.filter(
        exitoso=False,
        fecha_intento__gte=timezone.now() - timedelta(days=7)
    ).values('ip_address', 'ciudad', 'pais').annotate(
        intentos=Count('id_intento')
    ).order_by('-intentos')[:10]
    
    # Últimas operaciones de auditoría
    ultimas_operaciones = AuditoriaOperacion.objects.select_related().order_by('-fecha_operacion')[:20]
    
    # Anomalías recientes (últimos 7 días)
    anomalias_recientes = AnomaliaDetectada.objects.filter(
        fecha_deteccion__gte=timezone.now() - timedelta(days=7)
    ).order_by('-fecha_deteccion')[:10]
    
    # Sesiones activas ahora
    sesiones_activas_count = SesionActiva.objects.filter(activa=True).count()
    
    # Estadísticas 2FA (últimos 30 días)
    stats_2fa = obtener_estadisticas_2fa(dias=30)
    
    # Intentos 2FA recientes (últimos 7 días)
    intentos_2fa_recientes = Intento2Fa.objects.filter(
        fecha_intento__gte=timezone.now() - timedelta(days=7)
    ).order_by('-fecha_intento')[:10]
    
    # Renovaciones de sesión recientes
    renovaciones_recientes = RenovacionSesion.objects.order_by('-fecha_renovacion')[:5]
    
    context = {
        'intentos_fallidos_hoy': intentos_fallidos_hoy,
        'intentos_exitosos_hoy': intentos_exitosos_hoy,
        'cuentas_bloqueadas': cuentas_bloqueadas,
        'tokens_activos': tokens_activos,
        'operaciones_semana': operaciones_semana,
        'dias_exitosos': json.dumps(dias_exitosos),
        'dias_fallidos': json.dumps(dias_fallidos),
        'ultimos_bloqueos': ultimos_bloqueos,
        'top_ips_sospechosas': top_ips_sospechosas,
        'ultimas_operaciones': ultimas_operaciones,
        'anomalias_recientes': anomalias_recientes,
        'sesiones_activas_count': sesiones_activas_count,
        'stats_2fa': stats_2fa,
        'intentos_2fa_recientes': intentos_2fa_recientes,
        'renovaciones_recientes': renovaciones_recientes,
    }
    
    return render(request, 'seguridad/dashboard.html', context)


@login_required
def desbloquear_cuenta_view(request, bloqueo_id):
    """Desbloquear una cuenta manualmente"""
    
    if request.method == 'POST':
        try:
            bloqueo = BloqueoCuenta.objects.get(id_bloqueo=bloqueo_id)
            bloqueo.activo = False
            bloqueo.fecha_desbloqueo = timezone.now()
            bloqueo.save()
            
            messages.success(request, f'Cuenta {bloqueo.usuario} desbloqueada exitosamente')
        except BloqueoCuenta.DoesNotExist:
            messages.error(request, 'Bloqueo no encontrado')
    
    return redirect('pos:dashboard_seguridad')


@login_required
def logs_auditoria_view(request):
    """Vista detallada de logs de auditoría con filtros"""
    
    # Filtros
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    usuario = request.GET.get('usuario', '')
    operacion = request.GET.get('operacion', '')
    tipo_usuario = request.GET.get('tipo_usuario', '')
    resultado = request.GET.get('resultado', '')
    
    # Query base
    logs = AuditoriaOperacion.objects.all()
    
    # Aplicar filtros
    if fecha_desde:
        logs = logs.filter(fecha_operacion__date__gte=fecha_desde)
    if fecha_hasta:
        logs = logs.filter(fecha_operacion__date__lte=fecha_hasta)
    if usuario:
        logs = logs.filter(usuario__icontains=usuario)
    if operacion:
        logs = logs.filter(operacion=operacion)
    if tipo_usuario:
        logs = logs.filter(tipo_usuario=tipo_usuario)
    if resultado:
        logs = logs.filter(resultado=resultado)
    
    # Ordenar
    logs = logs.order_by('-fecha_operacion')
    
    # Operaciones únicas para filtro
    operaciones_disponibles = AuditoriaOperacion.objects.values_list(
        'operacion', flat=True
    ).distinct().order_by('operacion')
    
    context = {
        'logs': logs[:100],  # Limitar a 100 registros
        'total_logs': logs.count(),
        'operaciones_disponibles': operaciones_disponibles,
        'filtros': {
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'usuario': usuario,
            'operacion': operacion,
            'tipo_usuario': tipo_usuario,
            'resultado': resultado,
        }
    }
    
    return render(request, 'seguridad/logs_auditoria.html', context)


@login_required
def exportar_logs_view(request):
    """Exportar logs de auditoría a CSV"""
    
    # Obtener filtros del request
    fecha_desde = request.GET.get('fecha_desde', '')
    fecha_hasta = request.GET.get('fecha_hasta', '')
    usuario = request.GET.get('usuario', '')
    operacion = request.GET.get('operacion', '')
    
    # Query con filtros
    logs = AuditoriaOperacion.objects.all()
    
    if fecha_desde:
        logs = logs.filter(fecha_operacion__date__gte=fecha_desde)
    if fecha_hasta:
        logs = logs.filter(fecha_operacion__date__lte=fecha_hasta)
    if usuario:
        logs = logs.filter(usuario__icontains=usuario)
    if operacion:
        logs = logs.filter(operacion=operacion)
    
    logs = logs.order_by('-fecha_operacion')
    
    # Crear respuesta CSV
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="auditoria_logs_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    response.write('\ufeff'.encode('utf-8'))  # BOM para Excel
    
    writer = csv.writer(response)
    writer.writerow([
        'Fecha/Hora', 'Usuario', 'Tipo Usuario', 'Operación', 
        'Tabla Afectada', 'ID Registro', 'Descripción', 
        'IP Address', 'Resultado', 'Mensaje Error'
    ])
    
    for log in logs:
        writer.writerow([
            log.fecha_operacion.strftime('%Y-%m-%d %H:%M:%S'),
            log.usuario,
            log.tipo_usuario,
            log.operacion,
            log.tabla_afectada or '',
            log.id_registro or '',
            log.descripcion or '',
            log.ip_address or '',
            log.resultado,
            log.mensaje_error or ''
        ])
    
    return response


@login_required
def intentos_login_view(request):
    """Vista de intentos de login recientes"""
    
    # Filtros
    dias = int(request.GET.get('dias', 7))
    solo_fallidos = request.GET.get('solo_fallidos', '') == 'true'
    
    fecha_limite = timezone.now() - timedelta(days=dias)
    
    intentos = IntentoLogin.objects.filter(fecha_intento__gte=fecha_limite)
    
    if solo_fallidos:
        intentos = intentos.filter(exitoso=False)
    
    intentos = intentos.order_by('-fecha_intento')[:200]
    
    # Estadísticas
    total_intentos = intentos.count()
    intentos_exitosos = intentos.filter(exitoso=True).count()
    intentos_fallidos = intentos.filter(exitoso=False).count()
    
    context = {
        'intentos': intentos,
        'total_intentos': total_intentos,
        'intentos_exitosos': intentos_exitosos,
        'intentos_fallidos': intentos_fallidos,
        'dias': dias,
        'solo_fallidos': solo_fallidos,
    }
    
    return render(request, 'seguridad/intentos_login.html', context)
