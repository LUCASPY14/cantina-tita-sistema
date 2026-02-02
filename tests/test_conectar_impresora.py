#!/usr/bin/env python
"""
SCRIPT DE PRUEBA Y CONFIGURACIÓN - Impresora Térmica USB
Conecta, prueba y configura la impresora para producción
"""

import sys
import serial
import serial.tools.list_ports
from datetime import datetime
from pathlib import Path

class ConfiguradorImpresoraTermica:
    """Configurador completo de impresora térmica"""
    
    def __init__(self):
        self.impresora = None
        self.puerto = None
        self.baudrate = 9600
        self.config_dir = Path(__file__).parent / 'config'
        
    def detectar_y_conectar(self):
        """Detecta y conecta a la impresora"""
        print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║             🖨️  CONFIGURACIÓN DE IMPRESORA TÉRMICA USB                     ║
║                      Para Producción                                       ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
        """)
        
        print("\n[1/5] Detectando impresoras USB conectadas...")
        print("─" * 70)
        
        # Listar puertos
        puertos = list(serial.tools.list_ports.comports())
        
        if not puertos:
            print("❌ No hay puertos USB detectados")
            print("\n⚠️  SOLUCIÓN:")
            print("  1. Verifica que la impresora está conectada")
            print("  2. Comprueba que el cable USB está bien conectado")
            print("  3. En Windows: Abre Device Manager y busca en 'Puertos COM'")
            print("  4. En Linux: Ejecuta 'lsusb' en terminal")
            return False
        
        print(f"✓ Se encontraron {len(puertos)} puerto(s):\n")
        
        impresoras_probables = []
        
        for i, puerto in enumerate(puertos, 1):
            print(f"  {i}. {puerto.device:<15} | {puerto.description}")
            print(f"     Manufacturer: {puerto.manufacturer or 'Desconocido'}")
            
            # Detectar impresoras probables
            if 'thermal' in puerto.description.lower() or 'printer' in puerto.description.lower():
                impresoras_probables.append(puerto.device)
            print()
        
        # Seleccionar puerto
        if impresoras_probables and len(impresoras_probables) == 1:
            self.puerto = impresoras_probables[0]
            print(f"✓ Impresora detectada automáticamente: {self.puerto}")
        else:
            print("Selecciona el puerto de la impresora:")
            while True:
                try:
                    seleccion = int(input("Número (1-" + str(len(puertos)) + "): "))
                    if 1 <= seleccion <= len(puertos):
                        self.puerto = puertos[seleccion - 1].device
                        break
                except ValueError:
                    pass
                print("❌ Entrada inválida, intenta de nuevo")
        
        print(f"\nUsando puerto: {self.puerto}")
        return True
    
    def probar_conexion(self):
        """Prueba la conexión con la impresora"""
        print("\n[2/5] Probando conexión con la impresora...")
        print("─" * 70)
        
        try:
            self.impresora = serial.Serial(
                port=self.puerto,
                baudrate=self.baudrate,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=2
            )
            
            print(f"✓ Conexión establecida en {self.puerto}")
            print(f"  Velocidad: {self.baudrate} baud")
            
            # Enviar comando de inicialización
            self.impresora.write(b'\x1b\x40')
            
            print("✓ Impresora inicializada correctamente")
            return True
            
        except serial.SerialException as e:
            print(f"❌ Error de conexión: {e}")
            print("\n⚠️  SOLUCIÓN:")
            print("  1. Verifica que el puerto es correcto")
            print("  2. Cierra cualquier otro programa que use el puerto")
            print("  3. En Windows: Reinicia el Device Manager")
            print("  4. En Linux: Verifica permisos (sudo chmod 666 /dev/ttyUSB0)")
            return False
    
    def probar_impresion(self):
        """Envía un comando de prueba a la impresora"""
        print("\n[3/5] Enviando comando de prueba a la impresora...")
        print("─" * 70)
        
        if not self.impresora:
            print("❌ Impresora no conectada")
            return False
        
        try:
            # Secuencia ESC/POS
            comandos = [
                b'\x1b\x40',  # Inicializar
                b'╔════════════════════════════════╗\n',
                b'║   PRUEBA DE IMPRESORA TÉRMICA  ║\n',
                b'║                                ║\n',
                b'║  Sistema: Cantina-BD           ║\n',
                b'║  Fecha: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S').encode() + b'\n',
                b'║                                ║\n',
                b'║  ✓ CONEXIÓN EXITOSA            ║\n',
                b'╚════════════════════════════════╝\n',
                b'\n\n\n',
                b'\x1b\x69',  # Comando de corte
            ]
            
            for cmd in comandos:
                self.impresora.write(cmd)
                self.impresora.flush()
            
            print("✓ Comando de prueba enviado")
            print("  Verifica que la impresora imprimió una prueba")
            
            return input("\n¿La impresora imprimió correctamente? (s/n): ").lower() == 's'
            
        except Exception as e:
            print(f"❌ Error al enviar comando: {e}")
            return False
    
    def probar_impresion_ticket(self):
        """Prueba imprimiendo un ticket real"""
        print("\n[4/5] Imprimiendo ticket de prueba...")
        print("─" * 70)
        
        if not self.impresora:
            print("❌ Impresora no conectada")
            return False
        
        try:
            # Formato de ticket de venta real (80mm)
            ticket = f"""
╔════════════════════════════════╗
║      CANTINA - TICKET PRUEBA    ║
║                                ║
║  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
║                                ║
│  PRODUCTO          CANT  PRECIO│
├────────────────────────────────┤
│  Agua Mineral 1L    2   ₲5,000 │
│  Arepa de Queso     1   ₲8,000 │
│  Sándwich           1   ₲10,000│
├────────────────────────────────┤
│  TOTAL:                ₲23,000 │
│  EFECTIVO:            ₲25,000 │
│  CAMBIO:              ₲2,000  │
├────────────────────────────────┤
║  ¡Gracias por su compra!       ║
║  Vuelve pronto!                ║
╚════════════════════════════════╝


"""
            
            # Enviar comando
            self.impresora.write(ticket.encode('utf-8'))
            self.impresora.write(b'\x1b\x69')  # Corte
            self.impresora.flush()
            
            print("✓ Ticket de prueba enviado")
            print("  La impresora debe haber imprimido un ticket completo")
            
            return input("\n¿El ticket se imprimió correctamente? (s/n): ").lower() == 's'
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    def guardar_configuracion(self):
        """Guarda la configuración para ser usada en producción"""
        print("\n[5/5] Guardando configuración...")
        print("─" * 70)
        
        try:
            # Crear directorio si no existe
            self.config_dir.mkdir(exist_ok=True)
            
            # Crear archivo de configuración
            config_file = self.config_dir / 'impresora_config.py'
            
            contenido = f"""# Configuración de Impresora Térmica
# Generada automáticamente: {datetime.now().isoformat()}
# USAR ESTA CONFIGURACIÓN EN pos_general_views.py

PUERTO_IMPRESORA = '{self.puerto}'
BAUDRATE = {self.baudrate}
TIMEOUT = 2

# Tamaño de papel (80mm es estándar para térmicas)
ANCHO_PAGINA_MM = 80
ALTO_LINEA_MM = 3

# Comandos ESC/POS
ESC = b'\\x1b'
GS = b'\\x1d'

# Comandos básicos
INIT = b'\\x1b\\x40'           # Inicializar impresora
CORTE_TOTAL = b'\\x1b\\x69'    # Corte total
CORTE_PARCIAL = b'\\x1d\\x56\\x00'  # Corte parcial (si soporta)

# Configuración de fuente
NORMAL = b'\\x1b\\x21\\x00'
ENFATIZADO = b'\\x1b\\x21\\x08'
DOBLE_ALTO = b'\\x1b\\x21\\x10'
DOBLE_ANCHO = b'\\x1b\\x21\\x20'

# Alineación
ALINEAR_IZQ = b'\\x1b\\x61\\x00'
ALINEAR_CEN = b'\\x1b\\x61\\x01'
ALINEAR_DER = b'\\x1b\\x61\\x02'

# Línea
LINEA = b'════════════════════════════════'
"""
            
            with open(config_file, 'w') as f:
                f.write(contenido)
            
            print(f"✓ Configuración guardada: {config_file}")
            print(f"  Contenido: {config_file.read_text()[:200]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ Error al guardar: {e}")
            return False
    
    def ejecutar(self):
        """Ejecuta el flujo completo"""
        pasos = [
            ("Detectar puerto", self.detectar_y_conectar),
            ("Probar conexión", self.probar_conexion),
            ("Prueba simple", self.probar_impresion),
            ("Ticket de prueba", self.probar_impresion_ticket),
            ("Guardar configuración", self.guardar_configuracion),
        ]
        
        resultados = []
        
        for nombre, funcion in pasos:
            try:
                resultado = funcion()
                resultados.append((nombre, resultado))
                
                if not resultado:
                    print(f"\n⚠️  {nombre} falló")
                    continuar = input("¿Continuar con el siguiente paso? (s/n): ")
                    if continuar.lower() != 's':
                        break
                        
            except Exception as e:
                print(f"\n❌ Error en {nombre}: {e}")
                resultados.append((nombre, False))
        
        # Resumen final
        self.mostrar_resumen(resultados)
        
        # Cerrar conexión
        if self.impresora:
            self.impresora.close()
    
    def mostrar_resumen(self, resultados):
        """Muestra resumen final"""
        print("\n" + "=" * 70)
        print("\n✅ RESUMEN DE CONFIGURACIÓN\n")
        
        exitos = sum(1 for _, resultado in resultados if resultado)
        total = len(resultados)
        
        print(f"Estado: {exitos}/{total} pasos completados\n")
        
        for nombre, resultado in resultados:
            estado = "✅" if resultado else "❌"
            print(f"  {estado} {nombre}")
        
        if exitos == total:
            print(f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                   ✅ IMPRESORA CONFIGURADA EXITOSAMENTE                    ║
║                                                                            ║
║  Puerto: {self.puerto}
║  Velocidad: {self.baudrate} baud
║  Configuración guardada en: config/impresora_config.py
║                                                                            ║
║  PRÓXIMOS PASOS:                                                          ║
║  1. La impresora está lista para producción                               ║
║  2. El archivo de configuración se puede usar en Django                   ║
║  3. Integración: from config.impresora_config import PUERTO_IMPRESORA     ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
            """)
        else:
            print(f"""
⚠️  CONFIGURACIÓN INCOMPLETA

Se completaron {exitos}/{total} pasos.
Revisa los errores arriba y soluciona antes de usar en producción.
            """)


if __name__ == '__main__':
    try:
        configurador = ConfiguradorImpresoraTermica()
        configurador.ejecutar()
    except KeyboardInterrupt:
        print("\n\n✅ Cancelado por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
