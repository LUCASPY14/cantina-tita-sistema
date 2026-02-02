#!/usr/bin/env python
"""
Script de prueba: Procesar venta en POS Bootstrap
Simula una venta completa desde tarjeta hasta producto
"""
import os
import django
import json
import sys

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import Tarjeta, Hijo, Ventas, DetalleVenta, Producto
from django.test import Client

print("=" * 70)
print("[TEST] Procesar Venta en POS Bootstrap")
print("=" * 70)

# 1. Obtener una tarjeta activa
print("\n[1] Buscando tarjeta activa...")
tarjeta = Tarjeta.objects.filter(estado='Activa').select_related('id_hijo').first()

if not tarjeta:
    print("[ERROR] No hay tarjetas activas")
    exit(1)

print(f"[OK] Tarjeta encontrada: {tarjeta.nro_tarjeta}")
print(f"     Estudiante: {tarjeta.id_hijo.nombre_completo}")
print(f"     Saldo actual: Gs. {tarjeta.saldo_actual}")

# 2. Obtener productos activos
print("\n[2] Buscando productos activos...")
productos = Producto.objects.filter(activo=True).select_related('stock')[:3]

if not productos:
    print("[ERROR] No hay productos activos")
    exit(1)

print(f"[OK] {len(productos)} productos encontrados")

# 3. Preparar carrito
print("\n[3] Preparando carrito...")
carrito = []
monto_total = 0

for p in productos:
    precio = 5000  # Precio de prueba
    cantidad = 1
    subtotal = precio * cantidad
    
    carrito.append({
        'id_producto': p.id_producto,
        'cantidad': cantidad,
        'precio_unitario': precio
    })
    
    monto_total += subtotal
    print(f"     • {p.descripcion}: Gs. {precio} x {cantidad} = Gs. {subtotal}")

print(f"[OK] Total del carrito: Gs. {monto_total}")

# 4. Simular POST a procesar-venta
print("\n[4] Simulando POST a /pos/procesar-venta/...")

request_data = {
    'id_hijo': tarjeta.id_hijo.id_hijo,
    'productos': carrito,
    'pagos': [
        {
            'id_medio_pago': 1,  # Efectivo
            'monto': monto_total,
            'nro_tarjeta': tarjeta.nro_tarjeta
        }
    ],
    'tipo_venta': 'CONTADO',
    'emitir_factura': False,
    'medio_pago_id': 1
}

print(f"[REQUEST] JSON:")
print(json.dumps(request_data, indent=2))

# 5. Usar cliente Django para probar
print("\n[5] Enviando POST...")
client = Client()

try:
    response = client.post(
        '/pos/procesar-venta/',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    
    result = response.json()
    
    if result.get('success'):
        print("[OK] VENTA PROCESADA CORRECTAMENTE!")
        print(f"     Venta #: {result.get('id_venta')}")
        print(f"     Monto: Gs. {result.get('monto_total')}")
        print(f"     Factura: {result.get('nro_factura', 'No generada')}")
        
        # Verificar que la venta se creó
        print("\n[6] Verificando BD...")
        venta = Ventas.objects.filter(id_venta=result.get('id_venta')).first()
        
        if venta:
            print(f"[OK] Venta registrada en BD")
            print(f"     Cliente: {venta.id_cliente.nombre_completo}")
            print(f"     Detalles: {venta.detalles.count()} productos")
            print(f"     Pagos: {venta.pagos.count()}")
        else:
            print("[ERROR] Venta no encontrada en BD")
    else:
        print(f"[ERROR] {result.get('error')}")
        
except Exception as e:
    print(f"[ERROR] Exception: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("[DONE] TEST COMPLETADO")
print("=" * 70)
