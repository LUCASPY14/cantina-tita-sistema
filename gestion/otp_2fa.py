"""
Sistema de autenticación de dos factores (2FA) con OTP

Este módulo provee autenticación de dos factores usando códigos OTP
para autorizaciones de alto monto (> Gs. 100.000).

El código se envía por WhatsApp o SMS y tiene validez de 5 minutos.

Instalación:
    pip install pyotp qrcode

Autor: CantiTita
Fecha: 2026-01-12
"""

import pyotp
import qrcode
import io
import base64
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

# Configuración
OTP_VALIDITY_MINUTES = 5
OTP_LENGTH = 6
CACHE_TIMEOUT_OTP = 300  # 5 minutos


def generar_codigo_otp(supervisor_id, tarjeta, monto):
    """
    Generar código OTP de 6 dígitos para autorización
    
    Args:
        supervisor_id: ID del supervisor que autoriza
        tarjeta: Número de tarjeta
        monto: Monto a autorizar
    
    Returns:
        str con código OTP (6 dígitos)
    """
    try:
        # Generar código usando TOTP
        totp = pyotp.TOTP(
            pyotp.random_base32(),
            digits=OTP_LENGTH,
            interval=OTP_VALIDITY_MINUTES * 60
        )
        
        codigo = totp.now()
        
        # Guardar en cache para validación
        cache_key = f'otp:{supervisor_id}:{tarjeta}:{monto}'
        cache_data = {
            'codigo': codigo,
            'supervisor_id': supervisor_id,
            'tarjeta': str(tarjeta),
            'monto': float(monto),
            'timestamp': timezone.now().isoformat(),
            'usado': False
        }
        
        cache.set(cache_key, cache_data, CACHE_TIMEOUT_OTP)
        
        logger.info(f"🔐 OTP generado para supervisor {supervisor_id}: {codigo}")
        
        return codigo
        
    except Exception as e:
        logger.error(f"Error generando OTP: {e}")
        return None


def validar_codigo_otp(supervisor_id, tarjeta, monto, codigo_ingresado):
    """
    Validar código OTP ingresado
    
    Args:
        supervisor_id: ID del supervisor
        tarjeta: Número de tarjeta
        monto: Monto de la autorización
        codigo_ingresado: Código que ingresó el usuario
    
    Returns:
        tuple (bool, str): (es_valido, mensaje_error)
    """
    try:
        # Buscar en cache
        cache_key = f'otp:{supervisor_id}:{tarjeta}:{monto}'
        cache_data = cache.get(cache_key)
        
        if not cache_data:
            return False, "Código OTP expirado o inválido. Solicite uno nuevo."
        
        # Verificar si ya fue usado
        if cache_data.get('usado', False):
            return False, "Este código OTP ya fue utilizado."
        
        # Validar código
        if cache_data['codigo'] != codigo_ingresado:
            return False, "Código OTP incorrecto."
        
        # Marcar como usado
        cache_data['usado'] = True
        cache.set(cache_key, cache_data, CACHE_TIMEOUT_OTP)
        
        logger.info(f"✅ OTP validado correctamente para supervisor {supervisor_id}")
        
        return True, ""
        
    except Exception as e:
        logger.error(f"Error validando OTP: {e}")
        return False, f"Error al validar código: {str(e)}"


def enviar_otp_whatsapp(telefono, codigo, estudiante_nombre, monto):
    """
    Enviar código OTP por WhatsApp
    
    Args:
        telefono: Número de WhatsApp del supervisor
        codigo: Código OTP generado
        estudiante_nombre: Nombre del estudiante
        monto: Monto de la autorización
    
    Returns:
        bool: True si se envió correctamente
    """
    try:
        from gestion.whatsapp_client import WhatsAppWebClient
        
        # Crear cliente WhatsApp
        client = WhatsAppWebClient()
        
        # Mensaje
        mensaje = f"""🔐 *CÓDIGO DE AUTORIZACIÓN*

*Estudiante:* {estudiante_nombre}
*Monto:* Gs. {monto:,.0f}

*Tu código OTP:* `{codigo}`

⏰ Este código es válido por {OTP_VALIDITY_MINUTES} minutos.
🔒 NO compartas este código con nadie.

_Cantina Tita - Sistema de Seguridad_"""
        
        # Enviar
        enviado = client.send_message(telefono, mensaje)
        
        if enviado:
            logger.info(f"✅ OTP enviado por WhatsApp a {telefono}")
        else:
            logger.error(f"❌ Error enviando OTP por WhatsApp a {telefono}")
        
        return enviado
        
    except Exception as e:
        logger.error(f"Error enviando OTP por WhatsApp: {e}")
        return False


def enviar_otp_sms(telefono, codigo, estudiante_nombre, monto):
    """
    Enviar código OTP por SMS
    
    Args:
        telefono: Número de teléfono del supervisor
        codigo: Código OTP generado
        estudiante_nombre: Nombre del estudiante
        monto: Monto de la autorización
    
    Returns:
        bool: True si se envió correctamente
    """
    try:
        # TODO: Implementar integración con proveedor SMS (Tigo/Personal)
        # Por ahora solo log
        mensaje = f"CantinaTita - Codigo OTP: {codigo} para autorizar Gs. {monto:,.0f}. Valido {OTP_VALIDITY_MINUTES} min."
        
        logger.info(f"📱 OTP SMS a {telefono}: {mensaje}")
        
        # Aquí iría la integración real con API de SMS
        # return enviar_sms_tigo(telefono, mensaje)
        
        return False  # Por defecto False hasta implementar
        
    except Exception as e:
        logger.error(f"Error enviando OTP por SMS: {e}")
        return False


def requiere_otp(monto):
    """
    Determinar si el monto requiere autenticación 2FA
    
    Args:
        monto: Monto de la autorización (Decimal o float)
    
    Returns:
        bool: True si requiere OTP
    """
    from decimal import Decimal
    
    MONTO_MINIMO_OTP = Decimal('100000')  # Gs. 100.000
    
    return Decimal(str(monto)) >= MONTO_MINIMO_OTP


def obtener_telefono_supervisor(supervisor):
    """
    Obtener teléfono del supervisor para envío de OTP
    
    Args:
        supervisor: Instancia de Empleado
    
    Returns:
        str con teléfono o None
    """
    try:
        # Buscar en modelo Empleado
        if hasattr(supervisor, 'telefono_celular') and supervisor.telefono_celular:
            return supervisor.telefono_celular
        
        if hasattr(supervisor, 'telefono') and supervisor.telefono:
            return supervisor.telefono
        
        logger.warning(f"No se encontró teléfono para supervisor {supervisor.id}")
        return None
        
    except Exception as e:
        logger.error(f"Error obteniendo teléfono supervisor: {e}")
        return None


def solicitar_otp_autorizacion(supervisor_id, tarjeta, estudiante_nombre, monto):
    """
    Generar y enviar OTP para autorización de alto monto
    
    Args:
        supervisor_id: ID del supervisor
        tarjeta: Número de tarjeta
        estudiante_nombre: Nombre del estudiante
        monto: Monto a autorizar
    
    Returns:
        dict con resultado: {success, codigo (solo debug), mensaje, metodo_envio}
    """
    try:
        from gestion.models import Empleado
        
        # Buscar supervisor
        supervisor = Empleado.objects.get(id=supervisor_id)
        
        # Generar código
        codigo = generar_codigo_otp(supervisor_id, tarjeta, monto)
        
        if not codigo:
            return {
                'success': False,
                'mensaje': 'Error al generar código OTP',
                'metodo_envio': None
            }
        
        # Obtener teléfono
        telefono = obtener_telefono_supervisor(supervisor)
        
        if not telefono:
            return {
                'success': False,
                'mensaje': 'No se encontró teléfono del supervisor',
                'metodo_envio': None,
                'codigo_debug': codigo  # Solo para testing
            }
        
        # Intentar enviar por WhatsApp primero
        enviado_whatsapp = enviar_otp_whatsapp(
            telefono,
            codigo,
            estudiante_nombre,
            monto
        )
        
        if enviado_whatsapp:
            return {
                'success': True,
                'mensaje': f'Código OTP enviado por WhatsApp a {telefono[-4:]}',
                'metodo_envio': 'whatsapp',
                'valido_minutos': OTP_VALIDITY_MINUTES
            }
        
        # Si falla WhatsApp, intentar SMS
        enviado_sms = enviar_otp_sms(
            telefono,
            codigo,
            estudiante_nombre,
            monto
        )
        
        if enviado_sms:
            return {
                'success': True,
                'mensaje': f'Código OTP enviado por SMS a {telefono[-4:]}',
                'metodo_envio': 'sms',
                'valido_minutos': OTP_VALIDITY_MINUTES
            }
        
        # Si todo falla, devolver código para ingresar manualmente (solo desarrollo)
        return {
            'success': False,
            'mensaje': 'Error enviando OTP. Contacte al administrador.',
            'metodo_envio': None,
            'codigo_debug': codigo  # SOLO PARA DESARROLLO - QUITAR EN PRODUCCIÓN
        }
        
    except Empleado.DoesNotExist:
        return {
            'success': False,
            'mensaje': 'Supervisor no encontrado',
            'metodo_envio': None
        }
    except Exception as e:
        logger.error(f"Error solicitando OTP: {e}")
        return {
            'success': False,
            'mensaje': f'Error: {str(e)}',
            'metodo_envio': None
        }
