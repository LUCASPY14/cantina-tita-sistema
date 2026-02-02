# 🖨️ Guía Completa: Integración de Impresora Térmica en Django

## Índice
1. [Instalación de Dependencias](#instalación)
2. [Prueba y Configuración](#prueba)
3. [Integración en Django](#django)
4. [Uso en Ventas](#ventas)
5. [Troubleshooting](#troubleshooting)

---

## Instalación

### 1. Dependencias Python

```bash
# Instalar librería serial
pip install pyserial

# Verificar instalación
python -c "import serial; print('✓ Serial OK')"
```

### 2. En Windows

**USB a Serial (si es necesario):**
1. Descarga el driver desde el sitio del fabricante de la impresora
2. Conecta la impresora
3. En Device Manager, verifica que aparece un puerto COM (ej: COM3)
4. Anota el número del puerto

**Verificación:**
```powershell
# PowerShell
Get-PnpDevice -PresentOnly | Where-Object { $_.Name -like '*Serial*' }
```

### 3. En Linux

```bash
# Instalar reglas USB
sudo apt-get install udev

# Agregar usuario a grupo dialout (para acceso a puertos)
sudo usermod -a -G dialout $USER

# Desconecta e conecta la impresora
# Verifica que aparece en /dev (ej: /dev/ttyUSB0)
ls -la /dev/tty*
```

---

## Prueba y Configuración

### Paso 1: Ejecutar Script de Configuración

```bash
cd d:\anteproyecto20112025
python test_conectar_impresora.py
```

**Flujo interactivo:**
```
[1/5] Detectando impresoras USB...
      → Selecciona tu impresora de la lista

[2/5] Probando conexión...
      → Debe mostrar ✓ Conexión establecida

[3/5] Enviando prueba simple...
      → Verifica que imprime un texto de prueba

[4/5] Imprimiendo ticket de prueba...
      → Verifica que imprime un ticket completo

[5/5] Guardando configuración...
      → Crea config/impresora_config.py automáticamente
```

### Paso 2: Verificar Configuración

```python
# config/impresora_config.py (generado automáticamente)
PUERTO_IMPRESORA = 'COM3'  # o '/dev/ttyUSB0' en Linux
BAUDRATE = 9600
TIMEOUT = 2

# Comandos ESC/POS predefinidos
INIT = b'\x1b\x40'
CORTE_TOTAL = b'\x1b\x69'
```

---

## Integración en Django

### Crear Módulo de Impresora

**Archivo: `gestion/impresora_manager.py`**

```python
"""
Gestor de impresora térmica para Django
Maneja conexión, impresión y recuperación de errores
"""

import serial
from django.conf import settings
from datetime import datetime
from pathlib import Path

# Importar configuración de impresora
try:
    from config.impresora_config import (
        PUERTO_IMPRESORA, BAUDRATE, TIMEOUT, INIT, CORTE_TOTAL
    )
except ImportError:
    # Valores por defecto si no está configurado
    PUERTO_IMPRESORA = None
    BAUDRATE = 9600
    TIMEOUT = 2
    INIT = b'\x1b\x40'
    CORTE_TOTAL = b'\x1b\x69'


class ImpresoraTermica:
    """Interfaz para imprimir tickets en impresora térmica"""
    
    def __init__(self):
        self.puerto_impresora = PUERTO_IMPRESORA
        self.conexion = None
        self.log_file = Path('logs') / 'impresora.log'
        self.log_file.parent.mkdir(exist_ok=True)
    
    def conectar(self):
        """Establece conexión con la impresora"""
        if not self.puerto_impresora:
            self._registrar_error("Puerto no configurado")
            return False
        
        try:
            self.conexion = serial.Serial(
                port=self.puerto_impresora,
                baudrate=BAUDRATE,
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=TIMEOUT
            )
            
            # Inicializar impresora
            self.conexion.write(INIT)
            self.conexion.flush()
            
            self._registrar("Conexión establecida")
            return True
            
        except serial.SerialException as e:
            self._registrar_error(f"Fallo conexión: {e}")
            return False
    
    def desconectar(self):
        """Cierra la conexión"""
        if self.conexion and self.conexion.is_open:
            self.conexion.close()
            self._registrar("Conexión cerrada")
    
    def imprimir_texto(self, texto, enfatizado=False, centrado=False):
        """Imprime texto en la impresora"""
        if not self.conexion or not self.conexion.is_open:
            if not self.conectar():
                return False
        
        try:
            # Aplicar formatos
            if enfatizado:
                self.conexion.write(b'\x1b\x21\x08')  # Enfatizado
            
            if centrado:
                self.conexion.write(b'\x1b\x61\x01')  # Alineación central
            
            # Enviar texto
            self.conexion.write(texto.encode('utf-8'))
            self.conexion.write(b'\n')
            
            # Resetear formatos
            self.conexion.write(b'\x1b\x21\x00')  # Normal
            self.conexion.write(b'\x1b\x61\x00')  # Izquierda
            
            self.conexion.flush()
            return True
            
        except Exception as e:
            self._registrar_error(f"Error escribir: {e}")
            return False
    
    def imprimir_ticket(self, venta_data):
        """
        Imprime un ticket completo de venta
        
        Args:
            venta_data: Dict con datos de la venta
                {
                    'numero': '001',
                    'fecha': datetime,
                    'detalles': [
                        {'producto': 'Agua', 'cantidad': 2, 'precio': 5000, 'subtotal': 10000},
                        ...
                    ],
                    'subtotal': 10000,
                    'iva': 1600,
                    'total': 11600,
                    'metodo_pago': 'EFECTIVO',
                    'cliente': 'PÚBLICO'
                }
        """
        if not self.conexion or not self.conexion.is_open:
            if not self.conectar():
                return False
        
        try:
            # ENCABEZADO
            self.imprimir_texto("═" * 40, centrado=False)
            self.imprimir_texto("CANTINA - TICKET DE VENTA", enfatizado=True, centrado=True)
            self.imprimir_texto("═" * 40, centrado=False)
            
            # Información
            fecha_str = venta_data['fecha'].strftime('%d/%m/%Y %H:%M')
            self.imprimir_texto(f"Ticket: {venta_data['numero']:<25} {fecha_str}")
            self.imprimir_texto(f"Cliente: {venta_data.get('cliente', 'PÚBLICO')}")
            
            self.imprimir_texto("─" * 40)
            
            # DETALLES
            for detalle in venta_data['detalles']:
                # Línea del producto
                nombre = detalle['producto'][:25].ljust(25)
                cantidad = str(detalle['cantidad']).rjust(3)
                precio = f"{detalle['precio']:,.0f}".rjust(8)
                
                self.imprimir_texto(f"{nombre} {cantidad} {precio}")
                
                # Subtotal del producto
                subtotal = f"{detalle['subtotal']:,.0f}".rjust(8)
                self.imprimir_texto(f"{'SUBTOTAL':<28} {subtotal}")
            
            self.imprimir_texto("─" * 40)
            
            # TOTALES
            subtotal = f"{venta_data['subtotal']:,.0f}".rjust(10)
            self.imprimir_texto(f"{'SUBTOTAL':<30} {subtotal}")
            
            if 'iva' in venta_data:
                iva = f"{venta_data['iva']:,.0f}".rjust(10)
                self.imprimir_texto(f"{'IVA (10%)':<30} {iva}")
            
            total = f"{venta_data['total']:,.0f}".rjust(10)
            self.imprimir_texto(f"{'TOTAL':<30} {total}", enfatizado=True)
            
            # PAGO
            self.imprimir_texto("─" * 40)
            self.imprimir_texto(f"Método: {venta_data['metodo_pago']}")
            
            if venta_data.get('efectivo_recibido'):
                efectivo = venta_data['efectivo_recibido']
                cambio = efectivo - venta_data['total']
                self.imprimir_texto(f"Efectivo: {efectivo:,.0f}")
                self.imprimir_texto(f"Cambio:   {cambio:,.0f}")
            
            # PIE
            self.imprimir_texto("═" * 40)
            self.imprimir_texto("¡Gracias por su compra!", centrado=True)
            self.imprimir_texto("Vuelve pronto", centrado=True)
            
            # CORTE
            self.conexion.write(CORTE_TOTAL)
            self.conexion.flush()
            
            self._registrar(f"Ticket #{venta_data['numero']} imprimido")
            return True
            
        except Exception as e:
            self._registrar_error(f"Error imprimir ticket: {e}")
            return False
    
    def _registrar(self, mensaje):
        """Registra evento en log"""
        timestamp = datetime.now().isoformat()
        log_msg = f"[{timestamp}] ✓ {mensaje}\n"
        
        with open(self.log_file, 'a') as f:
            f.write(log_msg)
    
    def _registrar_error(self, mensaje):
        """Registra error en log"""
        timestamp = datetime.now().isoformat()
        log_msg = f"[{timestamp}] ❌ {mensaje}\n"
        
        with open(self.log_file, 'a') as f:
            f.write(log_msg)


# Singleton para uso global
_impresora = None

def obtener_impresora():
    """Obtiene instancia global de impresora"""
    global _impresora
    if _impresora is None:
        _impresora = ImpresoraTermica()
    return _impresora
```

---

## Uso en Ventas

### Integración en `procesar_venta_api()`

**Archivo: `gestion/pos_general_views.py`**

```python
from gestion.impresora_manager import obtener_impresora
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@require_POST
def procesar_venta_api(request):
    """Procesa venta y imprime ticket"""
    
    try:
        # ... código de validación de restricciones ...
        
        # Procesar venta
        venta = Ventas.objects.create(
            tarjeta=tarjeta,
            total=total,
            metodo_pago=metodo_pago,
            fecha=timezone.now()
        )
        
        # Crear detalles
        detalles = []
        for item in datos_venta:
            detalle = DetalleVenta.objects.create(
                venta=venta,
                producto=item['producto'],
                cantidad=item['cantidad'],
                precio=item['precio']
            )
            detalles.append(detalle)
        
        # IMPRIMIR TICKET
        impresora = obtener_impresora()
        
        # Preparar datos para ticket
        ticket_data = {
            'numero': str(venta.id).zfill(6),
            'fecha': venta.fecha,
            'detalles': [
                {
                    'producto': d.producto.nombre,
                    'cantidad': d.cantidad,
                    'precio': d.precio,
                    'subtotal': d.cantidad * d.precio
                }
                for d in detalles
            ],
            'subtotal': venta.total,
            'iva': int(venta.total * 0.1),
            'total': venta.total + int(venta.total * 0.1),
            'metodo_pago': metodo_pago,
            'cliente': tarjeta.hijo.nombre if tarjeta else 'PÚBLICO'
        }
        
        # Intentar imprimir (no bloquea si falla)
        impresora.imprimir_ticket(ticket_data)
        
        return JsonResponse({
            'status': 'success',
            'venta_id': venta.id,
            'impreso': True
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'mensaje': str(e)
        }, status=400)
```

### Opción: Impresión Manual desde POS

```python
# En el endpoint GET del dashboard
@require_GET
def imprimir_ultimo_ticket(request):
    """Imprime el último ticket"""
    try:
        venta = Ventas.objects.latest('fecha')
        
        impresora = obtener_impresora()
        
        ticket_data = {
            'numero': str(venta.id).zfill(6),
            'fecha': venta.fecha,
            'detalles': [
                {
                    'producto': d.producto.nombre,
                    'cantidad': d.cantidad,
                    'precio': d.precio,
                    'subtotal': d.cantidad * d.precio
                }
                for d in venta.detalleventa_set.all()
            ],
            'total': venta.total,
            'metodo_pago': venta.metodo_pago,
            'cliente': venta.tarjeta.hijo.nombre if venta.tarjeta else 'PÚBLICO'
        }
        
        if impresora.imprimir_ticket(ticket_data):
            return JsonResponse({'status': 'impreso'})
        else:
            return JsonResponse({'status': 'error'}, status=500)
            
    except Exception as e:
        return JsonResponse({'status': 'error', 'mensaje': str(e)}, status=500)
```

---

## Troubleshooting

### Problema 1: "Puerto no encontrado"

**Síntomas:** 
```
❌ Error: No hay puertos USB detectados
```

**Soluciones:**
1. Verifica conexión física USB
2. En Windows: Device Manager → Puertos COM
3. En Linux: `lsusb` y `ls -la /dev/tty*`
4. Intenta otro puerto USB de la computadora
5. Reinicia el sistema

---

### Problema 2: "Error de conexión (Puerto en uso)"

**Síntomas:**
```
❌ Error de conexión: Port COM3 already in use
```

**Soluciones:**
```bash
# Windows
# 1. Cierra otros programas que usen el puerto
# 2. En Device Manager, desconecta y reconecta la impresora
# 3. En PowerShell: Get-Process | Where-Object {$_.Handles -gt 1000}

# Linux
# 1. Verifica qué proceso usa el puerto:
lsof /dev/ttyUSB0

# 2. Mata el proceso si es necesario:
sudo kill -9 <PID>
```

---

### Problema 3: "Impresora conectada pero no imprime"

**Síntomas:**
```
✓ Conexión establecida
✓ Comando enviado
❌ Pero no sale nada impreso
```

**Soluciones:**
1. Verifica que el papel está correctamente insertado
2. Comprueba que hay papel disponible
3. Apaga y enciende la impresora
4. En la configuración, verifica `BAUDRATE` (típicamente 9600)
5. Prueba con velocidades alternativas: 19200, 38400

---

### Problema 4: "Error de timeout"

**Síntomas:**
```
❌ Error: Timeout error
```

**Soluciones:**
1. Aumenta el timeout en `impresora_config.py`:
   ```python
   TIMEOUT = 5  # Aumentar de 2 a 5 segundos
   ```

2. Verifica que el cable USB no está dañado
3. Prueba en puerto USB diferente
4. En Linux, comprueba permisos:
   ```bash
   sudo chmod 666 /dev/ttyUSB0
   ```

---

### Problema 5: "Caracteres extraños o mal formateados"

**Síntomas:**
```
Texto impreso con caracteres raros: ║░▒▓ en lugar de ═══
```

**Soluciones:**
1. La impresora puede tener codificación diferente
2. Modifica la codificación en `imprimir_texto()`:
   ```python
   self.conexion.write(texto.encode('latin-1'))
   # Intenta también: 'cp437', 'ascii'
   ```

3. Usa sólo caracteres ASCII si persiste:
   ```python
   # En lugar de: "═" * 40
   # Usa: "=" * 40
   ```

---

## Monitoreo y Mantenimiento

### Revisar Logs

```bash
# Ver últimos 20 eventos
tail -20 logs/impresora.log

# Ver sólo errores
grep "❌" logs/impresora.log

# Contar eventos por día
grep "2025-01" logs/impresora.log | wc -l
```

### Estadísticas Diarias

```python
from pathlib import Path
from datetime import datetime

log_file = Path('logs/impresora.log')

exitos = len([l for l in log_file.read_text().split('\n') if '✓' in l])
errores = len([l for l in log_file.read_text().split('\n') if '❌' in l])

print(f"Hoy: {exitos} impresiones exitosas, {errores} errores")
```

### Checklist Semanal

```
□ Verificar papel en la impresora
□ Revisar logs de errores (grep "❌")
□ Limpiar cabezal de impresión (según fabricante)
□ Probar impresión de prueba: python test_conectar_impresora.py
□ Verificar conexión USB sin problemas
```

---

## Resumen de Integración

| Componente | Ubicación | Uso |
|-----------|-----------|-----|
| Script de prueba | `test_conectar_impresora.py` | Configuración inicial |
| Configuración | `config/impresora_config.py` | Parámetros de conexión |
| Gestor | `gestion/impresora_manager.py` | Interfaz principal |
| Integración POS | `gestion/pos_general_views.py` | Llamar al imprimir |
| Logs | `logs/impresora.log` | Registro de eventos |

---

## Próximos Pasos

✅ Ejecutar `python test_conectar_impresora.py`
✅ Crear `config/impresora_config.py` automáticamente
✅ Copiar `gestion/impresora_manager.py` a tu proyecto
✅ Integrar en `procesar_venta_api()` con `obtener_impresora().imprimir_ticket()`
✅ Monitores logs en `logs/impresora.log`

**¡La impresora térmica está lista para producción!** 🖨️✓
