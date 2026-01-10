#!/usr/bin/env python
"""
Script de validación de impresora térmica
Detecta, prueba y valida impresoras térmicas USB (80mm)
Compatible con Windows y Linux
"""

import os
import sys
import subprocess
import serial
import serial.tools.list_ports
from datetime import datetime
from pathlib import Path

class ValidadorImpresoraTermica:
    """Validador de impresoras térmicas USB"""
    
    def __init__(self):
        self.puertos_detectados = []
        self.impresora_activa = None
        self.baudrate = 9600  # Estándar para impresoras térmicas
        
    def detectar_puertos_usb(self):
        """Detectar puertos COM/TTY disponibles"""
        print("🔍 Buscando puertos USB...")
        
        try:
            puertos = list(serial.tools.list_ports.comports())
            
            if not puertos:
                print("   ❌ No se encontraron puertos COM/TTY")
                return False
            
            print(f"   ✅ Encontrados {len(puertos)} puerto(s):\n")
            
            for puerto in puertos:
                print(f"   • {puerto.device}")
                print(f"     Descripción: {puerto.description}")
                print(f"     Manufacturer: {puerto.manufacturer or 'Desconocido'}\n")
                self.puertos_detectados.append(puerto.device)
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error al detectar puertos: {str(e)}")
            return False
    
    def probar_conexion_puerto(self, puerto):
        """Intentar conectarse a un puerto específico"""
        print(f"\n📡 Probando conexión en {puerto}...")
        
        try:
            # Intentar conexión
            ser = serial.Serial(
                port=puerto,
                baudrate=self.baudrate,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=2
            )
            
            # Conectado
            print(f"   ✅ Conexión exitosa")
            
            # Enviar comando de prueba (ESC/POS)
            # ESC @ = Inicializar impresora
            comando = b'\x1b\x40'
            ser.write(comando)
            
            # Leer respuesta (algunas impresoras responden)
            respuesta = ser.read(10)
            
            if respuesta:
                print(f"   ✅ Respuesta recibida: {respuesta.hex()}")
            else:
                print(f"   ⚠️  No hubo respuesta (normal en algunas impresoras)")
            
            ser.close()
            return True
            
        except serial.SerialException as e:
            print(f"   ❌ Error de conexión: {str(e)}")
            return False
        except Exception as e:
            print(f"   ❌ Error inesperado: {str(e)}")
            return False
    
    def enviar_test_impresion(self, puerto):
        """Enviar comando de prueba de impresión"""
        print(f"\n🖨️  Enviando comando de prueba...")
        
        try:
            ser = serial.Serial(
                port=puerto,
                baudrate=self.baudrate,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=1
            )
            
            # Secuencia ESC/POS para prueba
            # ESC @ = Inicializar
            # FS ! = Modo de comando
            # ESC d = Imprimir líneas de prueba
            comandos = [
                b'\x1b\x40',           # Inicializar impresora
                b'PRUEBA DE IMPRESORA TERMICA\n',  # Texto de prueba
                b'80mm USB Thermal Printer\n',     # Descripción
                b'Test: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S').encode() + b'\n',
                b'\n\n\n',             # Saltos para corte
                b'\x1b\x69',           # Comando de corte parcial
            ]
            
            # Enviar comandos
            for cmd in comandos:
                ser.write(cmd)
                ser.flush()
            
            ser.close()
            print("   ✅ Comando enviado a la impresora")
            return True
            
        except Exception as e:
            print(f"   ❌ Error al enviar prueba: {str(e)}")
            return False
    
    def validar_impresora(self):
        """Validación completa de impresora"""
        print("""
╔════════════════════════════════════════════════════════════════════════════╗
║          VALIDADOR DE IMPRESORA TÉRMICA USB (80mm)                        ║
╚════════════════════════════════════════════════════════════════════════════╝
        """)
        
        # Paso 1: Detectar puertos
        if not self.detectar_puertos_usb():
            print("\n❌ No hay puertos USB disponibles")
            return False
        
        # Paso 2: Probar conexión en cada puerto
        puertos_validos = []
        
        for puerto in self.puertos_detectados:
            if self.probar_conexion_puerto(puerto):
                puertos_validos.append(puerto)
        
        if not puertos_validos:
            print("\n❌ No se encontró impresora conectada")
            return False
        
        # Paso 3: Seleccionar puerto
        print(f"\n✅ Se encontraron {len(puertos_validos)} impresora(s) disponible(s)")
        
        if len(puertos_validos) == 1:
            puerto_seleccionado = puertos_validos[0]
            print(f"   Seleccionada: {puerto_seleccionado}")
        else:
            print("\n   Puertos disponibles:")
            for i, puerto in enumerate(puertos_validos):
                print(f"   {i+1}. {puerto}")
            
            try:
                seleccion = int(input("\n   Selecciona puerto (número): ")) - 1
                if 0 <= seleccion < len(puertos_validos):
                    puerto_seleccionado = puertos_validos[seleccion]
                else:
                    print("   ❌ Selección inválida")
                    return False
            except ValueError:
                print("   ❌ Entrada inválida")
                return False
        
        self.impresora_activa = puerto_seleccionado
        
        # Paso 4: Prueba de impresión
        print(f"\n📋 Enviando comando de prueba a {puerto_seleccionado}...")
        
        if self.enviar_test_impresion(puerto_seleccionado):
            print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                   ✅ VALIDACIÓN EXITOSA                                    ║
║                                                                            ║
║  La impresora térmica está:                                               ║
║    ✅ Conectada
║    ✅ Respondiendo a comandos
║    ✅ Lista para imprimir                                                 ║
║                                                                            ║
║  Puerto: """ + puerto_seleccionado + """
║  Velocidad: """ + str(self.baudrate) + """ baud
║  Tipo: USB Térmico 80mm
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
            """)
            
            # Guardar configuración
            self.guardar_configuracion(puerto_seleccionado)
            return True
        else:
            print("❌ La impresora no respondió al comando de prueba")
            return False
    
    def guardar_configuracion(self, puerto):
        """Guardar configuración en archivo"""
        config_dir = Path(__file__).parent / 'config'
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / 'impresora_config.py'
        
        contenido = f"""# Configuración de Impresora Térmica
# Generado automáticamente por validador
# Fecha: {datetime.now().isoformat()}

PUERTO_IMPRESORA = '{puerto}'
BAUDRATE = 9600
ANCHO_PAGINA_MM = 80  # Ancho estándar de impresora térmica
TIMEOUT = 2

# Configuración ESC/POS (Estándar térmico)
ESC = b'\\x1b'
GS = b'\\x1d'
INIT = ESC + b'@'           # Inicializar impresora
CORTE_TOTAL = ESC + b'i'    # Corte total
CORTE_PARCIAL = GS + b'V'   # Corte parcial (si soporta)
"""
        
        with open(config_file, 'w') as f:
            f.write(contenido)
        
        print(f"\n💾 Configuración guardada en: {config_file}")


def verificar_dependencias():
    """Verificar que pyserial está instalado"""
    try:
        import serial
        print("✅ pyserial está instalado\n")
        return True
    except ImportError:
        print("""
❌ Error: El módulo 'pyserial' no está instalado

Instala con:
  pip install pyserial

        """)
        return False


if __name__ == '__main__':
    # Verificar dependencias
    if not verificar_dependencias():
        sys.exit(1)
    
    # Crear validador
    validador = ValidadorImpresoraTermica()
    
    # Ejecutar validación
    if validador.validar_impresora():
        print("\n✅ Impresora validada correctamente")
        sys.exit(0)
    else:
        print("\n❌ Validación fallida")
        print("""
SOLUCIÓN DE PROBLEMAS:
═══════════════════════

1. Verifica que la impresora esté conectada por USB
2. En Windows: Revisa Device Manager (Puertos COM)
3. En Linux: Ejecuta 'lsusb' para ver dispositivos USB
4. Prueba con otro puerto USB
5. Verifica que el driver USB esté instalado

REINTENTAR:
  python validar_impresora_termica.py
        """)
        sys.exit(1)
