"""
Gestor de impresora térmica para Django
Maneja conexión, impresión y recuperación de errores en producción
"""

import serial
from django.conf import settings
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger('impresora')

# Importar configuración de impresora
try:
    from config.impresora_config import (
        PUERTO_IMPRESORA, BAUDRATE, TIMEOUT, INIT, CORTE_TOTAL,
        ALINEAR_IZQ, ALINEAR_CEN, ENFATIZADO, NORMAL
    )
    IMPRESORA_CONFIGURADA = True
except ImportError:
    # Valores por defecto si no está configurado
    PUERTO_IMPRESORA = None
    BAUDRATE = 9600
    TIMEOUT = 2
    INIT = b'\x1b\x40'
    CORTE_TOTAL = b'\x1b\x69'
    ALINEAR_IZQ = b'\x1b\x61\x00'
    ALINEAR_CEN = b'\x1b\x61\x01'
    ENFATIZADO = b'\x1b\x21\x08'
    NORMAL = b'\x1b\x21\x00'
    IMPRESORA_CONFIGURADA = False


class ImpresoraTermica:
    """Interfaz para imprimir tickets en impresora térmica USB"""
    
    def __init__(self, puerto=None, baudrate=None):
        """
        Inicializa el gestor de impresora
        
        Args:
            puerto: Puerto COM/TTY (ej: COM3 o /dev/ttyUSB0)
            baudrate: Velocidad en baudios (default: 9600)
        """
        self.puerto_impresora = puerto or PUERTO_IMPRESORA
        self.baudrate = baudrate or BAUDRATE
        self.conexion = None
        self.log_file = Path('logs') / 'impresora.log'
        self.log_file.parent.mkdir(exist_ok=True)
        self.intentos_conexion = 0
        self.max_intentos = 3
    
    def conectar(self):
        """Establece conexión con la impresora"""
        if not self.puerto_impresora:
            self._registrar_error("Puerto no configurado - ejecutar: python test_conectar_impresora.py")
            return False
        
        if self.conexion and self.conexion.is_open:
            return True
        
        try:
            self.conexion = serial.Serial(
                port=self.puerto_impresora,
                baudrate=self.baudrate,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=TIMEOUT
            )
            
            # Inicializar impresora
            self.conexion.write(INIT)
            self.conexion.flush()
            
            self._registrar("Conexión establecida en puerto " + str(self.puerto_impresora))
            self.intentos_conexion = 0
            return True
            
        except serial.SerialException as e:
            self.intentos_conexion += 1
            self._registrar_error(f"Fallo conexión ({self.intentos_conexion}/{self.max_intentos}): {e}")
            
            if self.intentos_conexion >= self.max_intentos:
                self._registrar_error("MAX_INTENTOS alcanzado - impresora probablemente desconectada")
            
            return False
    
    def desconectar(self):
        """Cierra la conexión"""
        if self.conexion and self.conexion.is_open:
            try:
                self.conexion.close()
                self._registrar("Conexión cerrada")
            except Exception as e:
                self._registrar_error(f"Error al cerrar: {e}")
    
    def _asegurar_conexion(self):
        """Verifica y reconecta si es necesario"""
        if not self.conexion or not self.conexion.is_open:
            return self.conectar()
        return True
    
    def imprimir_texto(self, texto, enfatizado=False, centrado=False):
        """
        Imprime texto simple
        
        Args:
            texto: Texto a imprimir
            enfatizado: Aplicar formato enfatizado
            centrado: Alinear al centro
        
        Returns:
            True si se imprimió correctamente
        """
        if not self._asegurar_conexion():
            return False
        
        try:
            # Aplicar alineación
            if centrado:
                self.conexion.write(ALINEAR_CEN)
            else:
                self.conexion.write(ALINEAR_IZQ)
            
            # Aplicar énfasis
            if enfatizado:
                self.conexion.write(ENFATIZADO)
            
            # Enviar texto
            self.conexion.write(texto.encode('utf-8'))
            self.conexion.write(b'\n')
            
            # Resetear formatos
            self.conexion.write(NORMAL)
            self.conexion.write(ALINEAR_IZQ)
            
            self.conexion.flush()
            return True
            
        except Exception as e:
            self._registrar_error(f"Error escribir: {e}")
            return False
    
    def imprimir_linea(self, longitud=40):
        """Imprime una línea divisoria"""
        self.imprimir_texto("=" * longitud)
    
    def imprimir_ticket(self, venta_data, con_corte=True):
        """
        Imprime un ticket completo de venta
        
        Args:
            venta_data: Dict con datos de la venta
                {
                    'numero': '001',
                    'fecha': datetime,
                    'detalles': [
                        {
                            'producto': 'Agua Mineral',
                            'cantidad': 2,
                            'precio': 5000,
                            'subtotal': 10000
                        },
                        ...
                    ],
                    'subtotal': 10000,
                    'iva': 1000,
                    'total': 11000,
                    'metodo_pago': 'EFECTIVO',
                    'cliente': 'PÚBLICO',
                    'efectivo_recibido': 15000  # opcional
                }
            con_corte: Si ejecutar comando de corte al final
        
        Returns:
            True si se imprimió correctamente
        """
        if not self._asegurar_conexion():
            return False
        
        try:
            # ENCABEZADO
            self.imprimir_linea(40)
            self.imprimir_texto("CANTINA - TICKET DE VENTA", enfatizado=True, centrado=True)
            self.imprimir_linea(40)
            
            # Información básica
            fecha_str = venta_data['fecha'].strftime('%d/%m/%Y %H:%M')
            numero = str(venta_data.get('numero', '???')).zfill(6)
            
            self.imprimir_texto(f"Ticket: {numero:<24} {fecha_str}")
            cliente = venta_data.get('cliente', 'PÚBLICO')
            self.imprimir_texto(f"Cliente: {cliente}")
            
            self.imprimir_linea(40)
            
            # DETALLES DE PRODUCTOS
            for detalle in venta_data['detalles']:
                # Línea del producto
                nombre = detalle['producto'][:22].ljust(22)
                cantidad = str(detalle['cantidad']).rjust(4)
                precio = f"{int(detalle['precio']):,}".rjust(10)
                
                self.imprimir_texto(f"{nombre}{cantidad} {precio}")
                
                # Subtotal
                subtotal_str = f"₲{int(detalle['subtotal']):,}".rjust(14)
                self.imprimir_texto(f"{'SUBT':<22}{subtotal_str}")
            
            self.imprimir_linea(40)
            
            # TOTALES
            subtotal = int(venta_data.get('subtotal', 0))
            iva = int(venta_data.get('iva', 0))
            total = int(venta_data.get('total', 0))
            
            if subtotal > 0:
                subtotal_str = f"₲{subtotal:,}".rjust(14)
                self.imprimir_texto(f"{'SUBTOTAL':<22}{subtotal_str}")
            
            if iva > 0:
                iva_str = f"₲{iva:,}".rjust(14)
                self.imprimir_texto(f"{'IVA (10%)':<22}{iva_str}")
            
            total_str = f"₲{total:,}".rjust(14)
            self.imprimir_texto(f"{'TOTAL':<22}{total_str}", enfatizado=True)
            
            # MÉTODO DE PAGO Y CAMBIO
            self.imprimir_linea(40)
            
            metodo = venta_data.get('metodo_pago', 'DESCONOCIDO')
            self.imprimir_texto(f"Método: {metodo}")
            
            if venta_data.get('efectivo_recibido'):
                efectivo = int(venta_data['efectivo_recibido'])
                cambio = efectivo - total
                
                efectivo_str = f"₲{efectivo:,}".rjust(14)
                cambio_str = f"₲{cambio:,}".rjust(14)
                
                self.imprimir_texto(f"{'Efectivo':<22}{efectivo_str}")
                self.imprimir_texto(f"{'Cambio':<22}{cambio_str}")
            
            # PIE
            self.imprimir_linea(40)
            self.imprimir_texto("¡Gracias por su compra!", centrado=True)
            self.imprimir_texto("Vuelve pronto", centrado=True)
            self.imprimir_texto(" ", centrado=False)
            
            # CORTE (opcional)
            if con_corte:
                try:
                    self.conexion.write(CORTE_TOTAL)
                    self.conexion.flush()
                except:
                    pass  # Algunos modelos no soportan corte automático
            
            self._registrar(f"Ticket #{numero} imprimido exitosamente")
            return True
            
        except Exception as e:
            self._registrar_error(f"Error imprimir ticket: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def imprimir_reporte(self, titulo, datos_tabla):
        """
        Imprime un reporte simple
        
        Args:
            titulo: Título del reporte
            datos_tabla: Lista de tuplas o listas para cada fila
        
        Returns:
            True si se imprimió correctamente
        """
        if not self._asegurar_conexion():
            return False
        
        try:
            self.imprimir_linea()
            self.imprimir_texto(titulo, enfatizado=True, centrado=True)
            self.imprimir_linea()
            
            for fila in datos_tabla:
                if isinstance(fila, (list, tuple)):
                    self.imprimir_texto(str(fila[0]) if len(fila) > 0 else "")
                else:
                    self.imprimir_texto(str(fila))
            
            self.imprimir_linea()
            
            self._registrar(f"Reporte imprimido: {titulo}")
            return True
            
        except Exception as e:
            self._registrar_error(f"Error imprimir reporte: {e}")
            return False
    
    def obtener_estado(self):
        """Retorna el estado actual de la impresora"""
        return {
            'puerto': self.puerto_impresora,
            'conectada': self.conexion and self.conexion.is_open,
            'baudrate': self.baudrate,
            'configurada': IMPRESORA_CONFIGURADA,
            'intentos_fallidos': self.intentos_conexion
        }
    
    def _registrar(self, mensaje):
        """Registra evento exitoso en log"""
        timestamp = datetime.now().isoformat()
        log_msg = f"[{timestamp}] ✓ {mensaje}"
        
        # Escribir en archivo
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
        
        # Log de Django
        logger.info(mensaje)
    
    def _registrar_error(self, mensaje):
        """Registra error en log"""
        timestamp = datetime.now().isoformat()
        log_msg = f"[{timestamp}] ❌ {mensaje}"
        
        # Escribir en archivo
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
        
        # Log de Django
        logger.error(mensaje)


# ===== SINGLETON PARA USO GLOBAL =====

_impresora_instance = None

def obtener_impresora(puerto=None, baudrate=None):
    """
    Obtiene o crea instancia singleton de impresora
    
    Args:
        puerto: Puerto a usar (si es None, usa config)
        baudrate: Velocidad en baudios
    
    Returns:
        ImpresoraTermica: Instancia singleton
    """
    global _impresora_instance
    
    if _impresora_instance is None:
        _impresora_instance = ImpresoraTermica(puerto=puerto, baudrate=baudrate)
    
    return _impresora_instance


def obtener_estado_impresora():
    """Obtiene estado de la impresora sin crear instancia"""
    impresora = obtener_impresora()
    return impresora.obtener_estado()
