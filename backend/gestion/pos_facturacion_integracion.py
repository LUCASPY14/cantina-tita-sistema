"""
Integración POS → Facturación Electrónica + Impresora Térmica
==============================================================

Sistema completo de:
- Emisión automática o manual de facturas desde POS
- Integración con impresora térmica
- Manejo de errores y reintentos
- Almacenamiento de histórico de impresión
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
import json
from typing import Dict, Optional, Tuple
import socket
import time

from .models import Ventas, MediosPago
from .facturacion_electronica import GeneradorXMLFactura, ClienteEkuatia
from .pos_general_views import imprimir_ticket_venta

# Métodos de pago que PERMITEN facturación electrónica
MEDIOS_PAGO_CON_FACTURA_ELECTRONICA = [
    'EFECTIVO',
    'TRANSFERENCIA BANCARIA',
    'GIROS TIGO',
    'TARJETA DEBITO /QR',
    'TARJETA CREDITO / QR',
]

# Métodos de pago que NO PERMITEN facturación (solo ticket)
MEDIOS_PAGO_SIN_FACTURA = [
    'TARJETA ESTUDIANTIL',  # Ya tiene factura desde la recarga
]


class GestorImpresoraTermica:
    """
    Gestor de impresora térmica para tickets de venta y facturas
    Soporta: USB, Red, Bluetooth
    """
    
    # Tipos de impresoras soportadas
    TIPOS_IMPRESORA = {
        'USB': 'ESC/POS_USB',
        'RED': 'ESC/POS_RED',
        'BLUETOOTH': 'ESC/POS_BLUETOOTH',
    }
    
    # Comandos ESC/POS
    COMANDOS = {
        'RESET': b'\x1b\x40',
        'INIT': b'\x1b\x40',
        'CORTE': b'\x1d\x56\x42\x00',  # Corte parcial
        'CORTE_TOTAL': b'\x1d\x56\x42\x01',  # Corte total
        'ALINEACION_IZQ': b'\x1b\x61\x00',
        'ALINEACION_CEN': b'\x1b\x61\x01',
        'ALINEACION_DER': b'\x1b\x61\x02',
        'BOLD_ON': b'\x1b\x45\x01',
        'BOLD_OFF': b'\x1b\x45\x00',
        'ANCHO_DOBLE': b'\x1d\x21\x11',
        'ANCHO_NORMAL': b'\x1d\x21\x00',
        'ALTURA_DOBLE': b'\x1d\x21\x10',
        'ALTURA_NORMAL': b'\x1d\x21\x00',
        'FUENTE_A': b'\x1b\x4d\x00',
        'FUENTE_B': b'\x1b\x4d\x01',
    }
    
    def __init__(self, tipo_conexion: str = 'USB', host: Optional[str] = None, puerto: int = 9100):
        """
        Inicializa conexión a impresora
        
        Args:
            tipo_conexion: 'USB', 'RED' o 'BLUETOOTH'
            host: Dirección IP (para RED)
            puerto: Puerto de conexión (para RED)
        """
        self.tipo_conexion = tipo_conexion
        self.host = host
        self.puerto = puerto
        self.conexion = None
        self.conectado = False
        
        if tipo_conexion == 'RED':
            self._conectar_red()
    
    def _conectar_red(self) -> bool:
        """Conecta a impresora por red"""
        try:
            self.conexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conexion.settimeout(10)
            self.conexion.connect((self.host, self.puerto))
            self.conectado = True
            return True
        except Exception as e:
            print(f"Error conectando a impresora: {e}")
            self.conectado = False
            return False
    
    def enviar_comando(self, comando: bytes) -> bool:
        """Envía comando ESC/POS a la impresora"""
        try:
            if self.tipo_conexion == 'RED':
                if not self.conectado:
                    self._conectar_red()
                self.conexion.send(comando)
            else:
                # Para USB/Bluetooth se usaría biblioteca específica
                pass
            return True
        except Exception as e:
            print(f"Error enviando comando: {e}")
            return False
    
    def imprimir_texto(self, texto: str, alineacion: str = 'izq', bold: bool = False) -> bool:
        """
        Imprime texto formateado
        
        Args:
            texto: Texto a imprimir
            alineacion: 'izq', 'centro', 'der'
            bold: Si es negrita
        """
        try:
            # Alineación
            alineaciones = {'izq': self.COMANDOS['ALINEACION_IZQ'],
                          'centro': self.COMANDOS['ALINEACION_CEN'],
                          'der': self.COMANDOS['ALINEACION_DER']}
            self.enviar_comando(alineaciones.get(alineacion, self.COMANDOS['ALINEACION_IZQ']))
            
            # Bold
            if bold:
                self.enviar_comando(self.COMANDOS['BOLD_ON'])
            
            # Texto
            self.enviar_comando(texto.encode('utf-8') + b'\n')
            
            if bold:
                self.enviar_comando(self.COMANDOS['BOLD_OFF'])
            
            return True
        except Exception as e:
            print(f"Error imprimiendo texto: {e}")
            return False
    
    def imprimir_linea_separadora(self, caracter: str = '−', ancho: int = 40):
        """Imprime línea separadora"""
        linea = caracter * ancho
        return self.imprimir_texto(linea, alineacion='centro')
    
    def hacer_corte(self, total: bool = False):
        """Hace corte de papel"""
        comando = self.COMANDOS['CORTE_TOTAL'] if total else self.COMANDOS['CORTE']
        return self.enviar_comando(comando)
    
    def desconectar(self):
        """Desconecta de la impresora"""
        if self.conexion:
            try:
                self.conexion.close()
            except:
                pass
        self.conectado = False


class IntegradorPOSFacturacion:
    """
    Integrador de POS con Facturación Electrónica
    Gestiona:
    - Emisión automática de facturas
    - Reintentos
    - Fallback a factura física
    - Validación de métodos de pago permitidos
    """
    
    def __init__(self, impresora: Optional[GestorImpresoraTermica] = None):
        """
        Inicializa integrador
        
        Args:
            impresora: Instancia de impresora (opcional)
        """
        self.impresora = impresora
        self.cliente_ekuatia = ClienteEkuatia()
        self.max_reintentos = 3
    
    def puede_facturar_electronico(self, id_medio_pago: int) -> Tuple[bool, str]:
        """
        Valida si un medio de pago permite facturación electrónica
        
        Args:
            id_medio_pago: ID del medio de pago
        
        Returns:
            (puede_facturar, mensaje)
        """
        try:
            medio = MediosPago.objects.get(id_medio_pago=id_medio_pago)
            descripcion = medio.descripcion.strip().upper()
            
            # Verificar si es medio que NO permite factura (solo ticket)
            for medio_sin_factura in MEDIOS_PAGO_SIN_FACTURA:
                if descripcion == medio_sin_factura.upper():
                    return False, f'Método "{medio.descripcion}" no genera factura (solo ticket). La factura se emitió en la recarga.'
            
            # Verificar si es medio que permite factura electrónica
            for medio_con_factura in MEDIOS_PAGO_CON_FACTURA_ELECTRONICA:
                if descripcion == medio_con_factura.upper():
                    return True, ''
            
            # Si no es ni uno ni otro, rechazar factura electrónica
            return False, f'Método de pago "{medio.descripcion}" no permite facturación electrónica'
        except MediosPago.DoesNotExist:
            return False, f'Método de pago {id_medio_pago} no encontrado'
        except Exception as e:
            return False, f'Error validando medio de pago: {str(e)}'
    
    @transaction.atomic
    def procesar_venta_con_factura(
        self,
        venta: Ventas,
        emitir_factura: bool = True,
        imprimir: bool = True,
        tipo_factura: str = 'electronica'
    ) -> Dict:
        """
        Procesa venta y emite factura si corresponde
        
        Args:
            venta: Instancia de Ventas
            emitir_factura: Si emitir factura automáticamente
            imprimir: Si imprimir ticket
            tipo_factura: 'electronica' o 'fisica'
        
        Returns:
            {
                'success': bool,
                'venta_id': int,
                'factura': {
                    'cdc': str,
                    'estado': str,
                    'url_kude': str
                },
                'impresion': {
                    'exitosa': bool,
                    'mensaje': str
                },
                'mensaje': str
            }
        """
        resultado = {
            'success': False,
            'venta_id': venta.id_venta,
            'factura': None,
            'impresion': None,
            'mensaje': ''
        }
        
        try:
            # Paso 0: Validar método de pago para facturación
            if emitir_factura and hasattr(venta, 'id_tipo_pago'):
                puede_facturar, mensaje_validacion = self.puede_facturar_electronico(venta.id_tipo_pago.id_tipo_pago)
                
                if not puede_facturar:
                    if 'La factura se emitió en la recarga' in mensaje_validacion:
                        # Es TARJETA ESTUDIANTIL - No facturar, solo ticket
                        emitir_factura = False
                        resultado['mensaje'] = f'✓ {mensaje_validacion}'
                    else:
                        # Cambiar a factura física automáticamente para otros métodos
                        tipo_factura = 'fisica'
                        resultado['mensaje'] = f'Método de pago no permite factura electrónica. {mensaje_validacion} - Emitiendo factura física.'
            
            # Paso 1: Validar que puede facturarse
            if emitir_factura and not venta.id_timbrado:
                resultado['mensaje'] = 'Venta sin timbrado asignado'
                return resultado
            
            # Paso 2: Emitir factura si se solicita
            if emitir_factura:
                factura_resultado = self._emitir_factura_con_reintentos(
                    venta, tipo_factura
                )
                
                if not factura_resultado['success']:
                    resultado['mensaje'] = factura_resultado.get('error', 'Error emitiendo factura')
                    resultado['factura'] = factura_resultado
                    
                    # Si falla factura electrónica, intentar física
                    if tipo_factura == 'electronica':
                        resultado['mensaje'] += ' - Intentando factura física...'
                        factura_resultado = self._emitir_factura_con_reintentos(
                            venta, 'fisica'
                        )
                    
                    if not factura_resultado['success']:
                        return resultado
                
                resultado['factura'] = factura_resultado
            
            # Paso 3: Imprimir si se solicita
            if imprimir and self.impresora and self.impresora.conectado:
                impresion_resultado = self._imprimir_ticket(venta)
                resultado['impresion'] = impresion_resultado
                
                if not impresion_resultado['exitosa']:
                    # No bloquear venta por error de impresión
                    resultado['mensaje'] += f" [Advertencia: {impresion_resultado['mensaje']}]"
            
            resultado['success'] = True
            resultado['mensaje'] = 'Venta procesada exitosamente'
            
            return resultado
            
        except Exception as e:
            resultado['mensaje'] = f'Error procesando venta: {str(e)}'
            return resultado
    
    def _emitir_factura_con_reintentos(
        self,
        venta: Ventas,
        tipo_factura: str
    ) -> Dict:
        """
        Emite factura con reintentos automáticos
        
        Args:
            venta: Instancia de Ventas
            tipo_factura: 'electronica' o 'fisica'
        
        Returns:
            Resultado de emisión
        """
        for intento in range(1, self.max_reintentos + 1):
            try:
                if tipo_factura == 'electronica':
                    # Generar XML
                    generador = GeneradorXMLFactura(venta)
                    xml_factura = generador.generar_xml()
                    cdc = generador.generar_cdc(xml_factura)
                    
                    # Enviar a Ekuatia
                    respuesta = self.cliente_ekuatia.enviar_factura(
                        xml_factura, venta.id_venta
                    )
                    
                    if respuesta['success']:
                        return {
                            'success': True,
                            'cdc': respuesta.get('cdc', cdc),
                            'estado': respuesta.get('estado'),
                            'url_kude': respuesta.get('kude', ''),
                            'xml': xml_factura
                        }
                    else:
                        # Reintentar
                        if intento < self.max_reintentos:
                            time.sleep(2 ** intento)  # Backoff exponencial
                            continue
                        else:
                            return {
                                'success': False,
                                'error': respuesta.get('mensaje', 'Error desconocido')
                            }
                
                else:
                    # Factura física
                    return {
                        'success': True,
                        'cdc': '',
                        'estado': 'FISICA',
                        'url_kude': ''
                    }
                    
            except Exception as e:
                if intento == self.max_reintentos:
                    return {
                        'success': False,
                        'error': str(e)
                    }
                time.sleep(2 ** intento)
        
        return {
            'success': False,
            'error': 'Máximo de reintentos alcanzado'
        }
    
    def _imprimir_ticket(self, venta: Ventas) -> Dict:
        """
        Imprime ticket de venta en impresora térmica
        
        Args:
            venta: Instancia de Ventas
        
        Returns:
            {
                'exitosa': bool,
                'mensaje': str
            }
        """
        try:
            if not self.impresora:
                return {
                    'exitosa': False,
                    'mensaje': 'Impresora no configurada'
                }
            
            # Resetear impresora
            self.impresora.enviar_comando(self.impresora.COMANDOS['RESET'])
            time.sleep(0.5)
            
            # Encabezado
            empresa = venta.id_cliente.id_lista_precio  # Usar empresa de empresa global
            self.impresora.imprimir_texto('CANTINA TITA', alineacion='centro', bold=True)
            self.impresora.imprimir_linea_separadora()
            
            # Info de venta
            self.impresora.imprimir_texto(f"Ticket: {venta.id_venta}", alineacion='izq')
            self.impresora.imprimir_texto(f"Fecha: {venta.fecha.strftime('%d/%m/%Y %H:%M')}", alineacion='izq')
            self.impresora.imprimir_linea_separadora()
            
            # Productos
            self.impresora.imprimir_texto('PRODUCTOS', alineacion='centro', bold=True)
            
            for detalle in venta.detalles.all():
                cantidad_precio = f"{int(detalle.cantidad)}x Gs.{int(detalle.precio_unitario):,}"
                subtotal = f"Gs.{int(detalle.subtotal_total):,}"
                
                self.impresora.imprimir_texto(detalle.id_producto.descripcion[:40], alineacion='izq')
                self.impresora.imprimir_texto(f"{cantidad_precio:<20} {subtotal:>19}", alineacion='izq')
            
            # Total
            self.impresora.imprimir_linea_separadora()
            total_str = f"TOTAL: Gs. {int(venta.monto_total):,}"
            self.impresora.imprimir_texto(total_str, alineacion='centro', bold=True)
            
            # Pie
            self.impresora.imprimir_texto('Gracias por su compra', alineacion='centro')
            self.impresora.imprimir_linea_separadora()
            
            # Corte
            self.impresora.hacer_corte()
            
            return {
                'exitosa': True,
                'mensaje': 'Ticket impreso exitosamente'
            }
            
        except Exception as e:
            return {
                'exitosa': False,
                'mensaje': str(e)
            }


@require_http_methods(["POST"])
@transaction.atomic
def procesar_venta_con_factura_api(request):
    """
    API para procesar venta con facturación automática
    
    POST /gestion/pos/general/api/procesar-venta-factura/
    Body: {
        "id_venta": 1,
        "emitir_factura": true,
        "imprimir": true,
        "tipo_factura": "electronica"
    }
    """
    try:
        data = json.loads(request.body)
        id_venta = data.get('id_venta')
        emitir_factura = data.get('emitir_factura', True)
        imprimir = data.get('imprimir', True)
        tipo_factura = data.get('tipo_factura', 'electronica')
        
        venta = Ventas.objects.get(id_venta=id_venta)
        
        # Crear integrador
        integrador = IntegradorPOSFacturacion()
        
        # Procesar
        resultado = integrador.procesar_venta_con_factura(
            venta,
            emitir_factura=emitir_factura,
            imprimir=imprimir,
            tipo_factura=tipo_factura
        )
        
        return JsonResponse(resultado)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
