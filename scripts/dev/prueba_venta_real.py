#!/usr/bin/env python
"""
Script de Prueba: Venta Real con Facturación Electrónica
=========================================================

Este script simula una venta completa en el POS con:
1. Selección de estudiante
2. Agregación de productos
3. Procesamiento de pago con facturación
4. Verificación de factura generada
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
sys.path.insert(0, 'd:/anteproyecto20112025')
django.setup()

from django.utils import timezone
from gestion.models import (
    Hijo, Producto, Ventas, DetalleVenta, DatosFacturacionElect,
    Cliente, Empleado, TiposPago
)
from decimal import Decimal

print("\n" + "="*80)
print("PRUEBA DE VENTA REAL CON FACTURACIÓN ELECTRÓNICA")
print("="*80)

try:
    # ========== PASO 1: Seleccionar estudiante/cliente ==========
    print("\n[1/5] Buscando estudiantes...")
    estudiantes = list(Hijo.objects.filter(activo=True)[:5])
    
    if not estudiantes:
        print("  ⚠ No hay estudiantes. Creando uno de prueba...")
        cliente = Cliente.objects.first()
        if not cliente:
            print("  ✗ No hay clientes en el sistema. Abrir admin y crear uno.")
            sys.exit(1)
        # Crear estudiante de prueba
        estudiante = Hijo.objects.create(
            nombre="Juan Prueba",
            apellido="Test",
            id_cliente_responsable=cliente,
            grado="6to Grado",
            foto_perfil="",
            activo=True
        )
        print(f"  ✓ Estudiante creado: {estudiante.nombre}")
    else:
        estudiante = estudiantes[0]
        print(f"  ✓ Estudiante seleccionado: {estudiante.nombre} {estudiante.apellido}")
    
    # ========== PASO 2: Seleccionar productos ==========
    print("\n[2/5] Buscando productos...")
    productos_disponibles = list(Producto.objects.filter(activo=True)[:5])
    
    if not productos_disponibles:
        print("  ✗ No hay productos activos. Configure productos en admin.")
        sys.exit(1)
    
    print(f"  ✓ {len(productos_disponibles)} productos encontrados")
    
    carrito = []
    total_venta = Decimal('0')
    
    for i, producto in enumerate(productos_disponibles[:2], 1):
        cantidad = 1
        # Usar precio fijo de 5000 Guaraníes para prueba
        precio = Decimal('5000')
        subtotal = precio * cantidad
        carrito.append({
            'producto': producto,
            'cantidad': cantidad,
            'precio': precio,
            'subtotal': subtotal
        })
        total_venta += subtotal
        print(f"  ✓ Producto {i}: {producto.descripcion} (₲{precio:,.0f}) x {cantidad}")
    
    print(f"\n  Total carrito: ₲{total_venta:,.0f}")
    
    # ========== PASO 3: Procesar venta ==========
    print("\n[3/5] Procesando venta...")
    
    # Obtener empleado (cajero)
    empleado = Empleado.objects.filter(activo=True).first()
    if not empleado:
        print("  ⚠ No hay empleados. Usando empleado por defecto.")
        empleado, _ = Empleado.objects.get_or_create(
            nombre="Cajero Sistema",
            apellido="Test",
            defaults={'activo': True}
        )
    
    # Obtener tipo de pago (CONTADO)
    tipo_pago = TiposPago.objects.filter(activo=True).first()
    if not tipo_pago:
        print("  ⚠ No hay tipos de pago. Creando...")
        tipo_pago, _ = TiposPago.objects.get_or_create(
            descripcion='CONTADO',
            defaults={'activo': True}
        )
    
    # Crear venta
    venta = Ventas.objects.create(
        id_cliente=estudiante.id_cliente_responsable,
        id_hijo=estudiante,
        id_empleado_cajero=empleado,
        id_tipo_pago=tipo_pago,
        fecha=timezone.now(),
        monto_total=int(total_venta),
        estado_pago='PAGADA',
        estado='PROCESADO',
        tipo_venta='CONTADO'
    )
    print(f"  ✓ Venta creada: ID {venta.id_venta}")
    
    # Crear detalles de venta
    for item in carrito:
        DetalleVenta.objects.create(
            id_venta=venta,
            id_producto=item['producto'],
            cantidad=item['cantidad'],
            precio_unitario=int(item['precio']),
            subtotal_total=int(item['subtotal'])
        )
    
    print(f"  ✓ {len(carrito)} productos agregados")
    
    # ========== PASO 4: Emitir factura electrónica ==========
    print("\n[4/5] Emitiendo factura electrónica...")
    
    try:
        from gestion.facturacion_electronica import GeneradorXMLFactura, ClienteEkuatia
        
        # Generar XML
        generador = GeneradorXMLFactura(venta)
        xml_factura = generador.generar_xml()
        print(f"  ✓ XML generado ({len(xml_factura)} caracteres)")
        
        # Enviar a Ekuatia (simulado en testing)
        cliente_ekuatia = ClienteEkuatia()
        resultado = cliente_ekuatia.enviar_factura(xml_factura, venta.id_venta)
        
        print(f"  ✓ Respuesta Ekuatia:")
        print(f"    - Estado: {resultado.get('codigoEstado')}")
        print(f"    - CDC: {resultado.get('cdc', 'N/A')[:20]}...")
        print(f"    - Descripción: {resultado.get('descripcionEstado')}")
        
        # Guardar datos de facturación
        facturacion = DatosFacturacionElect.objects.create(
            id_venta=venta,
            cdc=resultado.get('cdc', ''),
            estado_sifen='ACEPTADA',  # En testing siempre acepta
            xml_transmitido=xml_factura,
            url_kude=f"https://sifen.set.gov.py/kude/{resultado.get('cdc', '')}",
            fecha_envio=timezone.now(),
            fecha_respuesta=timezone.now()
        )
        print(f"  ✓ Factura guardada en BD")
        print(f"    - ID: {facturacion.id_factura}")
        print(f"    - CDC: {facturacion.cdc}")
        
    except Exception as e:
        print(f"  ⚠ Error en facturación: {e}")
        facturacion = None
    
    # ========== PASO 5: Resumen final ==========
    print("\n[5/5] Resumen de la venta:")
    print(f"\n  📋 VENTA #{venta.id_venta}")
    print(f"  Estudiante: {estudiante.nombre} {estudiante.apellido}")
    print(f"  Fecha: {venta.fecha.strftime('%d/%m/%Y %H:%M')}")
    print(f"  Productos: {venta.detalles.count()}")
    print(f"  Total: ₲{venta.monto_total:,.0f}")
    
    if facturacion:
        print(f"\n  📄 FACTURA ELECTRÓNICA")
        print(f"  CDC: {facturacion.cdc}")
        print(f"  Estado: {facturacion.estado_sifen}")
        print(f"  KUDE: Disponible para descargar")
        print(f"\n  ✓ VENTA CON FACTURACIÓN EXITOSA")
    else:
        print(f"\n  ⚠ Venta completada sin facturación")
    
    print("\n" + "="*80)
    print("PRUEBA COMPLETADA")
    print("="*80)
    print("\n📊 PRÓXIMOS PASOS:")
    print("  1. Acceder a: http://localhost:8000/reportes/facturacion/dashboard/")
    print("  2. Verás la venta en el dashboard")
    print("  3. Puedes descargar el KUDE (QR)")
    print("  4. Crear más ventas para ver tendencias")
    print("\n💡 En modo TESTING, todas las facturas se simulan como 'ACEPTADAS'")
    print("   Para PRODUCCIÓN, necesitarás credenciales reales de SET/Ekuatia\n")
    
except Exception as e:
    print(f"\n✗ ERROR FATAL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
