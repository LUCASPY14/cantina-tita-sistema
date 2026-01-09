"""
Integración con Tigo Money Paraguay
Gateway de pagos para billetera digital Tigo Money
"""
import requests
import json
import uuid
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse


class TigoMoneyGateway:
    """
    Cliente para API de Tigo Money Paraguay
    
    Basado en documentación de Tigo Money:
    - Billetera digital más usada en Paraguay
    - Pagos con número de teléfono
    - Confirmación por SMS/USSD
    """
    
    def __init__(self):
        self.base_url = getattr(settings, 'TIGO_MONEY_BASE_URL', 'https://api.tigo.com.py/v1')
        self.api_key = getattr(settings, 'TIGO_MONEY_API_KEY', '')
        self.merchant_id = getattr(settings, 'TIGO_MONEY_MERCHANT_ID', '')
        self.merchant_secret = getattr(settings, 'TIGO_MONEY_MERCHANT_SECRET', '')
        self.environment = getattr(settings, 'TIGO_MONEY_ENVIRONMENT', 'sandbox')
    
    def _get_headers(self):
        """Genera headers para requests a Tigo Money API"""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'X-API-Key': self.api_key,
            'X-Merchant-Id': self.merchant_id,
        }
    
    def _generar_transaction_id(self, tipo_pago='CARGA'):
        """Genera un ID único de transacción"""
        timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
        unique = uuid.uuid4().hex[:8].upper()
        return f"TIGO-{tipo_pago}-{timestamp}-{unique}"
    
    def iniciar_pago(self, telefono, monto, descripcion, customer_data=None):
        """
        Inicia un pago con Tigo Money
        
        Args:
            telefono (str): Número de teléfono Tigo Money (formato: +595981123456)
            monto (Decimal): Monto a cobrar en Guaraníes
            descripcion (str): Descripción del pago
            customer_data (dict): Datos adicionales del cliente
            
        Returns:
            tuple: (exito, transaction_id, response_data, error_message)
        """
        try:
            # Validar API key
            if not self.api_key or self.environment == 'sandbox':
                return self._simular_pago(telefono, monto, descripcion)
            
            # Formatear teléfono (debe incluir código de país +595)
            telefono_formateado = self._formatear_telefono(telefono)
            
            # Generar transaction ID
            transaction_id = self._generar_transaction_id()
            
            # Preparar payload
            payload = {
                'merchantId': self.merchant_id,
                'transactionId': transaction_id,
                'amount': int(monto),  # Tigo Money espera enteros (sin decimales)
                'currency': 'PYG',
                'phoneNumber': telefono_formateado,
                'description': descripcion,
                'callbackUrl': settings.SITE_URL + '/api/webhooks/tigo-money/',
                'metadata': {
                    'customer': customer_data or {},
                    'timestamp': timezone.now().isoformat(),
                }
            }
            
            # Endpoint de Tigo Money
            endpoint = f'{self.base_url}/payments/initiate'
            
            # Realizar request
            response = requests.post(
                endpoint,
                json=payload,
                headers=self._get_headers(),
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                
                return (
                    True,
                    transaction_id,
                    data,
                    None
                )
            else:
                error_msg = f"Error {response.status_code}: {response.text}"
                print(f"❌ Tigo Money error: {error_msg}")
                return (False, None, None, error_msg)
                
        except requests.exceptions.Timeout:
            return (False, None, None, "Timeout conectando con Tigo Money")
        except requests.exceptions.RequestException as e:
            return (False, None, None, f"Error de conexión: {str(e)}")
        except Exception as e:
            return (False, None, None, f"Error inesperado: {str(e)}")
    
    def _simular_pago(self, telefono, monto, descripcion):
        """
        Simula un pago exitoso en modo sandbox/desarrollo
        Útil para testing sin API key real
        """
        print("🧪 MODO SANDBOX: Simulando pago con Tigo Money")
        
        transaction_id = self._generar_transaction_id()
        
        response_data = {
            'status': 'PENDING',
            'transactionId': transaction_id,
            'amount': int(monto),
            'phoneNumber': telefono,
            'description': descripcion,
            'message': 'Pago iniciado. El cliente debe confirmar en su teléfono.',
            'simulado': True,
        }
        
        print(f"✅ Pago simulado: {transaction_id}")
        print(f"   Teléfono: {telefono}")
        print(f"   Monto: Gs. {int(monto):,}")
        print(f"   El usuario debe confirmar con *555# en su celular Tigo")
        
        return (True, transaction_id, response_data, None)
    
    def consultar_estado_pago(self, transaction_id):
        """
        Consulta el estado de un pago pendiente
        
        Args:
            transaction_id (str): ID de transacción generado
            
        Returns:
            tuple: (exito, estado, datos)
        """
        try:
            if not self.api_key or self.environment == 'sandbox':
                # En sandbox, simular que está pendiente
                return (True, 'PENDING', {'status': 'PENDING', 'message': 'Esperando confirmación del usuario'})
            
            endpoint = f'{self.base_url}/payments/status/{transaction_id}'
            
            response = requests.get(
                endpoint,
                headers=self._get_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                estado = data.get('status', 'UNKNOWN')
                return (True, estado, data)
            else:
                return (False, 'ERROR', None)
                
        except Exception as e:
            print(f"Error consultando estado: {e}")
            return (False, 'ERROR', None)
    
    def _formatear_telefono(self, telefono):
        """
        Formatea número de teléfono paraguayo al formato de Tigo Money
        
        Ejemplos:
            0981123456 -> +595981123456
            981123456 -> +595981123456
            +595981123456 -> +595981123456
        """
        # Limpiar el número
        telefono = str(telefono).strip().replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Si ya tiene +595, retornar
        if telefono.startswith('+595'):
            return telefono
        
        # Si empieza con 0, quitar el 0
        if telefono.startswith('0'):
            telefono = telefono[1:]
        
        # Agregar código de país
        return f'+595{telefono}'
    
    def validar_telefono_tigo(self, telefono):
        """
        Valida que el número sea un celular Tigo válido
        
        Operadoras en Paraguay:
        - Tigo: 981, 982, 983, 991, 992
        - Personal: 971, 972, 973, 975, 976, 981
        - Claro: 961, 962, 963, 964
        """
        telefono_limpio = telefono.strip().replace(' ', '').replace('-', '')
        
        # Quitar +595 o 0 inicial
        if telefono_limpio.startswith('+595'):
            telefono_limpio = telefono_limpio[4:]
        elif telefono_limpio.startswith('0'):
            telefono_limpio = telefono_limpio[1:]
        
        # Prefijos de Tigo
        prefijos_tigo = ['981', '982', '983', '991', '992']
        
        # Validar longitud (debe ser 9 dígitos sin el 0)
        if len(telefono_limpio) != 9:
            return False, "Número debe tener 9 dígitos (sin el 0 inicial)"
        
        # Validar que sea Tigo
        prefijo = telefono_limpio[:3]
        if prefijo not in prefijos_tigo:
            return False, f"El número no es Tigo. Prefijo {prefijo} no es válido. Use números que comiencen con: {', '.join(prefijos_tigo)}"
        
        return True, "Número Tigo válido"


# ============================================================================
# FUNCIONES DE CONVENIENCIA PARA USAR EN VISTAS
# ============================================================================

def procesar_pago_tigo_money(telefono, monto, descripcion, request, tipo_pago='CARGA_SALDO', venta_ids=None):
    """
    Función simplificada para procesar pagos con Tigo Money
    Compatible con la interfaz de procesar_pago_metrepay()
    
    Args:
        telefono (str): Número de celular Tigo Money
        monto (Decimal): Monto a cobrar
        descripcion (str): Descripción del pago
        request: Django request object
        tipo_pago (str): 'CARGA_SALDO', 'PAGO_DEUDAS', etc.
        venta_ids (list): IDs de ventas a pagar (opcional)
        
    Returns:
        tuple: (exito, transaction_id, confirmation_message, custom_id)
    """
    try:
        # Crear instancia del gateway
        gateway = TigoMoneyGateway()
        
        # Validar teléfono
        es_valido, mensaje = gateway.validar_telefono_tigo(telefono)
        if not es_valido:
            return (False, None, None, mensaje)
        
        # Obtener datos del cliente desde la sesión
        cliente_nombre = request.session.get('cliente_usuario', 'Cliente')
        
        # Generar custom_id según tipo de pago
        if tipo_pago == 'CARGA_SALDO':
            custom_id = f"CARGA-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        elif tipo_pago == 'PAGO_DEUDAS':
            venta_ids_str = ','.join(map(str, venta_ids or []))
            custom_id = f"PAGO-{venta_ids_str}"
        else:
            custom_id = f"OTRO-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        
        # Preparar datos del cliente
        customer_data = {
            'nombre': cliente_nombre,
            'custom_id': custom_id,
        }
        
        # Iniciar pago
        exito, transaction_id, response_data, error = gateway.iniciar_pago(
            telefono=telefono,
            monto=monto,
            descripcion=f"{descripcion} - {cliente_nombre}",
            customer_data=customer_data
        )
        
        if exito:
            # Mensaje de confirmación para el usuario
            mensaje = f"""
            ✅ Pago iniciado con Tigo Money
            
            📱 Se ha enviado una solicitud de pago a su número Tigo Money: {telefono}
            💰 Monto: Gs. {int(monto):,}
            🔢 Código de transacción: {transaction_id}
            
            ⚠️ IMPORTANTE:
            1. Marque *555# en su celular Tigo
            2. Seleccione "Pagar"
            3. Ingrese el código: {transaction_id[-6:]}
            4. Confirme el pago
            
            El pago se acreditará automáticamente una vez confirmado.
            """
            
            return (True, transaction_id, mensaje, custom_id)
        else:
            return (False, None, None, error)
            
    except Exception as e:
        error_msg = f"Error procesando pago con Tigo Money: {str(e)}"
        print(f"❌ {error_msg}")
        return (False, None, None, error_msg)


def verificar_pago_tigo_money(transaction_id):
    """
    Verifica el estado de un pago de Tigo Money
    
    Args:
        transaction_id (str): ID de transacción
        
    Returns:
        dict: Estado del pago
    """
    gateway = TigoMoneyGateway()
    exito, estado, datos = gateway.consultar_estado_pago(transaction_id)
    
    return {
        'exito': exito,
        'estado': estado,
        'datos': datos,
        'completado': estado == 'COMPLETED',
        'pendiente': estado == 'PENDING',
        'fallido': estado in ['FAILED', 'CANCELLED', 'EXPIRED'],
    }
