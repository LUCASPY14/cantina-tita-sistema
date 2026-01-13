"""
Sistema de Notificaciones de Saldo
Cantina Tita - 2026
"""

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


def verificar_saldo_y_notificar(tarjeta):
    """
    Verifica el saldo de una tarjeta y envía notificaciones si es necesario
    
    Reglas:
    - SALDO_CRITICO: saldo < 0 (negativo)
    - SALDO_BAJO: 0 <= saldo < saldo_alerta
    - SALDO_OK: saldo >= saldo_alerta
    """
    from gestion.models import NotificacionSaldo, Cliente
    
    saldo = tarjeta.saldo_actual
    saldo_alerta = tarjeta.saldo_alerta or 10000  # Default ₲10,000
    
    # Obtener email del padre/responsable
    hijo = tarjeta.id_hijo
    cliente = hijo.id_cliente_responsable
    email_padre = None
    telefono_padre = None
    
    # Buscar email y teléfono en UsuariosWebClientes o UsuarioPortal
    try:
        from gestion.models import UsuariosWebClientes
        usuario_web = UsuariosWebClientes.objects.filter(
            id_cliente=cliente,
            activo=True
        ).first()
        if usuario_web:
            email_padre = usuario_web.email
            # Intentar obtener teléfono
            if hasattr(usuario_web, 'telefono_celular'):
                telefono_padre = usuario_web.telefono_celular
            elif hasattr(usuario_web, 'telefono'):
                telefono_padre = usuario_web.telefono
    except:
        pass
    
    # Determinar tipo de notificación
    tipo_notificacion = None
    mensaje = ""
    
    if saldo < 0:
        # Saldo NEGATIVO (crítico)
        tipo_notificacion = 'SALDO_NEGATIVO'
        mensaje = f"""
        🚨 ALERTA: Saldo Negativo
        
        La tarjeta de {hijo.nombre_completo} tiene saldo NEGATIVO.
        
        Tarjeta: {tarjeta.nro_tarjeta}
        Saldo Actual: ₲ {saldo:,}
        Adeuda: ₲ {abs(saldo):,}
        
        Por favor, realice una recarga lo antes posible para regularizar el saldo.
        El próximo pago se descontará automáticamente de la recarga.
        
        Gracias,
        Cantina Tita
        """
    elif saldo < saldo_alerta:
        # Saldo BAJO
        tipo_notificacion = 'SALDO_BAJO'
        mensaje = f"""
        ⚠️ Aviso: Saldo Bajo
        
        La tarjeta de {hijo.nombre_completo} tiene saldo bajo.
        
        Tarjeta: {tarjeta.nro_tarjeta}
        Saldo Actual: ₲ {saldo:,}
        Saldo de Alerta: ₲ {saldo_alerta:,}
        
        Le recomendamos realizar una recarga para evitar inconvenientes.
        
        Saludos,
        Cantina Tita
        """
    else:
        # Saldo OK, no notificar
        return None
    
    # Verificar si ya se envió notificación recientemente (evitar spam)
    if tarjeta.notificar_saldo_bajo and tarjeta.ultima_notificacion_saldo:
        tiempo_desde_ultima = timezone.now() - tarjeta.ultima_notificacion_saldo
        if tiempo_desde_ultima < timedelta(hours=24):
            # Ya se notificó hace menos de 24 horas
            return None
    
    # Crear notificación en BD
    notificacion = NotificacionSaldo.objects.create(
        nro_tarjeta=tarjeta,
        tipo_notificacion=tipo_notificacion,
        saldo_actual=saldo,
        mensaje=mensaje,
        email_destinatario=email_padre
    )
    
    # Enviar email si hay dirección
    if email_padre and settings.EMAIL_HOST:
        try:
            send_mail(
                subject=f'Cantina Tita - {tipo_notificacion.replace("_", " ").title()}',
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_padre],
                fail_silently=True  # No fallar si email falla
            )
            notificacion.enviada_email = True
            notificacion.fecha_envio = timezone.now()
            notificacion.save()
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
    
    # Enviar WhatsApp si hay teléfono y está configurado
    if telefono_padre and tarjeta.notificar_saldo_bajo:
        enviado_whatsapp = enviar_notificacion_whatsapp(
            telefono=telefono_padre,
            tipo=tipo_notificacion,
            tarjeta=tarjeta.nro_tarjeta,
            estudiante=hijo.nombre_completo,
            saldo=saldo
        )
        
        if enviado_whatsapp:
            notificacion.enviada_sms = True  # Usamos campo enviada_sms para WhatsApp
            notificacion.save()
    
    # Actualizar fecha de última notificación
    tarjeta.ultima_notificacion_saldo = timezone.now()
    tarjeta.save(update_fields=['ultima_notificacion_saldo'])
    
    return notificacion


def notificar_regularizacion_saldo(tarjeta, carga_saldo):
    """
    Notifica cuando se regulariza un saldo negativo
    """
    from gestion.models import NotificacionSaldo
    
    hijo = tarjeta.id_hijo
    cliente = hijo.id_cliente_responsable
    
    # Obtener email
    email_padre = None
    try:
        from gestion.models import UsuariosWebClientes
        usuario_web = UsuariosWebClientes.objects.filter(
            id_cliente=cliente,
            activo=True
        ).first()
        if usuario_web:
            email_padre = usuario_web.email
    except:
        pass
    
    mensaje = f"""
    ✅ Saldo Regularizado
    
    La tarjeta de {hijo.nombre_completo} ha sido regularizada.
    
    Tarjeta: {tarjeta.nro_tarjeta}
    Recarga: ₲ {carga_saldo.monto:,}
    Nuevo Saldo: ₲ {tarjeta.saldo_actual:,}
    
    Gracias por su pago.
    
    Cantina Tita
    """
    
    # Crear notificación
    notificacion = NotificacionSaldo.objects.create(
        nro_tarjeta=tarjeta,
        tipo_notificacion='REGULARIZADO',
        saldo_actual=tarjeta.saldo_actual,
        mensaje=mensaje,
        email_destinatario=email_padre
    )
    
    # Enviar email
    if email_padre and settings.EMAIL_HOST:
        try:
            send_mail(
                subject='Cantina Tita - Saldo Regularizado',
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_padre],
                fail_silently=True
            )
            notificacion.enviada_email = True
            notificacion.fecha_envio = timezone.now()
            notificacion.save()
        except:
            pass
    
    return notificacion


def obtener_notificaciones_pendientes(cliente):
    """
    Obtiene notificaciones no leídas para un cliente
    """
    from gestion.models import NotificacionSaldo, Hijo
    
    # Obtener tarjetas de los hijos del cliente
    hijos = Hijo.objects.filter(id_cliente_responsable=cliente)
    tarjetas = [hijo.tarjeta for hijo in hijos if hasattr(hijo, 'tarjeta')]
    
    # Obtener notificaciones no leídas
    notificaciones = NotificacionSaldo.objects.filter(
        nro_tarjeta__in=tarjetas,
        leida=False
    ).order_by('-fecha_creacion')
    
    return notificaciones


def enviar_notificacion_whatsapp(telefono, tipo, tarjeta, estudiante, saldo):
    """
    Enviar notificación de saldo por WhatsApp con botones de acción
    
    Args:
        telefono: Número de WhatsApp del padre
        tipo: Tipo de notificación (SALDO_BAJO, SALDO_NEGATIVO, etc.)
        tarjeta: Número de tarjeta
        estudiante: Nombre del estudiante
        saldo: Saldo actual
    
    Returns:
        bool: True si se envió correctamente
    """
    try:
        from gestion.whatsapp_client import WhatsAppWebClient
        
        # Crear cliente WhatsApp
        client = WhatsAppWebClient()
        
        # Verificar conexión
        if not client.check_status():
            logger.warning("WhatsApp no está conectado, saltando notificación")
            return False
        
        # Preparar mensaje según tipo
        if tipo == 'SALDO_BAJO':
            emoji = '⚠️'
            titulo = 'Saldo Bajo'
            descripcion = f'El saldo de la tarjeta está bajo. Le recomendamos recargar pronto.'
            urgencia = ''
        elif tipo == 'SALDO_NEGATIVO':
            emoji = '🚨'
            titulo = 'Saldo Negativo'
            descripcion = f'La tarjeta tiene saldo negativo. Por favor regularice a la brevedad.'
            urgencia = '\n⚠️ *URGENTE:* Regularice el saldo lo antes posible.'
        else:  # REGULARIZADO
            emoji = '✅'
            titulo = 'Saldo Regularizado'
            descripcion = f'El saldo de la tarjeta ha sido regularizado exitosamente.'
            urgencia = ''
        
        # Construir mensaje con formato WhatsApp
        mensaje = f"""{emoji} *{titulo} - Cantina Tita*

*Estudiante:* {estudiante}
*Tarjeta:* {tarjeta}
*Saldo Actual:* Gs. {saldo:,.0f}

{descripcion}{urgencia}

*Acciones disponibles:*
• 💳 Recargar ahora: {settings.SITE_URL}/portal/recargas/
• 📊 Ver movimientos: {settings.SITE_URL}/portal/
• 📞 Contactar cantina: {getattr(settings, 'CANTITA_WHATSAPP_CONTACTO', '+595981234567')}

_Este es un mensaje automático del sistema de gestión de Cantina Tita._"""
        
        # Enviar mensaje
        enviado = client.send_message(telefono, mensaje)
        
        if enviado:
            logger.info(f"✅ Notificación WhatsApp enviada a {telefono}: {tipo}")
        else:
            logger.warning(f"❌ No se pudo enviar WhatsApp a {telefono}")
        
        return enviado
        
    except Exception as e:
        logger.error(f"Error enviando notificación WhatsApp: {e}")
        return False

