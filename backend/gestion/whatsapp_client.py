"""
Cliente Python para servidor WhatsApp (whatsapp-web.js)

Este módulo provee una interfaz Python para comunicarse con el servidor
Node.js que maneja WhatsApp Web.

Costo: $0 GRATIS
⚠️ NO OFICIAL - Solo usar con número secundario

Autor: CantiTita
Fecha: 2026-01-10
"""

import requests
import logging
from django.conf import settings
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class WhatsAppWebClient:
    """
    Cliente para servidor whatsapp-web.js
    
    Permite enviar mensajes de WhatsApp de forma gratuita usando
    un servidor Node.js local.
    
    Attributes:
        base_url (str): URL del servidor WhatsApp (default: http://localhost:3000)
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Inicializar cliente WhatsApp
        
        Args:
            base_url: URL del servidor WhatsApp. Si None, usa settings.WHATSAPP_SERVER_URL
        """
        self.base_url = base_url or getattr(
            settings, 
            'WHATSAPP_SERVER_URL', 
            'http://localhost:3000'
        )
        self.timeout = 30  # Timeout para requests
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict] = None,
        timeout: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Realizar request HTTP al servidor WhatsApp
        
        Args:
            method: Método HTTP ('GET' o 'POST')
            endpoint: Endpoint a llamar (ej: '/send')
            data: Datos a enviar (para POST)
            timeout: Timeout personalizado
            
        Returns:
            Respuesta JSON del servidor o None si error
        """
        try:
            url = f"{self.base_url}{endpoint}"
            timeout = timeout or self.timeout
            
            if method.upper() == 'GET':
                response = requests.get(url, timeout=timeout)
            else:
                response = requests.post(url, json=data, timeout=timeout)
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(f"Error HTTP {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout al conectar con servidor WhatsApp en {url}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"No se pudo conectar con servidor WhatsApp en {url}")
            return None
        except Exception as e:
            logger.error(f"Error en request a {endpoint}: {str(e)}")
            return None
    
    def check_status(self) -> bool:
        """
        Verificar si WhatsApp está conectado y listo
        
        Returns:
            True si está conectado, False si no
        """
        try:
            response = self._make_request('GET', '/status', timeout=5)
            if response:
                is_ready = response.get('ready', False)
                if is_ready:
                    logger.info("✅ WhatsApp conectado y listo")
                else:
                    logger.warning("⚠️ WhatsApp no está listo")
                return is_ready
            return False
        except Exception as e:
            logger.error(f"Error verificando estado WhatsApp: {e}")
            return False
    
    def get_qr(self) -> Optional[str]:
        """
        Obtener código QR para escanear (si existe)
        
        Returns:
            String con QR code o None
        """
        try:
            response = self._make_request('GET', '/qr', timeout=5)
            if response:
                return response.get('qr')
            return None
        except Exception as e:
            logger.error(f"Error obteniendo QR: {e}")
            return None
    
    def send_message(self, phone: str, message: str) -> bool:
        """
        Enviar mensaje de texto simple
        
        Args:
            phone: Número de teléfono con formato +595981234567
            message: Texto del mensaje a enviar
        
        Returns:
            True si envío exitoso, False si error
            
        Example:
            >>> client = WhatsAppWebClient()
            >>> client.send_message('+595981234567', 'Hola desde CantiTita')
            True
        """
        try:
            # Verificar conexión primero
            if not self.check_status():
                logger.error("❌ WhatsApp no está conectado. Inicia el servidor primero.")
                return False
            
            # Limpiar número
            phone_clean = phone.replace('+', '').replace(' ', '').replace('-', '')
            
            # Enviar mensaje
            response = self._make_request(
                'POST',
                '/send',
                data={
                    'phone': phone_clean,
                    'message': message
                }
            )
            
            if response and response.get('success'):
                logger.info(f"✅ WhatsApp enviado a {phone}")
                return True
            else:
                error = response.get('error', 'Error desconocido') if response else 'Sin respuesta'
                logger.error(f"❌ Error enviando WhatsApp a {phone}: {error}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Excepción enviando WhatsApp: {str(e)}")
            return False
    
    def send_template(
        self, 
        phone: str, 
        template_name: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Enviar mensaje usando template predefinido
        
        Templates disponibles:
        - 'saldo_bajo': Notificación de saldo bajo
        - 'recarga_exitosa': Confirmación de recarga
        - 'cuenta_pendiente': Recordatorio de cuenta pendiente
        - 'compra_realizada': Confirmación de compra
        
        Args:
            phone: Número de teléfono
            template_name: Nombre del template a usar
            params: Parámetros para el template
        
        Returns:
            True si envío exitoso, False si error
            
        Example:
            >>> client.send_template(
            ...     '+595981234567',
            ...     'saldo_bajo',
            ...     {'tarjeta': '12345', 'saldo': '5,000'}
            ... )
            True
        """
        try:
            if not self.check_status():
                logger.error("❌ WhatsApp no está conectado")
                return False
            
            phone_clean = phone.replace('+', '').replace(' ', '').replace('-', '')
            
            response = self._make_request(
                'POST',
                '/send-template',
                data={
                    'phone': phone_clean,
                    'template': template_name,
                    'params': params or {}
                }
            )
            
            if response and response.get('success'):
                logger.info(f"✅ Template '{template_name}' enviado a {phone}")
                return True
            else:
                error = response.get('error', 'Error desconocido') if response else 'Sin respuesta'
                logger.error(f"❌ Error enviando template: {error}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error enviando template: {str(e)}")
            return False
    
    def send_image(
        self, 
        phone: str, 
        image_url: str, 
        caption: Optional[str] = None
    ) -> bool:
        """
        Enviar imagen con caption opcional
        
        Args:
            phone: Número de teléfono
            image_url: URL de la imagen a enviar
            caption: Texto opcional para la imagen
        
        Returns:
            True si envío exitoso, False si error
        """
        try:
            if not self.check_status():
                logger.error("❌ WhatsApp no está conectado")
                return False
            
            phone_clean = phone.replace('+', '').replace(' ', '').replace('-', '')
            
            response = self._make_request(
                'POST',
                '/send-image',
                data={
                    'phone': phone_clean,
                    'imageUrl': image_url,
                    'caption': caption or ''
                }
            )
            
            if response and response.get('success'):
                logger.info(f"✅ Imagen enviada a {phone}")
                return True
            else:
                error = response.get('error', 'Error desconocido') if response else 'Sin respuesta'
                logger.error(f"❌ Error enviando imagen: {error}")
                return False
            
        except Exception as e:
            logger.error(f"❌ Error enviando imagen: {str(e)}")
            return False
    
    def send_bulk(self, recipients: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Enviar múltiples mensajes
        
        Args:
            recipients: Lista de dicts con 'phone' y 'message'
                       Ejemplo: [
                           {'phone': '+595981234567', 'message': 'Hola 1'},
                           {'phone': '+595987654321', 'message': 'Hola 2'}
                       ]
        
        Returns:
            Dict con resultados del envío masivo
            
        Example:
            >>> recipients = [
            ...     {'phone': '+595981111111', 'message': 'Msg 1'},
            ...     {'phone': '+595982222222', 'message': 'Msg 2'}
            ... ]
            >>> result = client.send_bulk(recipients)
            >>> print(f"Enviados: {result['successCount']}/{result['total']}")
        """
        try:
            if not self.check_status():
                logger.error("❌ WhatsApp no está conectado")
                return {
                    'success': False, 
                    'error': 'WhatsApp no conectado',
                    'total': len(recipients),
                    'successCount': 0,
                    'errorCount': len(recipients)
                }
            
            # Timeout largo para envío masivo (5 seg por mensaje)
            timeout = len(recipients) * 5 + 10
            
            response = self._make_request(
                'POST',
                '/send-bulk',
                data={'recipients': recipients},
                timeout=timeout
            )
            
            if response:
                logger.info(
                    f"📊 Envío masivo completado: {response.get('successCount', 0)}"
                    f"/{response.get('total', 0)} exitosos"
                )
                return response
            else:
                return {
                    'success': False, 
                    'error': 'Sin respuesta del servidor',
                    'total': len(recipients),
                    'successCount': 0,
                    'errorCount': len(recipients)
                }
            
        except Exception as e:
            logger.error(f"❌ Error en envío masivo: {str(e)}")
            return {
                'success': False, 
                'error': str(e),
                'total': len(recipients),
                'successCount': 0,
                'errorCount': len(recipients)
            }
    
    def get_available_templates(self) -> List[str]:
        """
        Obtener lista de templates disponibles
        
        Returns:
            Lista de nombres de templates
        """
        try:
            response = self._make_request('GET', '/templates', timeout=5)
            if response:
                return response.get('templates', [])
            return []
        except Exception as e:
            logger.error(f"Error obteniendo templates: {e}")
            return []


# ============================================================================
# INSTANCIA GLOBAL
# ============================================================================

# Instancia global para uso en toda la aplicación
whatsapp_client = WhatsAppWebClient()


# ============================================================================
# FUNCIONES DE CONVENIENCIA
# ============================================================================

def enviar_whatsapp_gratis(telefono: str, mensaje: str) -> bool:
    """
    Enviar WhatsApp usando servidor local (GRATIS)
    
    ⚠️ SOLO USAR CON NÚMERO SECUNDARIO
    Costo: $0
    Riesgo: BAN permanente si se usa número principal
    
    Args:
        telefono: Número con formato +595981234567
        mensaje: Texto del mensaje
    
    Returns:
        True si envío exitoso
        
    Example:
        >>> enviar_whatsapp_gratis('+595981234567', 'Hola')
        True
    """
    return whatsapp_client.send_message(telefono, mensaje)


def verificar_whatsapp_conectado() -> bool:
    """
    Verificar si servidor WhatsApp está conectado
    
    Returns:
        True si conectado, False si no
    """
    return whatsapp_client.check_status()
