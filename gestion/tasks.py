"""
Tareas asíncronas de Celery para Cantina Tita

Este módulo contiene todas las tareas programadas y asíncronas
que se ejecutan en background.

Autor: CantiTita
Fecha: 2026-01-12
"""

from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from datetime import timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


@shared_task(name='recordatorios_deuda_saldo_negativo')
def tarea_recordatorios_deuda():
    """
    Enviar recordatorios automáticos de deuda a padres
    
    Escalamiento:
    - 3 días: Recordatorio amable
    - 7 días: Recordatorio urgente
    - 15 días: Advertencia de bloqueo
    
    Se ejecuta diariamente a las 08:00
    """
    from gestion.models import AutorizacionSaldoNegativo, Tarjeta, UsuariosWebClientes, NotificacionSaldo
    
    logger.info("🔔 Iniciando tarea de recordatorios de deuda...")
    
    hoy = timezone.now()
    recordatorios_enviados = {
        '3_dias': 0,
        '7_dias': 0,
        '15_dias': 0
    }
    
    # Buscar autorizaciones pendientes
    autorizaciones_pendientes = AutorizacionSaldoNegativo.objects.filter(
        regularizado=False
    ).select_related('nro_tarjeta')
    
    for auth in autorizaciones_pendientes:
        dias_deuda = (hoy - auth.fecha_autorizacion).days
        
        # Determinar tipo de recordatorio
        tipo_recordatorio = None
        if dias_deuda == 3:
            tipo_recordatorio = 'amable'
            key = '3_dias'
        elif dias_deuda == 7:
            tipo_recordatorio = 'urgente'
            key = '7_dias'
        elif dias_deuda == 15:
            tipo_recordatorio = 'critico'
            key = '15_dias'
        
        if tipo_recordatorio:
            # Buscar email del padre
            try:
                hijo = auth.nro_tarjeta.id_hijo
                if not hijo:
                    continue
                
                cliente = hijo.id_cliente
                if not cliente:
                    continue
                
                usuario_web = UsuariosWebClientes.objects.filter(
                    id_cliente=cliente
                ).first()
                
                if not usuario_web or not usuario_web.correo_electronico:
                    logger.warning(f"No hay email para tarjeta {auth.nro_tarjeta}")
                    continue
                
                # Enviar recordatorio
                enviado = enviar_recordatorio_deuda(
                    auth=auth,
                    email_destino=usuario_web.correo_electronico,
                    tipo=tipo_recordatorio,
                    dias_deuda=dias_deuda
                )
                
                if enviado:
                    recordatorios_enviados[key] += 1
                    logger.info(f"✅ Recordatorio {tipo_recordatorio} enviado: {auth.nro_tarjeta} ({dias_deuda} días)")
                
            except Exception as e:
                logger.error(f"Error enviando recordatorio para {auth.nro_tarjeta}: {e}")
                continue
    
    # Bloquear tarjetas con deuda > 15 días
    bloqueadas = bloquear_tarjetas_morosidad()
    
    logger.info(f"""
    ✅ Tarea de recordatorios completada:
    - Recordatorios 3 días: {recordatorios_enviados['3_dias']}
    - Recordatorios 7 días: {recordatorios_enviados['7_dias']}
    - Advertencias 15 días: {recordatorios_enviados['15_dias']}
    - Tarjetas bloqueadas: {bloqueadas}
    """)
    
    return recordatorios_enviados


def enviar_recordatorio_deuda(auth, email_destino, tipo, dias_deuda):
    """Enviar email de recordatorio según tipo"""
    
    tarjeta = auth.nro_tarjeta
    estudiante = auth.estudiante_nombre
    monto_deuda = auth.monto_autorizado
    
    # Configurar mensaje según tipo
    if tipo == 'amable':
        asunto = f"Recordatorio: Saldo Pendiente - Tarjeta {tarjeta}"
        template = 'emails/recordatorio_deuda_amable.html'
        urgencia = 'RECORDATORIO'
    elif tipo == 'urgente':
        asunto = f"⚠️ URGENTE: Saldo Pendiente - Tarjeta {tarjeta}"
        template = 'emails/recordatorio_deuda_urgente.html'
        urgencia = 'URGENTE'
    else:  # critico
        asunto = f"🚨 CRÍTICO: Bloqueo Inminente - Tarjeta {tarjeta}"
        template = 'emails/recordatorio_deuda_critico.html'
        urgencia = 'CRÍTICO'
    
    # Contexto para template
    contexto = {
        'tarjeta': tarjeta,
        'estudiante': estudiante,
        'monto_deuda': monto_deuda,
        'dias_deuda': dias_deuda,
        'fecha_autorizacion': auth.fecha_autorizacion,
        'urgencia': urgencia,
        'url_recarga': f"{settings.SITE_URL}/portal/recargas/",
    }
    
    try:
        # Renderizar HTML
        html_message = render_to_string(template, contexto)
        
        # Enviar email
        send_mail(
            subject=asunto,
            message=f"Deuda pendiente: Gs. {monto_deuda:,.0f}. Por favor ingrese al portal para recargar.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email_destino],
            html_message=html_message,
            fail_silently=False
        )
        
        # Registrar notificación
        from gestion.models import NotificacionSaldo
        NotificacionSaldo.objects.create(
            nro_tarjeta=tarjeta,
            tipo='SALDO_NEGATIVO',
            mensaje=f"Recordatorio {urgencia}: Deuda de Gs. {monto_deuda:,.0f} por {dias_deuda} días",
            saldo_monto=tarjeta.saldo_actual,
            enviada_email=True,
            email_destino=email_destino
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Error enviando recordatorio: {e}")
        return False


def bloquear_tarjetas_morosidad():
    """Bloquear tarjetas con deuda mayor a 15 días"""
    from gestion.models import AutorizacionSaldoNegativo, Tarjeta, UsuariosWebClientes
    
    hoy = timezone.now()
    fecha_limite = hoy - timedelta(days=15)
    bloqueadas = 0
    
    # Buscar deudas viejas
    deudas_criticas = AutorizacionSaldoNegativo.objects.filter(
        regularizado=False,
        fecha_autorizacion__lte=fecha_limite
    ).select_related('nro_tarjeta')
    
    for auth in deudas_criticas:
        tarjeta = auth.nro_tarjeta
        
        # Verificar si ya está bloqueada
        if tarjeta.estado == 'Bloqueada':
            continue
        
        # Bloquear tarjeta
        tarjeta.estado = 'Bloqueada'
        tarjeta.save()
        
        bloqueadas += 1
        logger.warning(f"🔒 Tarjeta bloqueada por morosidad: {tarjeta}")
        
        # Enviar notificación de bloqueo
        try:
            hijo = tarjeta.id_hijo
            if hijo and hijo.id_cliente:
                usuario_web = UsuariosWebClientes.objects.filter(
                    id_cliente=hijo.id_cliente
                ).first()
                
                if usuario_web and usuario_web.correo_electronico:
                    enviar_notificacion_bloqueo(
                        tarjeta=tarjeta,
                        email=usuario_web.correo_electronico,
                        dias_deuda=(hoy - auth.fecha_autorizacion).days
                    )
        except Exception as e:
            logger.error(f"Error enviando notificación de bloqueo: {e}")
    
    return bloqueadas


def enviar_notificacion_bloqueo(tarjeta, email, dias_deuda):
    """Enviar email notificando bloqueo de tarjeta"""
    
    asunto = f"🔒 TARJETA BLOQUEADA - {tarjeta}"
    
    contexto = {
        'tarjeta': tarjeta,
        'dias_deuda': dias_deuda,
        'url_contacto': f"{settings.SITE_URL}/portal/contacto/",
    }
    
    html_message = render_to_string('emails/tarjeta_bloqueada.html', contexto)
    
    send_mail(
        subject=asunto,
        message=f"Su tarjeta {tarjeta} ha sido bloqueada por morosidad de {dias_deuda} días.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        html_message=html_message,
        fail_silently=True
    )


@shared_task(name='limpieza_notificaciones_antiguas')
def tarea_limpieza_notificaciones():
    """
    Limpiar notificaciones antiguas (> 90 días)
    
    Se ejecuta semanalmente los domingos a las 02:00
    """
    from gestion.models import NotificacionSaldo
    
    logger.info("🧹 Limpiando notificaciones antiguas...")
    
    fecha_limite = timezone.now() - timedelta(days=90)
    
    eliminadas = NotificacionSaldo.objects.filter(
        fecha_creacion__lt=fecha_limite,
        leida=True
    ).delete()[0]
    
    logger.info(f"✅ Notificaciones eliminadas: {eliminadas}")
    return eliminadas


@shared_task(name='verificar_saldos_bajos_diario')
def tarea_verificar_saldos_bajos():
    """
    Verificar tarjetas con saldo bajo y enviar notificaciones
    
    Se ejecuta diariamente a las 20:00
    """
    from gestion.models import Tarjeta
    from gestion.notificaciones_saldo import verificar_saldo_y_notificar
    
    logger.info("📊 Verificando saldos bajos...")
    
    # Tarjetas activas con notificaciones habilitadas
    tarjetas = Tarjeta.objects.filter(
        estado='Activa',
        notificar_saldo_bajo=True
    )
    
    notificaciones_enviadas = 0
    
    for tarjeta in tarjetas:
        try:
            enviada = verificar_saldo_y_notificar(tarjeta)
            if enviada:
                notificaciones_enviadas += 1
        except Exception as e:
            logger.error(f"Error verificando saldo de {tarjeta}: {e}")
    
    logger.info(f"✅ Notificaciones de saldo bajo enviadas: {notificaciones_enviadas}")
    return notificaciones_enviadas


@shared_task(name='generar_reporte_diario_gerencia')
def tarea_reporte_diario_gerencia():
    """
    Generar y enviar reporte diario a gerencia
    
    Incluye:
    - Ventas del día
    - Recargas del día
    - Autorizaciones de saldo negativo
    - Saldos críticos
    
    Se ejecuta diariamente a las 21:00
    """
    from gestion.models import Venta, CargaSaldo, AutorizacionSaldoNegativo, Tarjeta
    from django.db.models import Sum, Count
    
    logger.info("📧 Generando reporte diario para gerencia...")
    
    hoy = timezone.now().date()
    
    # Estadísticas del día
    ventas_hoy = Venta.objects.filter(fecha_venta__date=hoy)
    recargas_hoy = CargaSaldo.objects.filter(fecha_carga__date=hoy)
    autorizaciones_hoy = AutorizacionSaldoNegativo.objects.filter(fecha_autorizacion__date=hoy)
    
    total_ventas = ventas_hoy.aggregate(Sum('monto_total'))['monto_total__sum'] or 0
    total_recargas = recargas_hoy.aggregate(Sum('monto'))['monto__sum'] or 0
    count_ventas = ventas_hoy.count()
    count_recargas = recargas_hoy.count()
    count_autorizaciones = autorizaciones_hoy.count()
    
    # Saldos críticos
    saldos_negativos = Tarjeta.objects.filter(
        saldo_actual__lt=0,
        estado='Activa'
    ).count()
    
    # Email a gerencia
    contexto = {
        'fecha': hoy,
        'total_ventas': total_ventas,
        'count_ventas': count_ventas,
        'total_recargas': total_recargas,
        'count_recargas': count_recargas,
        'count_autorizaciones': count_autorizaciones,
        'saldos_negativos': saldos_negativos,
    }
    
    html_message = render_to_string('emails/reporte_diario_gerencia.html', contexto)
    
    send_mail(
        subject=f"📊 Reporte Diario Cantina - {hoy.strftime('%d/%m/%Y')}",
        message=f"Ventas: Gs. {total_ventas:,.0f} | Recargas: Gs. {total_recargas:,.0f}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.GERENCIA_EMAIL],
        html_message=html_message,
        fail_silently=True
    )
    
    logger.info("✅ Reporte diario enviado a gerencia")
    
    return {
        'ventas': count_ventas,
        'recargas': count_recargas,
        'autorizaciones': count_autorizaciones
    }
