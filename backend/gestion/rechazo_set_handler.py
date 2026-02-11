"""
Manejo Avanzado de Rechazos SET
================================
Gestión de errores, reintentos automáticos y notificaciones para facturación electrónica
Fecha: 10 Enero 2026
"""

import logging
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import json

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache

from .models import (
    DocumentosTributarios, Ventas, DatosFacturacionElect,
    AlertasSistema, AuditoriaOperacion
)

# Configurar logging
logger = logging.getLogger(__name__)

# =============================================================================
# CÓDIGOS DE ERROR SET
# =============================================================================

CODIGOS_ERROR_SET = {
    # Errores recuperables (reintentar)
    '1001': {
        'descripcion': 'Error de comunicación con SET',
        'tipo': 'recuperable',
        'reintentar': True,
        'espera_segundos': 60
    },
    '1002': {
        'descripcion': 'Timeout en la conexión',
        'tipo': 'recuperable',
        'reintentar': True,
        'espera_segundos': 30
    },
    '1003': {
        'descripcion': 'Servicio SET temporalmente no disponible',
        'tipo': 'recuperable',
        'reintentar': True,
        'espera_segundos': 120
    },
    
    # Errores de validación (no reintentar, corregir datos)
    '2001': {
        'descripcion': 'RUC inválido',
        'tipo': 'validacion',
        'reintentar': False,
        'accion': 'Verificar RUC del emisor en datos de empresa'
    },
    '2002': {
        'descripcion': 'Timbrado vencido',
        'tipo': 'validacion',
        'reintentar': False,
        'accion': 'Renovar timbrado en SET'
    },
    '2003': {
        'descripcion': 'Número de factura duplicado',
        'tipo': 'validacion',
        'reintentar': False,
        'accion': 'Verificar secuencia de numeración'
    },
    '2004': {
        'descripcion': 'CDC inválido',
        'tipo': 'validacion',
        'reintentar': False,
        'accion': 'Recalcular CDC'
    },
    '2005': {
        'descripcion': 'Formato XML inválido',
        'tipo': 'validacion',
        'reintentar': False,
        'accion': 'Validar estructura XML contra esquema SET'
    },
    '2006': {
        'descripcion': 'Monto total incorrecto',
        'tipo': 'validacion',
        'reintentar': False,
        'accion': 'Recalcular totales de la factura'
    },
    
    # Errores críticos (requieren intervención manual)
    '3001': {
        'descripcion': 'Certificado digital vencido',
        'tipo': 'critico',
        'reintentar': False,
        'accion': 'Renovar certificado digital en SET'
    },
    '3002': {
        'descripcion': 'Contribuyente bloqueado en SET',
        'tipo': 'critico',
        'reintentar': False,
        'accion': 'Contactar con SET para resolver bloqueo'
    },
    '3003': {
        'descripcion': 'Timbrado no autorizado',
        'tipo': 'critico',
        'reintentar': False,
        'accion': 'Solicitar autorización de timbrado en SET'
    },
}


class SETAPIClient:
    """Cliente HTTP con reintentos automáticos para API SET"""
    
    def __init__(self, max_retries=3, backoff_factor=1):
        """
        Inicializa cliente con estrategia de reintentos
        
        Args:
            max_retries: Número máximo de reintentos
            backoff_factor: Factor de espera exponencial (1, 2, 4, 8...)
        """
        self.base_url = settings.SET_API_URL if hasattr(settings, 'SET_API_URL') else 'https://sifen.set.gov.py/dte/rest'
        self.timeout = 30  # segundos
        
        # Configurar sesión con reintentos automáticos
        self.session = requests.Session()
        
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def enviar_de(self, xml_firmado: str, cdc: str) -> Dict:
        """
        Envía Documento Electrónico a SET
        
        Args:
            xml_firmado: XML firmado digitalmente
            cdc: Código de Control Criptográfico
            
        Returns:
            Respuesta de SET con estado y CDC
        """
        endpoint = f"{self.base_url}/recepcion"
        
        payload = {
            'cdc': cdc,
            'xml': xml_firmado
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        try:
            logger.info(f"Enviando DE con CDC: {cdc}")
            
            response = self.session.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Respuesta SET: {data}")
            
            return data
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout al enviar CDC {cdc}")
            return {
                'codigo': '1002',
                'mensaje': 'Timeout en la conexión',
                'estado': 'error'
            }
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Error de conexión al enviar CDC {cdc}")
            return {
                'codigo': '1001',
                'mensaje': 'Error de comunicación con SET',
                'estado': 'error'
            }
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error {e.response.status_code}: {e}")
            return {
                'codigo': str(e.response.status_code),
                'mensaje': f'Error HTTP: {e.response.text}',
                'estado': 'error'
            }
            
        except Exception as e:
            logger.exception(f"Error inesperado al enviar CDC {cdc}: {e}")
            return {
                'codigo': '9999',
                'mensaje': f'Error inesperado: {str(e)}',
                'estado': 'error'
            }
    
    def consultar_estado(self, cdc: str) -> Dict:
        """
        Consulta estado de un DE en SET
        
        Args:
            cdc: Código de Control Criptográfico
            
        Returns:
            Estado actual del documento
        """
        endpoint = f"{self.base_url}/consulta/{cdc}"
        
        try:
            response = self.session.get(endpoint, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error al consultar estado de CDC {cdc}: {e}")
            return {'estado': 'error', 'mensaje': str(e)}


class ManejadorRechazos:
    """Gestiona rechazos y errores de facturación electrónica"""
    
    def __init__(self):
        self.client = SETAPIClient()
        self.max_reintentos_automaticos = 3
    
    @transaction.atomic
    def procesar_rechazo(self, documento: DocumentosTributarios, 
                        codigo_error: str, mensaje_error: str) -> Dict:
        """
        Procesa un rechazo de SET y determina acción a tomar
        
        Args:
            documento: Documento tributario rechazado
            codigo_error: Código de error SET
            mensaje_error: Mensaje descriptivo
            
        Returns:
            Diccionario con acción tomada y resultado
        """
        logger.warning(f"Procesando rechazo CDC {documento.cdc}: {codigo_error} - {mensaje_error}")
        
        # Obtener info del error
        error_info = CODIGOS_ERROR_SET.get(codigo_error, {
            'descripcion': 'Error desconocido',
            'tipo': 'desconocido',
            'reintentar': False
        })
        
        # Actualizar documento
        documento.estado = 'rechazado'
        documento.codigo_error = codigo_error
        documento.mensaje_error = f"{error_info['descripcion']}: {mensaje_error}"
        documento.fecha_rechazo = timezone.now()
        documento.save()
        
        # Registrar en auditoría
        self._registrar_auditoria(documento, codigo_error, mensaje_error)
        
        # Crear alerta
        self._crear_alerta(documento, error_info, mensaje_error)
        
        # Determinar acción
        if error_info['reintentar']:
            resultado = self._programar_reintento(documento, error_info)
        else:
            resultado = self._marcar_para_revision_manual(documento, error_info)
        
        # Notificar responsables
        self._notificar_rechazo(documento, error_info, mensaje_error)
        
        return resultado
    
    def reintentar_envio(self, documento: DocumentosTributarios) -> Dict:
        """
        Reintenta envío de un documento rechazado
        
        Args:
            documento: Documento a reintentar
            
        Returns:
            Resultado del reintento
        """
        logger.info(f"Reintentando envío de CDC {documento.cdc}")
        
        # Incrementar contador
        documento.intentos_envio = (documento.intentos_envio or 0) + 1
        
        # Verificar límite de reintentos
        if documento.intentos_envio > self.max_reintentos_automaticos:
            logger.warning(f"CDC {documento.cdc} superó máximo de reintentos ({self.max_reintentos_automaticos})")
            return self._marcar_para_revision_manual(documento, {
                'descripcion': 'Máximo de reintentos alcanzado',
                'accion': 'Requiere revisión manual'
            })
        
        # Obtener XML del documento
        xml_firmado = documento.xml_firmado
        if not xml_firmado:
            logger.error(f"CDC {documento.cdc} no tiene XML firmado")
            return {'exito': False, 'mensaje': 'XML firmado no disponible'}
        
        # Enviar a SET
        respuesta = self.client.enviar_de(xml_firmado, documento.cdc)
        
        # Procesar respuesta
        if respuesta.get('estado') == 'aceptado':
            documento.estado = 'aceptado'
            documento.fecha_aprobacion = timezone.now()
            documento.codigo_error = None
            documento.mensaje_error = None
            documento.save()
            
            logger.info(f"CDC {documento.cdc} aceptado en reintento {documento.intentos_envio}")
            
            self._crear_alerta(documento, {
                'tipo': 'exito',
                'descripcion': f'Factura aceptada tras {documento.intentos_envio} reintento(s)'
            }, '')
            
            return {'exito': True, 'mensaje': 'Documento aceptado', 'cdc': documento.cdc}
        else:
            # Aún rechazado
            codigo_error = respuesta.get('codigo', '9999')
            mensaje_error = respuesta.get('mensaje', 'Error desconocido')
            
            return self.procesar_rechazo(documento, codigo_error, mensaje_error)
    
    def reintentar_masivo(self, limite: int = 10) -> List[Dict]:
        """
        Reintenta envío de documentos pendientes
        
        Args:
            limite: Cantidad máxima de documentos a procesar
            
        Returns:
            Lista de resultados
        """
        logger.info(f"Iniciando reintento masivo (límite: {limite})")
        
        # Obtener documentos pendientes de reintento
        documentos_pendientes = DocumentosTributarios.objects.filter(
            estado='rechazado',
            intentos_envio__lt=self.max_reintentos_automaticos,
            fecha_rechazo__gte=timezone.now() - timedelta(days=7)  # Solo últimos 7 días
        ).order_by('fecha_rechazo')[:limite]
        
        resultados = []
        
        for doc in documentos_pendientes:
            try:
                resultado = self.reintentar_envio(doc)
                resultados.append({
                    'cdc': doc.cdc,
                    'exito': resultado.get('exito', False),
                    'mensaje': resultado.get('mensaje', '')
                })
                
                # Esperar 1 segundo entre reintentos para no saturar API
                time.sleep(1)
                
            except Exception as e:
                logger.exception(f"Error al reintentar CDC {doc.cdc}: {e}")
                resultados.append({
                    'cdc': doc.cdc,
                    'exito': False,
                    'mensaje': f'Error: {str(e)}'
                })
        
        logger.info(f"Reintento masivo completado: {len([r for r in resultados if r['exito']])} exitosos de {len(resultados)}")
        
        return resultados
    
    def _programar_reintento(self, documento: DocumentosTributarios, 
                            error_info: Dict) -> Dict:
        """
        Programa un reintento futuro
        
        Args:
            documento: Documento a reintentar
            error_info: Información del error
            
        Returns:
            Resultado de la programación
        """
        espera_segundos = error_info.get('espera_segundos', 60)
        
        # Guardar en cache para procesamiento posterior
        cache_key = f"reintento_factura:{documento.cdc}"
        cache.set(cache_key, {
            'documento_id': documento.id_documento,
            'programado_para': (timezone.now() + timedelta(seconds=espera_segundos)).isoformat()
        }, timeout=espera_segundos + 60)
        
        logger.info(f"Reintento programado para CDC {documento.cdc} en {espera_segundos} segundos")
        
        return {
            'exito': False,
            'mensaje': f'Reintento programado en {espera_segundos} segundos',
            'accion': 'reintento_programado',
            'espera_segundos': espera_segundos
        }
    
    def _marcar_para_revision_manual(self, documento: DocumentosTributarios, 
                                     error_info: Dict) -> Dict:
        """
        Marca documento para revisión manual
        
        Args:
            documento: Documento rechazado
            error_info: Información del error
            
        Returns:
            Resultado
        """
        documento.requiere_revision_manual = True
        documento.save()
        
        # Crear alerta de alta prioridad
        AlertasSistema.objects.create(
            tipo_alerta='facturacion_critica',
            prioridad='alta',
            titulo=f'Factura {documento.cdc} requiere revisión manual',
            mensaje=f"{error_info.get('descripcion', 'Error desconocido')}\n\nAcción requerida: {error_info.get('accion', 'Revisar manualmente')}",
            datos_json=json.dumps({
                'documento_id': documento.id_documento,
                'cdc': documento.cdc,
                'codigo_error': documento.codigo_error,
                'intentos': documento.intentos_envio
            })
        )
        
        logger.warning(f"CDC {documento.cdc} marcado para revisión manual")
        
        return {
            'exito': False,
            'mensaje': 'Documento requiere revisión manual',
            'accion': 'revision_manual',
            'razon': error_info.get('accion', 'No especificada')
        }
    
    def _registrar_auditoria(self, documento: DocumentosTributarios, 
                            codigo_error: str, mensaje_error: str):
        """Registra evento en auditoría"""
        try:
            AuditoriaOperacion.objects.create(
                tipo_operacion='facturacion_electronica',
                accion='rechazo_set',
                descripcion=f'Factura rechazada por SET: {codigo_error}',
                detalles_json=json.dumps({
                    'cdc': documento.cdc,
                    'codigo_error': codigo_error,
                    'mensaje': mensaje_error,
                    'intentos': documento.intentos_envio
                }),
                ip_origen='SET',
                resultado='error'
            )
        except Exception as e:
            logger.error(f"Error al registrar auditoría: {e}")
    
    def _crear_alerta(self, documento: DocumentosTributarios, 
                     error_info: Dict, mensaje_adicional: str = ''):
        """Crea alerta en el sistema"""
        try:
            # Determinar prioridad según tipo de error
            prioridad_map = {
                'recuperable': 'media',
                'validacion': 'alta',
                'critico': 'critica',
                'exito': 'baja'
            }
            
            prioridad = prioridad_map.get(error_info.get('tipo'), 'media')
            
            AlertasSistema.objects.create(
                tipo_alerta='facturacion',
                prioridad=prioridad,
                titulo=f'Factura {documento.numero_documento}: {error_info.get("descripcion", "Estado actualizado")}',
                mensaje=f"{mensaje_adicional}\n\nCDC: {documento.cdc}\nIntentos: {documento.intentos_envio or 0}",
                datos_json=json.dumps({
                    'documento_id': documento.id_documento,
                    'cdc': documento.cdc,
                    'tipo_error': error_info.get('tipo'),
                    'codigo_error': documento.codigo_error
                })
            )
        except Exception as e:
            logger.error(f"Error al crear alerta: {e}")
    
    def _notificar_rechazo(self, documento: DocumentosTributarios, 
                          error_info: Dict, mensaje_error: str):
        """Envía notificaciones por email a responsables"""
        if not hasattr(settings, 'FACTURACION_EMAIL_NOTIFICACIONES'):
            return
        
        destinatarios = settings.FACTURACION_EMAIL_NOTIFICACIONES
        if not destinatarios:
            return
        
        tipo_error = error_info.get('tipo', 'desconocido')
        
        # Solo notificar errores críticos y de validación
        if tipo_error not in ['critico', 'validacion']:
            return
        
        asunto = f"⚠️ Factura Electrónica Rechazada - CDC {documento.cdc}"
        
        mensaje = f"""
        Factura Electrónica Rechazada por SET
        
        Documento: {documento.numero_documento}
        CDC: {documento.cdc}
        Fecha Emisión: {documento.fecha_emision}
        
        Error: {error_info.get('descripcion', 'Error desconocido')}
        Detalle: {mensaje_error}
        
        Tipo de Error: {tipo_error.upper()}
        Acción Requerida: {error_info.get('accion', 'Revisar documento')}
        
        Intentos de Envío: {documento.intentos_envio or 0}
        
        Por favor, revisar y corregir el documento en el sistema.
        """
        
        try:
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                destinatarios,
                fail_silently=True
            )
            logger.info(f"Notificación enviada para CDC {documento.cdc}")
        except Exception as e:
            logger.error(f"Error al enviar notificación: {e}")


# =============================================================================
# COMANDO DJANGO PARA REINTENTOS AUTOMÁTICOS
# =============================================================================

"""
Crear archivo: gestion/management/commands/reintentar_facturas.py

from django.core.management.base import BaseCommand
from gestion.rechazo_set_handler import ManejadorRechazos

class Command(BaseCommand):
    help = 'Reintenta envío de facturas rechazadas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limite',
            type=int,
            default=10,
            help='Cantidad máxima de documentos a procesar'
        )
    
    def handle(self, *args, **options):
        limite = options['limite']
        
        manejador = ManejadorRechazos()
        resultados = manejador.reintentar_masivo(limite=limite)
        
        exitosos = len([r for r in resultados if r['exito']])
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Procesados {len(resultados)} documentos. '
                f'Exitosos: {exitosos}, Fallidos: {len(resultados) - exitosos}'
            )
        )

# Ejecutar cada 15 minutos con cron:
# */15 * * * * cd /ruta/proyecto && python manage.py reintentar_facturas --limite=20
"""
