"""
Sistema de Notificaciones - Cantina Tita
========================================

Módulo para envío de notificaciones por:
- Email (SMTP configurado)
- SMS (Tigo Paraguay, Personal)
- WhatsApp (whatsapp-web.js - GRATIS)

Funciones principales:
- enviar_email(): Envío genérico de emails
- enviar_sms(): Envío de SMS
- enviar_whatsapp(): Envío de mensajes WhatsApp (gratis)
- notificar_saldo_bajo(): Notificación multi-canal para saldo bajo
- notificar_recarga_exitosa(): Notificación de recarga exitosa
- notificar_cuenta_pendiente(): Notificación de cuenta pendiente

⚠️ WhatsApp usa servidor local whatsapp-web.js (costo $0)
   Solo usar con número secundario para evitar ban
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from gestion.models import SolicitudesNotificacion, AlertasSistema
from gestion.whatsapp_client import whatsapp_client
import logging

logger = logging.getLogger(__name__)


# ==================== CONFIGURACIÓN ====================

# SMS Providers
SMS_PROVIDER = getattr(settings, 'SMS_PROVIDER', 'tigo')  # 'tigo', 'personal'

# WhatsApp Provider
WHATSAPP_PROVIDER = getattr(settings, 'WHATSAPP_PROVIDER', 'whatsapp-web-js')  # 'whatsapp-web-js', 'business_api'


# ==================== EMAIL ====================

def enviar_email(destinatario, asunto, mensaje, html_mensaje=None, archivo_adjunto=None):
    """
    Envía un email usando Django send_mail
    
    Args:
        destinatario (str): Email del destinatario
        asunto (str): Asunto del email
        mensaje (str): Mensaje en texto plano
        html_mensaje (str, optional): Mensaje en HTML
        archivo_adjunto (str, optional): Ruta al archivo adjunto
        
    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    try:
        if html_mensaje:
            email = EmailMultiAlternatives(
                asunto,
                mensaje,
                settings.EMAIL_HOST_USER,
                [destinatario]
            )
            email.attach_alternative(html_mensaje, "text/html")
            
            if archivo_adjunto:
                email.attach_file(archivo_adjunto)
                
            email.send()
        else:
            send_mail(
                asunto,
                mensaje,
                settings.EMAIL_HOST_USER,
                [destinatario],
                fail_silently=False
            )
        
        logger.info(f"Email enviado exitosamente a {destinatario}: {asunto}")
        return True
        
    except Exception as e:
        logger.error(f"Error al enviar email a {destinatario}: {str(e)}")
        return False


def enviar_email_saldo_bajo(tarjeta):
    """
    Envía notificación de saldo bajo por email
    
    Args:
        tarjeta (Tarjeta): Instancia de Tarjeta con saldo bajo
        
    Returns:
        bool: True si se envió correctamente
    """
    try:
        responsable = tarjeta.id_hijo.id_cliente_responsable
        hijo = tarjeta.id_hijo
        
        if not responsable.email:
            logger.warning(f"Cliente {responsable.id_cliente} no tiene email configurado")
            return False
        
        # Contexto para el template
        context = {
            'responsable': responsable,
            'hijo': hijo,
            'tarjeta': tarjeta,
            'saldo_actual': tarjeta.saldo_actual,
            'fecha': timezone.now(),
        }
        
        # Renderizar templates
        html_mensaje = render_to_string('emails/saldo_bajo.html', context)
        texto_plano = strip_tags(html_mensaje)
        
        asunto = f"Saldo Bajo - Tarjeta {tarjeta.nro_tarjeta}"
        
        return enviar_email(
            responsable.email,
            asunto,
            texto_plano,
            html_mensaje
        )
        
    except Exception as e:
        logger.error(f"Error al enviar email saldo bajo para tarjeta {tarjeta.nro_tarjeta}: {str(e)}")
        return False


def enviar_email_recarga_exitosa(recarga):
    """
    Envía notificación de recarga exitosa por email
    
    Args:
        recarga (Recargas): Instancia de Recargas
        
    Returns:
        bool: True si se envió correctamente
    """
    try:
        tarjeta = recarga.nro_tarjeta
        responsable = tarjeta.id_hijo.id_cliente_responsable
        
        if not responsable.email:
            return False
        
        context = {
            'responsable': responsable,
            'recarga': recarga,
            'tarjeta': tarjeta,
            'fecha': timezone.now(),
        }
        
        html_mensaje = render_to_string('emails/recarga_exitosa.html', context)
        texto_plano = strip_tags(html_mensaje)
        
        asunto = f"Recarga Exitosa - Gs. {recarga.monto:,.0f}"
        
        return enviar_email(
            responsable.email,
            asunto,
            texto_plano,
            html_mensaje
        )
        
    except Exception as e:
        logger.error(f"Error al enviar email recarga exitosa: {str(e)}")
        return False


def enviar_email_cuenta_pendiente(cliente):
    """
    Envía notificación de cuenta pendiente por email
    
    Args:
        cliente (Cliente): Instancia de Cliente con cuenta pendiente
        
    Returns:
        bool: True si se envió correctamente
    """
    try:
        if not cliente.email:
            return False
        
        # Calcular saldo deudor
        from gestion.cuenta_corriente import calcular_saldo_cliente
        saldo = calcular_saldo_cliente(cliente)
        
        if saldo >= 0:
            return False  # No hay deuda
        
        context = {
            'cliente': cliente,
            'saldo_deudor': abs(saldo),
            'fecha': timezone.now(),
        }
        
        html_mensaje = render_to_string('emails/cuenta_pendiente.html', context)
        texto_plano = strip_tags(html_mensaje)
        
        asunto = f"Cuenta Pendiente - Gs. {abs(saldo):,.0f}"
        
        return enviar_email(
            cliente.email,
            asunto,
            texto_plano,
            html_mensaje
        )
        
    except Exception as e:
        logger.error(f"Error al enviar email cuenta pendiente: {str(e)}")
        return False


# ==================== SMS ====================

def enviar_sms_tigo(telefono, mensaje):
    """
    Envía SMS usando API de Tigo Paraguay
    
    Args:
        telefono (str): Número de teléfono (0981234567)
        mensaje (str): Mensaje a enviar
        
    Returns:
        bool: True si se envió correctamente
    """
    try:
        import requests
        
        api_key = getattr(settings, 'TIGO_SMS_API_KEY', None)
        api_url = getattr(settings, 'TIGO_SMS_API_URL', 'https://api.tigo.com.py/sms/send')
        
        if not api_key:
            logger.error("API Key de Tigo no configurada")
            return False
        
        payload = {
            'api_key': api_key,
            'to': telefono,
            'message': mensaje
        }
        
        response = requests.post(api_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"SMS Tigo enviado a {telefono}")
            return True
        else:
            logger.error(f"Error Tigo API: {response.status_code} - {response.text}")
            return False
        
    except Exception as e:
        logger.error(f"Error al enviar SMS Tigo a {telefono}: {str(e)}")
        return False


def enviar_sms_personal(telefono, mensaje):
    """
    Envía SMS usando API de Personal Paraguay
    
    Args:
        telefono (str): Número de teléfono (0982234567)
        mensaje (str): Mensaje a enviar
        
    Returns:
        bool: True si se envió correctamente
    """
    try:
        import requests
        
        api_key = getattr(settings, 'PERSONAL_SMS_API_KEY', None)
        api_url = getattr(settings, 'PERSONAL_SMS_API_URL', 'https://api.personal.com.py/sms')
        
        if not api_key:
            logger.error("API Key de Personal no configurada")
            return False
        
        payload = {
            'apikey': api_key,
            'phone': telefono,
            'text': mensaje
        }
        
        response = requests.post(api_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"SMS Personal enviado a {telefono}")
            return True
        else:
            logger.error(f"Error Personal API: {response.status_code}")
            return False
        
    except Exception as e:
        logger.error(f"Error al enviar SMS Personal a {telefono}: {str(e)}")
        return False


def enviar_sms(telefono, mensaje):
    """
    Envía SMS usando el proveedor configurado
    
    Args:
        telefono (str): Número de teléfono
        mensaje (str): Mensaje a enviar
        
    Returns:
        bool: True si se envió correctamente
    """
    # Normalizar teléfono a formato internacional
    if telefono.startswith('0'):
        telefono = '+595' + telefono[1:]
    elif not telefono.startswith('+'):
        telefono = '+595' + telefono
    
    if SMS_PROVIDER == 'tigo':
        return enviar_sms_tigo(telefono, mensaje)
    elif SMS_PROVIDER == 'personal':
        return enviar_sms_personal(telefono, mensaje)
    else:
        logger.error(f"Proveedor SMS desconocido: {SMS_PROVIDER}")
        return False


# ==================== WHATSAPP ====================

def enviar_whatsapp_web_js(telefono, mensaje):
    """
    Envía mensaje WhatsApp usando servidor whatsapp-web.js (GRATIS)
    
    ⚠️ NO OFICIAL - Solo usar con número secundario
    Costo: $0
    Requiere: Servidor Node.js corriendo en localhost:3000
    
    Args:
        telefono (str): Número de teléfono (+595981234567)
        mensaje (str): Mensaje a enviar
        
    Returns:
        bool: True si se envió correctamente
    """
    try:
        return whatsapp_client.send_message(telefono, mensaje)
    except Exception as e:
        logger.error(f"Error al enviar WhatsApp (whatsapp-web.js): {str(e)}")
        return False


def enviar_whatsapp_template(telefono, template_name, params):
    """
    Envía mensaje WhatsApp usando template predefinido
    
    Templates disponibles:
    - 'saldo_bajo': Notificación de saldo bajo
    - 'recarga_exitosa': Confirmación de recarga
    - 'cuenta_pendiente': Recordatorio de cuenta pendiente
    - 'compra_realizada': Confirmación de compra
    
    Args:
        telefono (str): Número de teléfono (+595981234567)
        template_name (str): Nombre del template
        params (dict): Parámetros del template
        
    Returns:
        bool: True si se envió correctamente
    """
    try:
        return whatsapp_client.send_template(telefono, template_name, params)
    except Exception as e:
        logger.error(f"Error al enviar WhatsApp template: {str(e)}")
        return False


def enviar_whatsapp_business_api(telefono, mensaje):
    """
    Envía mensaje WhatsApp usando Business API oficial (Meta)
    
    ⚠️ Requiere cuenta Business verificada
    Costo: ~$0.006/mensaje
    
    Args:
        telefono (str): Número de teléfono (+595981234567)
        mensaje (str): Mensaje a enviar
        
    Returns:
        bool: True si se envió correctamente
    """
    try:
        import requests
        
        access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', None)
        phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', None)
        
        if not all([access_token, phone_number_id]):
            logger.error("Configuración de WhatsApp Business API incompleta")
            return False
        
        url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": telefono.replace('+', ''),
            "type": "text",
            "text": {"body": mensaje}
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"WhatsApp Business API enviado a {telefono}")
            return True
        else:
            logger.error(f"Error WhatsApp API: {response.status_code} - {response.text}")
            return False
        
    except Exception as e:
        logger.error(f"Error al enviar WhatsApp Business API: {str(e)}")
        return False


def enviar_whatsapp(telefono, mensaje):
    """
    Envía mensaje WhatsApp usando el proveedor configurado
    
    Proveedores disponibles:
    - 'whatsapp-web-js': Servidor local GRATIS (recomendado)
    - 'business_api': Meta Business API oficial (pago)
    
    Args:
        telefono (str): Número de teléfono
        mensaje (str): Mensaje a enviar
        
    Returns:
        bool: True si se envió correctamente
    """
    # Normalizar teléfono
    if telefono.startswith('0'):
        telefono = '+595' + telefono[1:]
    elif not telefono.startswith('+'):
        telefono = '+595' + telefono
    
    if WHATSAPP_PROVIDER == 'whatsapp-web-js':
        return enviar_whatsapp_web_js(telefono, mensaje)
    elif WHATSAPP_PROVIDER == 'business_api':
        return enviar_whatsapp_business_api(telefono, mensaje)
    else:
        logger.error(f"Proveedor WhatsApp desconocido: {WHATSAPP_PROVIDER}")
        return False


# ==================== NOTIFICACIONES MULTI-CANAL ====================

def notificar_saldo_bajo(tarjeta, canales=['email']):
    """
    Notifica saldo bajo en los canales especificados
    
    Args:
        tarjeta (Tarjeta): Instancia de Tarjeta con saldo bajo
        canales (list): Lista de canales ['email', 'sms', 'whatsapp']
        
    Returns:
        dict: Resultado de cada canal {'email': True, 'sms': False, ...}
    """
    resultados = {}
    
    try:
        responsable = tarjeta.id_hijo.id_cliente_responsable
        hijo = tarjeta.id_hijo
        
        # Mensaje genérico
        mensaje_corto = (
            f"Saldo Bajo - Tarjeta {tarjeta.nro_tarjeta}\n"
            f"Estudiante: {hijo.nombre} {hijo.apellido}\n"
            f"Saldo: Gs. {tarjeta.saldo_actual:,.0f}\n"
            f"Por favor recargue para evitar inconvenientes."
        )
        
        # Enviar por cada canal
        if 'email' in canales and responsable.email:
            resultados['email'] = enviar_email_saldo_bajo(tarjeta)
        
        if 'sms' in canales and responsable.telefono:
            resultados['sms'] = enviar_sms(responsable.telefono, mensaje_corto)
        
        if 'whatsapp' in canales and responsable.telefono:
            resultados['whatsapp'] = enviar_whatsapp(responsable.telefono, mensaje_corto)
        
        # Registrar en SolicitudesNotificacion
        for canal, exito in resultados.items():
            SolicitudesNotificacion.objects.create(
                id_cliente=responsable,
                nro_tarjeta=tarjeta,
                saldo_alerta=tarjeta.saldo_actual,
                mensaje=mensaje_corto,
                destino=canal.upper() if canal != 'whatsapp' else 'WhatsApp',
                estado='Enviada' if exito else 'Fallida'
            )
        
        logger.info(f"Notificación saldo bajo enviada para tarjeta {tarjeta.nro_tarjeta}: {resultados}")
        
    except Exception as e:
        logger.error(f"Error en notificar_saldo_bajo: {str(e)}")
        resultados['error'] = str(e)
    
    return resultados


def notificar_recarga_exitosa(recarga, canales=['email']):
    """
    Notifica recarga exitosa en los canales especificados
    
    Args:
        recarga (Recargas): Instancia de Recargas
        canales (list): Lista de canales ['email', 'sms', 'whatsapp']
        
    Returns:
        dict: Resultado de cada canal
    """
    resultados = {}
    
    try:
        tarjeta = recarga.nro_tarjeta
        responsable = tarjeta.id_hijo.id_cliente_responsable
        
        mensaje_corto = (
            f"Recarga Exitosa\n"
            f"Tarjeta: {tarjeta.nro_tarjeta}\n"
            f"Monto: Gs. {recarga.monto:,.0f}\n"
            f"Nuevo saldo: Gs. {tarjeta.saldo_actual:,.0f}"
        )
        
        if 'email' in canales and responsable.email:
            resultados['email'] = enviar_email_recarga_exitosa(recarga)
        
        if 'sms' in canales and responsable.telefono:
            resultados['sms'] = enviar_sms(responsable.telefono, mensaje_corto)
        
        if 'whatsapp' in canales and responsable.telefono:
            resultados['whatsapp'] = enviar_whatsapp(responsable.telefono, mensaje_corto)
        
        logger.info(f"Notificación recarga exitosa: {resultados}")
        
    except Exception as e:
        logger.error(f"Error en notificar_recarga_exitosa: {str(e)}")
        resultados['error'] = str(e)
    
    return resultados


def notificar_cuenta_pendiente(cliente, canales=['email']):
    """
    Notifica cuenta pendiente en los canales especificados
    
    Args:
        cliente (Cliente): Instancia de Cliente con deuda
        canales (list): Lista de canales ['email', 'sms', 'whatsapp']
        
    Returns:
        dict: Resultado de cada canal
    """
    resultados = {}
    
    try:
        from gestion.cuenta_corriente import calcular_saldo_cliente
        saldo = calcular_saldo_cliente(cliente)
        
        if saldo >= 0:
            logger.info(f"Cliente {cliente.id_cliente} no tiene deuda")
            return resultados
        
        deuda = abs(saldo)
        
        mensaje_corto = (
            f"Cuenta Pendiente\n"
            f"Cliente: {cliente.apellidos}, {cliente.nombres}\n"
            f"Saldo deudor: Gs. {deuda:,.0f}\n"
            f"Por favor regularice su cuenta."
        )
        
        if 'email' in canales and cliente.email:
            resultados['email'] = enviar_email_cuenta_pendiente(cliente)
        
        if 'sms' in canales and cliente.telefono:
            resultados['sms'] = enviar_sms(cliente.telefono, mensaje_corto)
        
        if 'whatsapp' in canales and cliente.telefono:
            resultados['whatsapp'] = enviar_whatsapp(cliente.telefono, mensaje_corto)
        
        logger.info(f"Notificación cuenta pendiente enviada a cliente {cliente.id_cliente}: {resultados}")
        
    except Exception as e:
        logger.error(f"Error en notificar_cuenta_pendiente: {str(e)}")
        resultados['error'] = str(e)
    
    return resultados
