#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST MÓDULO - VENTAS DIRECTAS
==============================
Pruebas del sistema de ventas sin tarjeta.

COBERTURA:
- Venta en efectivo
- Venta a crédito (cuenta corriente)
- Venta con múltiples medios de pago
- Generación de documentos tributarios
- Consultas y reportes de ventas
"""

import MySQLdb
from datetime import datetime
from decimal import Decimal

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'passwd': 'L01G05S33Vice.42',
    'db': 'cantinatitadb',
    'charset': 'utf8mb4'
}

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")

def print_success(text):
    print(f"✅ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def print_error(text):
    print(f"❌ {text}")

# ============================================================================
# TEST 1: VENTA EN EFECTIVO
# ============================================================================

def test_venta_efectivo():
    """Prueba venta directa en efectivo"""
    print_header("TEST 1: Venta en Efectivo")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar cliente y empleado
        cursor.execute("SELECT ID_Cliente FROM clientes WHERE Activo = TRUE LIMIT 1")
        cliente = cursor.fetchone()
        
        cursor.execute("SELECT ID_Empleado FROM empleados WHERE Activo = TRUE LIMIT 1")
        empleado = cursor.fetchone()
        
        if not cliente or not empleado:
            print_error("No hay datos necesarios")
            return False
        
        id_cliente = cliente[0]
        id_empleado = empleado[0]
        
        # Buscar productos disponibles
        cursor.execute("""
            SELECT p.ID_Producto, p.Descripcion, hp.Precio_Nuevo
            FROM productos p
            INNER JOIN historico_precios hp ON p.ID_Producto = hp.ID_Producto
            WHERE p.Activo = TRUE
            AND hp.Fecha_Cambio = (
                SELECT MAX(Fecha_Cambio)
                FROM historico_precios
                WHERE ID_Producto = p.ID_Producto
            )
            LIMIT 3
        """)
        
        productos = cursor.fetchall()
        
        if not productos:
            print_error("No hay productos disponibles")
            return False
        
        print_info(f"Productos seleccionados: {len(productos)}")
        
        # Calcular total de la venta PRIMERO
        total_venta = 0
        for id_prod, desc, precio in productos:
            cantidad = 2
            precio_unitario = int(precio)
            subtotal = precio_unitario * cantidad
            total_venta += subtotal
        
        # Crear documento tributario para esta venta
        cursor.execute("""
            INSERT INTO documentos_tributarios
            (Nro_Timbrado, Nro_Secuencial, Fecha_Emision, Monto_Total, Monto_Exento, Monto_Gravado_5, Monto_IVA_5, Monto_Gravado_10, Monto_IVA_10)
            VALUES ('12345678', FLOOR(RAND() * 1000000), NOW(), %s, 0, 0, 0, 0, 0)
        """, (total_venta,))
        
        id_documento = cursor.lastrowid
        
        # Crear venta con total calculado
        cursor.execute("""
            INSERT INTO ventas
            (ID_Cliente, ID_Documento, ID_Tipo_Pago, Fecha, Tipo_Venta, Monto_Total, Estado, ID_Empleado_Cajero)
            VALUES (%s, %s, 2, NOW(), 'Directa', %s, 'Completada', %s)
        """, (id_cliente, id_documento, total_venta, id_empleado))
        
        id_venta = cursor.lastrowid
        print_info(f"Venta creada: ID {id_venta}")
        
        # Agregar detalles
        for id_prod, desc, precio in productos:
            cantidad = 2
            precio_unitario = int(precio)
            subtotal = precio_unitario * cantidad
            
            cursor.execute("""
                INSERT INTO detalle_venta
                (ID_Venta, ID_Producto, Cantidad, Precio_Unitario_Total, Subtotal_Total, Monto_IVA)
                VALUES (%s, %s, %s, %s, %s, 0)
            """, (id_venta, id_prod, cantidad, precio_unitario, subtotal))
            
            print_info(f"  + {desc[:30]}: {cantidad} x Gs. {precio_unitario:,.0f} = Gs. {subtotal:,.0f}")
        
        # Registrar pago en efectivo (ID_Medio_Pago=1 para EFECTIVO)
        cursor.execute("""
            INSERT INTO pagos_venta
            (ID_Venta, ID_Medio_Pago, Monto_Aplicado, Fecha_Pago)
            VALUES (%s, 1, %s, NOW())
        """, (id_venta, total_venta))
        
        id_pago = cursor.lastrowid
        
        print_success(f"\n✅ Venta en efectivo completada")
        print_info(f"   ID Venta: {id_venta}")
        print_info(f"   Total: Gs. {total_venta:,.0f}")
        print_info(f"   ID Pago: {id_pago}")
        print_info(f"   Estado: Completada")
        
        conn.rollback()
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# TEST 2: VENTA A CRÉDITO
# ============================================================================

def test_venta_credito():
    """Prueba venta a crédito (cuenta corriente)"""
    print_header("TEST 2: Venta a Crédito")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar cliente y empleado
        cursor.execute("""
            SELECT c.ID_Cliente, c.Nombres, c.Apellidos
            FROM clientes c
            WHERE c.Activo = TRUE
            LIMIT 1
        """)
        
        cliente = cursor.fetchone()
        
        cursor.execute("SELECT ID_Empleado FROM empleados WHERE Activo = TRUE LIMIT 1")
        empleado = cursor.fetchone()
        
        if not cliente or not empleado:
            print_error("No hay datos necesarios")
            return False
        
        id_cliente, nombres, apellidos = cliente
        id_empleado = empleado[0]
        
        print_info(f"Cliente: {nombres} {apellidos}")
        
        # Buscar productos
        cursor.execute("""
            SELECT p.ID_Producto, p.Descripcion, hp.Precio_Nuevo
            FROM productos p
            INNER JOIN historico_precios hp ON p.ID_Producto = hp.ID_Producto
            WHERE p.Activo = TRUE
            AND hp.Fecha_Cambio = (
                SELECT MAX(Fecha_Cambio)
                FROM historico_precios
                WHERE ID_Producto = p.ID_Producto
            )
            LIMIT 2
        """)
        
        productos = cursor.fetchall()
        
        if not productos:
            print_error("No hay productos disponibles")
            return False
        
        print_info(f"Productos seleccionados: {len(productos)}")
        
        # Calcular total PRIMERO
        total_venta = 0
        for id_prod, desc, precio in productos:
            cantidad = 3
            precio_unitario = int(precio)
            subtotal = precio_unitario * cantidad
            total_venta += subtotal
        
        # Crear documento tributario para esta venta
        cursor.execute("""
            INSERT INTO documentos_tributarios
            (Nro_Timbrado, Nro_Secuencial, Fecha_Emision, Monto_Total, Monto_Exento, Monto_Gravado_5, Monto_IVA_5, Monto_Gravado_10, Monto_IVA_10)
            VALUES ('12345678', FLOOR(RAND() * 1000000), NOW(), %s, 0, 0, 0, 0, 0)
        """, (total_venta,))
        
        id_documento = cursor.lastrowid
        
        # Crear venta con total calculado
        cursor.execute("""
            INSERT INTO ventas
            (ID_Cliente, ID_Documento, ID_Tipo_Pago, Fecha, Tipo_Venta, Monto_Total, Estado, ID_Empleado_Cajero)
            VALUES (%s, %s, 1, NOW(), 'Credito', %s, 'Pendiente', %s)
        """, (id_cliente, id_documento, total_venta, id_empleado))
        
        id_venta = cursor.lastrowid
        
        # Agregar detalles
        print_info("\n   🛍️  Productos:")
        for id_prod, desc, precio in productos:
            cantidad = 3
            precio_unitario = int(precio)
            subtotal = precio_unitario * cantidad
            
            cursor.execute("""
                INSERT INTO detalle_venta
                (ID_Venta, ID_Producto, Cantidad, Precio_Unitario_Total, Subtotal_Total, Monto_IVA)
                VALUES (%s, %s, %s, %s, %s, 0)
            """, (id_venta, id_prod, cantidad, precio_unitario, subtotal))
            
            print_info(f"     {desc[:30]}: {cantidad} x Gs. {precio_unitario:,.0f}")
        
        # Registrar en cuenta corriente (tabla correcta: cta_corriente)
        cursor.execute("""
            INSERT INTO cta_corriente
            (ID_Cliente, ID_Venta, Tipo_Movimiento, Monto, Fecha, Referencia_Doc)
            VALUES (%s, %s, 'Cargo', %s, NOW(), %s)
        """, (id_cliente, id_venta, total_venta, f'Venta #{id_venta}'))
        
        id_movimiento = cursor.lastrowid
        
        print_success(f"\n✅ Venta a crédito registrada")
        print_info(f"   ID Venta: {id_venta}")
        print_info(f"   Total: Gs. {total_venta:,.0f}")
        print_info(f"   Estado: Pendiente de pago")
        print_info(f"   Cuenta corriente: Movimiento #{id_movimiento}")
        
        conn.rollback()
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# TEST 3: VENTA CON MÚLTIPLES MEDIOS DE PAGO
# ============================================================================

def test_venta_multiple_pago():
    """Prueba venta con múltiples medios de pago"""
    print_header("TEST 3: Venta con Múltiples Medios de Pago")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar cliente y empleado
        cursor.execute("SELECT ID_Cliente FROM clientes WHERE Activo = TRUE LIMIT 1")
        cliente = cursor.fetchone()
        
        cursor.execute("SELECT ID_Empleado FROM empleados WHERE Activo = TRUE LIMIT 1")
        empleado = cursor.fetchone()
        
        if not cliente or not empleado:
            print_error("No hay datos necesarios")
            return False
        
        id_cliente = cliente[0]
        id_empleado = empleado[0]
        
        # Buscar producto
        cursor.execute("""
            SELECT p.ID_Producto, p.Descripcion, hp.Precio_Nuevo
            FROM productos p
            INNER JOIN historico_precios hp ON p.ID_Producto = hp.ID_Producto
            WHERE p.Activo = TRUE
            AND hp.Fecha_Cambio = (
                SELECT MAX(Fecha_Cambio)
                FROM historico_precios
                WHERE ID_Producto = p.ID_Producto
            )
            LIMIT 1
        """)
        
        producto = cursor.fetchone()
        
        if not producto:
            print_error("No hay productos disponibles")
            return False
        
        id_prod, desc, precio = producto
        cantidad = 5
        precio_unitario = int(precio)
        total_venta = precio_unitario * cantidad
        
        print_info(f"Producto: {desc}")
        print_info(f"Total: Gs. {total_venta:,.0f}")
        
        # Crear documento tributario NUEVO para esta venta
        cursor.execute("""
            INSERT INTO documentos_tributarios
            (Nro_Timbrado, Nro_Secuencial, Fecha_Emision, Monto_Total, Monto_Exento, Monto_Gravado_5, Monto_IVA_5, Monto_Gravado_10, Monto_IVA_10)
            VALUES ('12345678', FLOOR(RAND() * 1000000), NOW(), %s, 0, 0, 0, 0, 0)
        """, (total_venta,))
        
        id_documento = cursor.lastrowid
        
        # Crear venta
        cursor.execute("""
            INSERT INTO ventas
            (ID_Cliente, ID_Documento, ID_Tipo_Pago, Fecha, Tipo_Venta, Monto_Total, Estado, ID_Empleado_Cajero)
            VALUES (%s, %s, 2, NOW(), 'Directa', %s, 'Completada', %s)
        """, (id_cliente, id_documento, total_venta, id_empleado))
        
        id_venta = cursor.lastrowid
        
        # Agregar detalle
        precio_unitario = int(precio)
        subtotal = precio_unitario * cantidad
        
        cursor.execute("""
            INSERT INTO detalle_venta
            (ID_Venta, ID_Producto, Cantidad, Precio_Unitario_Total, Subtotal_Total, Monto_IVA)
            VALUES (%s, %s, %s, %s, %s, 0)
        """, (id_venta, id_prod, cantidad, precio_unitario, subtotal))
        
        # Registrar múltiples pagos
        medios_pago = [
            (1, 'Efectivo', total_venta * 0.4),        # 40%
            (3, 'Tarjeta Débito', total_venta * 0.3),  # 30%
            (4, 'Tarjeta Crédito', total_venta * 0.3)  # 30%
        ]
        
        print_info("\n   💳 Medios de pago:")
        total_pagado = 0
        
        for id_medio, medio, monto in medios_pago:
            cursor.execute("""
                INSERT INTO pagos_venta
                (ID_Venta, ID_Medio_Pago, Monto_Aplicado, Fecha_Pago)
                VALUES (%s, %s, %s, NOW())
            """, (id_venta, id_medio, monto))
            
            total_pagado += monto
            porcentaje = (monto / total_venta) * 100
            print_info(f"     {medio}: Gs. {monto:,.0f} ({porcentaje:.0f}%)")
        
        print_success(f"\n✅ Venta con múltiples pagos completada")
        print_info(f"   ID Venta: {id_venta}")
        print_info(f"   Total venta: Gs. {total_venta:,.0f}")
        print_info(f"   Total pagado: Gs. {total_pagado:,.0f}")
        print_info(f"   Medios utilizados: {len(medios_pago)}")
        
        conn.rollback()
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# TEST 4: GENERACIÓN DE DOCUMENTOS TRIBUTARIOS
# ============================================================================

def test_documentos_tributarios():
    """Prueba la generación de documentos en ventas"""
    print_header("TEST 4: Generación de Documentos Tributarios")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Consultar documentos disponibles
        cursor.execute("""
            SELECT 
                dt.ID_Documento,
                dt.Nro_Timbrado,
                dt.Nro_Secuencial,
                dt.Fecha_Emision
            FROM documentos_tributarios dt
            WHERE dt.Fecha_Emision > DATE_SUB(CURDATE(), INTERVAL 90 DAY)
            ORDER BY dt.Fecha_Emision DESC
            LIMIT 5
        """)
        
        documentos = cursor.fetchall()
        
        print_success(f"✅ {len(documentos)} documento(s) disponible(s)")
        
        if documentos:
            print("\n   📄 Documentos tributarios activos:")
            print(f"   {'ID':<10} {'Timbrado':<15} {'Secuencial':<15} {'Fecha Emisión':<15}")
            print(f"   {'-'*60}")
            
            for doc in documentos:
                id_doc, timbrado, secuencial, fecha = doc
                fecha_str = fecha.strftime('%d/%m/%Y')
                
                print(f"   {id_doc:<10} {timbrado:<15} {secuencial:<15} {fecha_str:<15}")
        
        # Buscar ventas con documento
        cursor.execute("""
            SELECT 
                v.ID_Venta,
                dt.Nro_Secuencial,
                v.Monto_Total,
                v.Fecha
            FROM ventas v
            INNER JOIN documentos_tributarios dt ON v.ID_Documento = dt.ID_Documento
            ORDER BY v.Fecha DESC
            LIMIT 5
        """)
        
        ventas_doc = cursor.fetchall()
        
        if ventas_doc:
            print(f"\n   📋 Últimas ventas con documento:")
            print(f"   {'Venta':<10} {'Secuencial':<15} {'Monto':>20} {'Fecha':<20}")
            print(f"   {'-'*70}")
            
            for venta in ventas_doc:
                id_v, secuencial, monto, fecha = venta
                fecha_str = fecha.strftime('%d/%m/%Y %H:%M')
                print(f"   #{id_v:<9} {secuencial:<15} Gs. {float(monto):>15,.0f} {fecha_str:<20}")
        
        # Verificar documentos recientes
        cursor.execute("""
            SELECT 
                ID_Documento,
                Nro_Timbrado,
                Nro_Secuencial,
                Fecha_Emision
            FROM documentos_tributarios
            WHERE Fecha_Emision > DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            ORDER BY Fecha_Emision DESC
            LIMIT 10
        """)
        
        proximos_vencer = cursor.fetchall()
        
        if proximos_vencer:
            print(f"\n   📄 Documentos recientes emitidos:")
            for doc in proximos_vencer:
                id_d, timbrado, secuencial, fecha = doc
                print_info(f"     Doc #{id_d}: Timbrado {timbrado}, Nro {secuencial}, Fecha {fecha}")
        
        conn.rollback()
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# TEST 5: REPORTES DE VENTAS
# ============================================================================

def test_reportes_ventas():
    """Prueba la generación de reportes de ventas"""
    print_header("TEST 5: Reportes de Ventas")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Resumen de ventas por tipo
        cursor.execute("""
            SELECT 
                Tipo_Venta,
                COUNT(*) as cantidad,
                SUM(Monto_Total) as total,
                AVG(Monto_Total) as promedio
            FROM ventas
            WHERE Fecha >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY Tipo_Venta
        """)
        
        por_tipo = cursor.fetchall()
        
        print_success("✅ Reporte generado")
        
        if por_tipo:
            print("\n   📊 Ventas por tipo (últimos 30 días):")
            print(f"   {'Tipo':<20} {'Cantidad':>10} {'Total':>20} {'Promedio':>20}")
            print(f"   {'-'*75}")
            
            for tipo, cant, total, prom in por_tipo:
                print(f"   {tipo:<20} {cant:>10} Gs. {float(total):>15,.0f} Gs. {float(prom):>15,.0f}")
        
        # Ventas por estado
        cursor.execute("""
            SELECT 
                Estado,
                COUNT(*) as cantidad,
                SUM(Monto_Total) as total
            FROM ventas
            WHERE Fecha >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY Estado
        """)
        
        por_estado = cursor.fetchall()
        
        if por_estado:
            print(f"\n   📈 Ventas por estado:")
            for estado, cant, total in por_estado:
                print_info(f"     {estado}: {cant} ventas - Gs. {float(total):,.0f}")
        
        # Top productos vendidos
        cursor.execute("""
            SELECT 
                p.Descripcion,
                SUM(dv.Cantidad) as unidades,
                SUM(dv.Cantidad * dv.Precio_Unitario_Total) as total
            FROM detalle_venta dv
            INNER JOIN productos p ON dv.ID_Producto = p.ID_Producto
            INNER JOIN ventas v ON dv.ID_Venta = v.ID_Venta
            WHERE v.Fecha >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            GROUP BY p.ID_Producto, p.Descripcion
            ORDER BY unidades DESC
            LIMIT 10
        """)
        
        top_productos = cursor.fetchall()
        
        if top_productos:
            print(f"\n   🏆 Top 10 productos más vendidos:")
            print(f"   {'Producto':<35} {'Unidades':>10} {'Total':>20}")
            print(f"   {'-'*70}")
            
            for desc, unidades, total in top_productos:
                prod = desc[:33]
                print(f"   {prod:<35} {int(unidades):>10} Gs. {float(total):>15,.0f}")
        
        # Estadísticas generales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_ventas,
                SUM(Monto_Total) as total_facturado,
                AVG(Monto_Total) as ticket_promedio,
                COUNT(DISTINCT ID_Cliente) as clientes_unicos
            FROM ventas
            WHERE Fecha >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """)
        
        stats = cursor.fetchone()
        
        if stats:
            total_v, facturado, promedio, clientes = stats
            
            print(f"\n   💰 Estadísticas generales (30 días):")
            print(f"   Total ventas: {total_v}")
            print(f"   Total facturado: Gs. {float(facturado):,.0f}")
            print(f"   Ticket promedio: Gs. {float(promedio):,.0f}")
            print(f"   Clientes únicos: {clientes}")
        
        conn.rollback()
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# EJECUTAR TODOS LOS TESTS
# ============================================================================

def main():
    print("\n")
    print("█" * 70)
    print("█                                                                    █")
    print("█                TEST COMPLETO - VENTAS DIRECTAS                     █")
    print("█                                                                    █")
    print("█" * 70)
    
    tests = [
        ("Venta en Efectivo", test_venta_efectivo),
        ("Venta a Crédito", test_venta_credito),
        ("Venta Múltiple Pago", test_venta_multiple_pago),
        ("Documentos Tributarios", test_documentos_tributarios),
        ("Reportes de Ventas", test_reportes_ventas),
    ]
    
    resultados = []
    
    for nombre, test_func in tests:
        try:
            resultado = test_func()
            resultados.append((nombre, resultado))
        except Exception as e:
            print_error(f"Error crítico en {nombre}: {str(e)}")
            resultados.append((nombre, False))
    
    # Resumen
    print_header("RESUMEN DE RESULTADOS")
    
    exitosos = sum(1 for _, r in resultados if r)
    total = len(resultados)
    
    for nombre, resultado in resultados:
        estado = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{estado} - {nombre}")
    
    print(f"\n{'='*70}")
    print(f"Total: {exitosos}/{total} tests exitosos ({exitosos/total*100:.1f}%)")
    print(f"{'='*70}")
    
    if exitosos == total:
        print("\n🎉 ¡PERFECTO! Todos los tests de ventas directas pasaron.")
    else:
        print(f"\n⚠️  {total - exitosos} test(s) fallaron.")
    
    print("\n")

if __name__ == "__main__":
    main()
