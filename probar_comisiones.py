"""
Script para probar el cálculo automático de comisiones
Crea una venta de prueba con pago de tarjeta y verifica que la comisión se calcule
"""

import os
import django
from datetime import datetime
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from gestion.models import (
    Ventas, DetalleVenta, PagosVenta, DetalleComisionVenta,
    Cliente, Producto, MediosPago, Empleado, DocumentosTributarios,
    TiposPago
)
from django.db import connection

def print_separator(title=""):
    print("\n" + "="*70)
    if title:
        print(f"  {title}")
        print("="*70)

def print_result(message, success=True, detail=""):
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")
    if detail:
        print(f"   {detail}")

def crear_venta_prueba():
    """Crea una venta de prueba con pago de tarjeta"""
    print_separator("CREAR VENTA DE PRUEBA")
    
    try:
        # 1. Obtener datos necesarios
        cliente = Cliente.objects.first()
        if not cliente:
            print_result("No hay clientes", False)
            return None
            
        producto = Producto.objects.first()
        if not producto:
            print_result("No hay productos", False)
            return None
            
        empleado = Empleado.objects.first()
        if not empleado:
            print_result("No hay empleados", False)
            return None
        
        # Crear un nuevo documento tributario para la prueba
        from gestion.models import Timbrados, PuntosExpedicion
        
        punto = PuntosExpedicion.objects.first()
        if not punto:
            print_result("No hay puntos de expedición", False)
            return None
        
        timbrado = Timbrados.objects.first()
        if not timbrado:
            print_result("No hay timbrados", False)
            return None
        
        # Obtener el último número secuencial usado
        ultimo_doc = DocumentosTributarios.objects.order_by('-nro_secuencial').first()
        siguiente_num = (ultimo_doc.nro_secuencial + 1) if ultimo_doc else 1
        
        documento = DocumentosTributarios.objects.create(
            nro_timbrado=timbrado,
            nro_secuencial=siguiente_num
        )
        
        print_result("Documento creado", True, f"Nro: {siguiente_num}")
            
        tipo_pago = TiposPago.objects.first()
        if not tipo_pago:
            print_result("No hay tipos de pago", False)
            return None
        
        # 2. Crear la venta
        monto_total = Decimal('150000')  # Gs 150,000
        
        venta = Ventas.objects.create(
            id_documento=documento,
            id_cliente=cliente,
            id_tipo_pago=tipo_pago,
            id_empleado_cajero=empleado,
            fecha=datetime.now(),
            monto_total=int(monto_total),
            estado='Completada',
            tipo_venta='MOSTRADOR'
        )
        
        print_result("Venta creada", True, f"ID: {venta.id_venta} | Monto: Gs {monto_total:,.0f}")
        
        # 3. Crear detalle de venta
        detalle = DetalleVenta.objects.create(
            id_venta=venta,
            id_producto=producto,
            cantidad=Decimal('3.000'),
            precio_unitario_total=int(monto_total / 3),
            subtotal_total=int(monto_total),
            monto_iva=int(monto_total * Decimal('0.1'))
        )
        
        print_result("Detalle creado", True, f"Producto: {producto.descripcion} x3")
        
        return venta
        
    except Exception as e:
        print_result("Error al crear venta", False, str(e))
        import traceback
        traceback.print_exc()
        return None

def crear_pagos_con_tarjetas(venta):
    """Crea pagos con diferentes medios de pago para probar comisiones"""
    print_separator("CREAR PAGOS CON TARJETAS")
    
    if not venta:
        print_result("No hay venta para crear pagos", False)
        return []
    
    # Dividir el pago en 3 partes con diferentes medios
    pagos_config = [
        {
            'medio': 'TARJETA DEBITO /QR',
            'monto': Decimal('50000'),  # Gs 50,000
            'esperado': Decimal('900')  # 1.8% = 900
        },
        {
            'medio': 'TARJETA CREDITO / QR',
            'monto': Decimal('50000'),  # Gs 50,000
            'esperado': Decimal('1750')  # 3.5% = 1,750
        },
        {
            'medio': 'GIROS TIGO',
            'monto': Decimal('50000'),  # Gs 50,000
            'esperado': Decimal('2500')  # 2% + 1,500 = 2,500
        },
    ]
    
    pagos_creados = []
    
    for config in pagos_config:
        try:
            medio = MediosPago.objects.get(descripcion=config['medio'])
            
            # Crear el pago (el trigger calculará la comisión)
            pago = PagosVenta.objects.create(
                id_venta=venta,
                id_medio_pago=medio,
                monto_aplicado=int(config['monto']),
                fecha_pago=datetime.now(),
                referencia_transaccion=f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            
            pagos_creados.append(pago)
            
            print_result(
                f"Pago: {config['medio']}", 
                True, 
                f"ID: {pago.id_pago_venta} | Monto: Gs {config['monto']:,.0f}"
            )
            
        except Exception as e:
            print_result(f"Error: {config['medio']}", False, str(e))
    
    return pagos_creados

def verificar_comisiones_calculadas(pagos):
    """Verifica que las comisiones se hayan calculado automáticamente"""
    print_separator("VERIFICACIÓN DE COMISIONES CALCULADAS")
    
    total_comisiones = Decimal('0')
    
    for pago in pagos:
        # Buscar comisión calculada
        comision = DetalleComisionVenta.objects.filter(id_pago_venta=pago).first()
        
        if comision:
            print_result(
                f"Comisión calculada: {pago.id_medio_pago.descripcion}",
                True,
                f"Gs {comision.monto_comision_calculada:,.2f} ({comision.porcentaje_aplicado*100:.2f}%)"
            )
            total_comisiones += comision.monto_comision_calculada
        else:
            print_result(
                f"Sin comisión: {pago.id_medio_pago.descripcion}",
                False,
                "El trigger no calculó la comisión"
            )
    
    if total_comisiones > 0:
        print(f"\n💰 Total comisiones: Gs {total_comisiones:,.2f}")
        return True
    else:
        print("\n⚠️  No se calcularon comisiones")
        return False

def mostrar_resumen_detallado():
    """Muestra un resumen detallado de todas las comisiones"""
    print_separator("RESUMEN DETALLADO DE COMISIONES")
    
    from django.db import connection
    cursor = connection.cursor()
    
    cursor.execute("""
        SELECT 
            pv.ID_Pago_Venta,
            v.ID_Venta,
            v.Fecha,
            mp.Descripcion as Medio_Pago,
            pv.Monto_Aplicado,
            COALESCE(dc.Monto_Comision_Calculada, 0) as Comision,
            COALESCE(dc.Porcentaje_Aplicado * 100, 0) as Porcentaje,
            CASE 
                WHEN dc.ID_Detalle_Comision IS NOT NULL THEN 'SÍ'
                ELSE 'NO'
            END as Tiene_Comision
        FROM Pagos_Venta pv
        JOIN Ventas v ON pv.ID_Venta = v.ID_Venta
        JOIN Medios_Pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
        LEFT JOIN Detalle_Comision_Venta dc ON pv.ID_Pago_Venta = dc.ID_Pago_Venta
        ORDER BY pv.ID_Pago_Venta DESC
        LIMIT 10
    """)
    
    rows = cursor.fetchall()
    
    if not rows:
        print("⚠️  No hay pagos registrados")
        return
    
    print("\n📊 Últimos 10 pagos:")
    print(f"\n{'ID Pago':<10} {'Venta':<8} {'Medio Pago':<25} {'Monto':>12} {'Comisión':>12} {'%':>8} {'Calc':>5}")
    print("-" * 90)
    
    total_monto = 0
    total_comision = 0
    
    for row in rows:
        total_monto += row[4]
        total_comision += row[5]
        
        comision_str = f"Gs {row[5]:>8,.0f}" if row[5] > 0 else "-"
        porcentaje_str = f"{row[6]:.2f}%" if row[6] > 0 else "-"
        
        print(f"{row[0]:<10} {row[1]:<8} {row[2]:<25} Gs {row[4]:>9,} {comision_str} {porcentaje_str:>8} {row[7]:>5}")
    
    print("-" * 90)
    print(f"{'TOTAL':<44} Gs {total_monto:>9,} Gs {total_comision:>8,.0f}")
    
    # Estadísticas
    cursor.execute("""
        SELECT 
            COUNT(*) as Total_Pagos,
            COUNT(dc.ID_Detalle_Comision) as Pagos_Con_Comision,
            SUM(pv.Monto_Aplicado) as Total_Monto,
            SUM(COALESCE(dc.Monto_Comision_Calculada, 0)) as Total_Comisiones
        FROM Pagos_Venta pv
        LEFT JOIN Detalle_Comision_Venta dc ON pv.ID_Pago_Venta = dc.ID_Pago_Venta
    """)
    
    stats = cursor.fetchone()
    
    print(f"\n📈 Estadísticas generales:")
    print(f"  - Total pagos registrados: {stats[0]}")
    print(f"  - Pagos con comisión: {stats[1]}")
    print(f"  - Monto total procesado: Gs {stats[2]:,}" if stats[2] else "  - Monto total procesado: Gs 0")
    print(f"  - Total comisiones: Gs {stats[3]:,.2f}" if stats[3] else "  - Total comisiones: Gs 0")
    
    if stats[2] and stats[2] > 0:
        porcentaje_efectivo = (stats[3] / stats[2]) * 100
        print(f"  - Comisión promedio efectiva: {porcentaje_efectivo:.2f}%")

def limpiar_datos_prueba():
    """Limpia los datos de prueba creados"""
    print_separator("LIMPIEZA DE DATOS DE PRUEBA")
    
    respuesta = input("\n¿Deseas eliminar las ventas de prueba? (s/n): ")
    
    if respuesta.lower() == 's':
        try:
            # Eliminar comisiones
            comisiones_deleted = DetalleComisionVenta.objects.filter(
                id_pago_venta__id_venta__tipo_venta='MOSTRADOR'
            ).delete()
            
            # Eliminar pagos
            pagos_deleted = PagosVenta.objects.filter(
                id_venta__tipo_venta='MOSTRADOR',
                referencia_transaccion__startswith='TEST-'
            ).delete()
            
            # Eliminar detalles
            detalles_deleted = DetalleVenta.objects.filter(
                id_venta__tipo_venta='MOSTRADOR'
            ).delete()
            
            # Eliminar ventas
            ventas_deleted = Ventas.objects.filter(
                tipo_venta='MOSTRADOR'
            ).delete()
            
            print_result("Datos de prueba eliminados", True, 
                        f"Ventas: {ventas_deleted[0]}, Comisiones: {comisiones_deleted[0]}")
        except Exception as e:
            print_result("Error al limpiar", False, str(e))
    else:
        print("✅ Datos de prueba conservados")

def main():
    print("\n" + "="*70)
    print("  PRUEBA DE CÁLCULO AUTOMÁTICO DE COMISIONES")
    print("  Sistema Cantina Tita - Fase 1")
    print("="*70)
    
    try:
        # 1. Crear venta de prueba
        venta = crear_venta_prueba()
        
        if not venta:
            print("\n⚠️  No se pudo crear la venta de prueba")
            return
        
        # 2. Crear pagos con diferentes tarjetas
        pagos = crear_pagos_con_tarjetas(venta)
        
        if not pagos:
            print("\n⚠️  No se pudieron crear los pagos")
            return
        
        # 3. Verificar que las comisiones se calcularon
        comisiones_ok = verificar_comisiones_calculadas(pagos)
        
        # 4. Mostrar resumen detallado
        mostrar_resumen_detallado()
        
        print("\n" + "="*70)
        if comisiones_ok:
            print("  ✅ PRUEBA EXITOSA - COMISIONES CALCULADAS AUTOMÁTICAMENTE")
        else:
            print("  ❌ PRUEBA FALLIDA - COMISIONES NO CALCULADAS")
        print("="*70)
        
        # 5. Opción de limpiar datos
        limpiar_datos_prueba()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
