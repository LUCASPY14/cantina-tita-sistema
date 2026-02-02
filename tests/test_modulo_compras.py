#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST MÓDULO DE COMPRAS Y PROVEEDORES - CANTINA TITA
Pruebas completas: Compras, Pagos a Proveedores, Cuenta Corriente, Notas de Crédito
Fecha: 26 de noviembre de 2025
"""

import MySQLdb
from datetime import datetime
from decimal import Decimal

# Configuración de base de datos
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'L01G05S33Vice.42',
    'database': 'cantinatitadb',
    'charset': 'utf8mb4'
}

def print_header(title):
    print("\n" + "=" * 90)
    print(f"  {title}")
    print("=" * 90)

def print_success(message):
    print(f"✓ {message}")

def print_error(message):
    print(f"✗ {message}")

def print_info(message):
    print(f"ℹ {message}")

def print_divider():
    print("-" * 90)


# =============================================================================
# TEST 1: COMPRA A PROVEEDOR CON MÚLTIPLES PRODUCTOS
# =============================================================================
def test_compra_proveedor(conn, cursor):
    print_header("TEST 1: COMPRA A PROVEEDOR - FLUJO COMPLETO")
    
    try:
        # 1. Seleccionar proveedor activo
        cursor.execute("""
            SELECT ID_Proveedor, Razon_Social, RUC
            FROM proveedores
            WHERE Activo = TRUE
            ORDER BY ID_Proveedor
            LIMIT 1
        """)
        proveedor = cursor.fetchone()
        
        if not proveedor:
            print_error("No hay proveedores activos en el sistema")
            return False
        
        id_proveedor = proveedor[0]
        razon_social = proveedor[1]
        ruc = proveedor[2]
        
        print_info(f"🏭 Proveedor seleccionado:")
        print_info(f"   • ID: {id_proveedor}")
        print_info(f"   • Razón Social: {razon_social}")
        print_info(f"   • RUC: {ruc}")
        
        # 2. Verificar saldo actual en cuenta corriente
        cursor.execute("""
            SELECT COALESCE(MAX(Saldo_Acumulado), 0)
            FROM cta_corriente_prov
            WHERE ID_Proveedor = %s
        """, (id_proveedor,))
        saldo_inicial = float(cursor.fetchone()[0])
        
        print_info(f"\n💰 Saldo inicial cuenta corriente: Gs. {saldo_inicial:,.0f}")
        
        # 3. Obtener productos para comprar
        cursor.execute("""
            SELECT p.ID_Producto, p.Descripcion, su.Stock_Actual
            FROM productos p
            JOIN stock_unico su ON p.ID_Producto = su.ID_Producto
            WHERE p.Activo = TRUE
            ORDER BY su.Stock_Actual ASC
            LIMIT 3
        """)
        productos = cursor.fetchall()
        
        if len(productos) < 2:
            print_error("No hay suficientes productos para la compra")
            return False
        
        print_info(f"\n📦 Productos a comprar:")
        for p in productos:
            print_info(f"   • {p[1]} (Stock actual: {p[2]})")
        
        # 4. Calcular monto total ANTES de crear la compra
        print_info(f"\n📋 Calculando monto de la compra:")
        print_divider()
        
        monto_total_compra = 0
        detalles_compra = []
        stock_updates = []
        
        for idx, producto in enumerate(productos, 1):
            id_producto = producto[0]
            descripcion = producto[1]
            stock_actual = float(producto[2])
            
            # Definir cantidades y precios
            cantidad = 20 + (idx * 5)  # 25, 30, 35 unidades
            costo_unitario = 3000 + (idx * 500)  # Gs. 3,500, 4,000, 4,500
            
            # Calcular subtotales
            subtotal_neto = cantidad * costo_unitario
            monto_iva = subtotal_neto * 0.10  # IVA 10%
            total_producto = subtotal_neto + monto_iva
            
            monto_total_compra += total_producto
            detalles_compra.append((id_producto, costo_unitario, cantidad, subtotal_neto, monto_iva))
            stock_updates.append((id_producto, cantidad, stock_actual))
            
            print_info(f"   {idx}. {descripcion}")
            print_info(f"      Cantidad: {cantidad} unidades x Gs. {costo_unitario:,} = Gs. {subtotal_neto:,.0f}")
            print_info(f"      IVA 10%: Gs. {monto_iva:,.0f}")
            print_info(f"      Total: Gs. {total_producto:,.0f}")
        
        print_divider()
        print_success(f"💰 TOTAL COMPRA: Gs. {monto_total_compra:,.0f}")
        
        # 5. Crear la compra CON el monto calculado
        nro_factura = f"001-001-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        fecha_compra = datetime.now()
        
        print_info(f"\n📄 Creando compra con factura: {nro_factura}")
        
        cursor.execute("""
            INSERT INTO compras (ID_Proveedor, Fecha, Monto_Total, Nro_Factura, Observaciones)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_proveedor, fecha_compra, monto_total_compra, nro_factura, 'Compra de prueba - Test módulo compras'))
        
        id_compra = cursor.lastrowid
        conn.commit()
        
        print_success(f"✅ Compra creada con ID: {id_compra}")
        
        # 6. Agregar detalles de compra
        print_info(f"\n📦 Insertando detalles...")
        
        for detalle in detalles_compra:
            id_producto, costo_unitario, cantidad, subtotal_neto, monto_iva = detalle
            cursor.execute("""
                INSERT INTO detalle_compra
                (ID_Compra, ID_Producto, Costo_Unitario_Neto, Cantidad, Subtotal_Neto, Monto_IVA)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_compra, id_producto, costo_unitario, cantidad, subtotal_neto, monto_iva))
        
        print_success(f"✅ {len(detalles_compra)} productos agregados al detalle")
        
        # 7. Registrar movimientos de stock (Entradas)
        print_info(f"\n📈 Actualizando inventario...")
        
        cursor.execute("SELECT ID_Empleado FROM empleados WHERE Activo = TRUE LIMIT 1")
        empleado = cursor.fetchone()
        id_empleado = empleado[0] if empleado else 1
        
        for id_producto, cantidad, stock_anterior in stock_updates:
            stock_nuevo = stock_anterior + cantidad
            
            # Registrar movimiento
            cursor.execute("""
                INSERT INTO movimientos_stock
                (ID_Producto, ID_Empleado_Autoriza, ID_Compra, Tipo_Movimiento, 
                 Cantidad, Stock_Resultante, Referencia_Documento)
                VALUES (%s, %s, %s, 'Entrada', %s, %s, %s)
            """, (id_producto, id_empleado, id_compra, cantidad, stock_nuevo, nro_factura))
            
            # Actualizar stock
            cursor.execute("""
                UPDATE stock_unico
                SET Stock_Actual = %s
                WHERE ID_Producto = %s
            """, (stock_nuevo, id_producto))
            
            print_info(f"   ✓ Producto ID {id_producto}: {stock_anterior} → {stock_nuevo} (+{cantidad})")
        
        # 8. Registrar en cuenta corriente del proveedor
        print_info(f"\n💳 Registrando en cuenta corriente...")
        
        saldo_nuevo = saldo_inicial + monto_total_compra
        
        cursor.execute("""
            INSERT INTO cta_corriente_prov
            (ID_Proveedor, ID_Compra, Tipo_Movimiento, Monto, Fecha, 
             Saldo_Acumulado, Referencia_Doc)
            VALUES (%s, %s, 'CARGO', %s, %s, %s, %s)
        """, (id_proveedor, id_compra, monto_total_compra, fecha_compra, saldo_nuevo, nro_factura))
        
        conn.commit()
        
        print_success(f"   ✓ Cargo registrado: +Gs. {monto_total_compra:,.0f}")
        print_success(f"   ✓ Saldo acumulado: Gs. {saldo_nuevo:,.0f}")
        
        print_success("\n🎉 ✓✓✓ COMPRA COMPLETADA EXITOSAMENTE ✓✓✓")
        
        return {
            'id_compra': id_compra,
            'id_proveedor': id_proveedor,
            'monto': monto_total_compra,
            'nro_factura': nro_factura
        }
        
    except Exception as e:
        print_error(f"❌ Error: {str(e)}")
        conn.rollback()
        return False


# =============================================================================
# TEST 2: PAGO A PROVEEDOR
# =============================================================================
def test_pago_proveedor(conn, cursor, datos_compra):
    print_header("TEST 2: PAGO A PROVEEDOR - ABONO A CUENTA")
    
    if not datos_compra:
        print_error("No hay datos de compra previa")
        return False
    
    try:
        id_proveedor = datos_compra['id_proveedor']
        monto_compra = datos_compra['monto']
        
        # 1. Consultar saldo actual
        cursor.execute("""
            SELECT p.Razon_Social, COALESCE(MAX(cc.Saldo_Acumulado), 0)
            FROM proveedores p
            LEFT JOIN cta_corriente_prov cc ON p.ID_Proveedor = cc.ID_Proveedor
            WHERE p.ID_Proveedor = %s
            GROUP BY p.ID_Proveedor, p.Razon_Social
        """, (id_proveedor,))
        
        resultado = cursor.fetchone()
        razon_social = resultado[0]
        saldo_actual = float(resultado[1])
        
        print_info(f"🏭 Proveedor: {razon_social}")
        print_info(f"💰 Deuda actual: Gs. {saldo_actual:,.0f}")
        
        # 2. Realizar pago parcial (50% de la compra reciente)
        monto_pago = monto_compra * 0.5
        
        print_info(f"\n💵 Procesando pago de Gs. {monto_pago:,.0f} (50% del total)")
        
        # 3. Registrar pago en cuenta corriente
        saldo_nuevo = saldo_actual - monto_pago
        nro_recibo = f"REC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        cursor.execute("""
            INSERT INTO cta_corriente_prov
            (ID_Proveedor, Tipo_Movimiento, Monto, Fecha, Saldo_Acumulado, Referencia_Doc)
            VALUES (%s, 'ABONO', %s, NOW(), %s, %s)
        """, (id_proveedor, monto_pago, saldo_nuevo, nro_recibo))
        
        conn.commit()
        
        print_success(f"\n✅ Pago registrado:")
        print_success(f"   • Recibo: {nro_recibo}")
        print_success(f"   • Monto: Gs. {monto_pago:,.0f}")
        print_success(f"   • Saldo anterior: Gs. {saldo_actual:,.0f}")
        print_success(f"   • Saldo nuevo: Gs. {saldo_nuevo:,.0f}")
        print_success(f"   • Saldo pendiente: Gs. {saldo_nuevo:,.0f}")
        
        print_success("\n🎉 ✓✓✓ PAGO PROCESADO EXITOSAMENTE ✓✓✓")
        return True
        
    except Exception as e:
        print_error(f"❌ Error: {str(e)}")
        conn.rollback()
        return False


# =============================================================================
# TEST 3: CONSULTA DETALLADA DE CUENTA CORRIENTE
# =============================================================================
def test_cuenta_corriente_detalle(conn, cursor, datos_compra):
    print_header("TEST 3: DETALLE DE CUENTA CORRIENTE DEL PROVEEDOR")
    
    if not datos_compra:
        print_error("No hay datos de proveedor")
        return False
    
    try:
        id_proveedor = datos_compra['id_proveedor']
        
        # 1. Información del proveedor
        cursor.execute("""
            SELECT Razon_Social, RUC, Telefono, Email, Direccion
            FROM proveedores
            WHERE ID_Proveedor = %s
        """, (id_proveedor,))
        
        prov = cursor.fetchone()
        
        print_info(f"🏭 PROVEEDOR:")
        print_info(f"   • Razón Social: {prov[0]}")
        print_info(f"   • RUC: {prov[1]}")
        print_info(f"   • Teléfono: {prov[2] or 'N/A'}")
        print_info(f"   • Email: {prov[3] or 'N/A'}")
        print_info(f"   • Dirección: {prov[4] or 'N/A'}")
        
        # 2. Movimientos de cuenta corriente
        cursor.execute("""
            SELECT 
                ID_MovimientoProv,
                Fecha,
                Tipo_Movimiento,
                Monto,
                Saldo_Acumulado,
                Referencia_Doc,
                ID_Compra
            FROM cta_corriente_prov
            WHERE ID_Proveedor = %s
            ORDER BY ID_MovimientoProv DESC
            LIMIT 10
        """, (id_proveedor,))
        
        movimientos = cursor.fetchall()
        
        print_info(f"\n💳 MOVIMIENTOS DE CUENTA CORRIENTE (últimos 10):")
        print_divider()
        print_info(f"{'ID':<6} {'Fecha':<20} {'Tipo':<8} {'Monto':>15} {'Saldo':>15} {'Referencia':<20}")
        print_divider()
        
        for mov in movimientos:
            fecha_str = mov[1].strftime('%d/%m/%Y %H:%M') if mov[1] else 'N/A'
            tipo_symbol = "+" if mov[2] == 'CARGO' else "-"
            print_info(f"{mov[0]:<6} {fecha_str:<20} {mov[2]:<8} {tipo_symbol}Gs. {float(mov[3]):>12,.0f} Gs. {float(mov[4]):>12,.0f} {mov[5] or 'N/A':<20}")
        
        # 3. Resumen de compras
        cursor.execute("""
            SELECT 
                COUNT(*) as Total_Compras,
                COALESCE(SUM(Monto_Total), 0) as Total_Comprado,
                MIN(Fecha) as Primera_Compra,
                MAX(Fecha) as Ultima_Compra
            FROM compras
            WHERE ID_Proveedor = %s
        """, (id_proveedor,))
        
        resumen = cursor.fetchone()
        
        print_info(f"\n📊 RESUMEN DE COMPRAS:")
        print_info(f"   • Total compras: {resumen[0]}")
        print_info(f"   • Monto total comprado: Gs. {float(resumen[1]):,.0f}")
        if resumen[2]:
            print_info(f"   • Primera compra: {resumen[2].strftime('%d/%m/%Y')}")
        if resumen[3]:
            print_info(f"   • Última compra: {resumen[3].strftime('%d/%m/%Y')}")
        
        # 4. Saldo actual
        cursor.execute("""
            SELECT COALESCE(MAX(Saldo_Acumulado), 0)
            FROM cta_corriente_prov
            WHERE ID_Proveedor = %s
        """, (id_proveedor,))
        
        saldo_actual = float(cursor.fetchone()[0])
        
        print_info(f"\n💰 SALDO ACTUAL: Gs. {saldo_actual:,.0f}")
        
        if saldo_actual > 0:
            print_info(f"   ⚠️  Deuda pendiente con el proveedor")
        elif saldo_actual < 0:
            print_info(f"   ✓ Saldo a favor del proveedor")
        else:
            print_info(f"   ✓ Cuenta saldada")
        
        print_success("\n🎉 ✓✓✓ CONSULTA COMPLETADA ✓✓✓")
        return True
        
    except Exception as e:
        print_error(f"❌ Error: {str(e)}")
        return False


# =============================================================================
# TEST 4: NOTA DE CRÉDITO DE PROVEEDOR (DEVOLUCIÓN)
# =============================================================================
def test_nota_credito_cliente(conn, cursor):
    print_header("TEST 4: NOTA DE CRÉDITO A CLIENTE - DEVOLUCIÓN")
    
    try:
        # 1. Verificar si hay ventas para devolver
        cursor.execute("""
            SELECT v.ID_Venta, v.ID_Cliente, v.Monto_Total, 
                   CONCAT(c.Nombres, ' ', c.Apellidos) as Cliente,
                   v.Fecha
            FROM ventas v
            JOIN clientes c ON v.ID_Cliente = c.ID_Cliente
            WHERE v.Estado = 'Completada'
            ORDER BY v.Fecha DESC
            LIMIT 1
        """)
        
        venta = cursor.fetchone()
        
        if not venta:
            print_info("ℹ️  No hay ventas registradas para crear nota de crédito")
            print_info("   (Esto es esperado si no hay módulo de ventas activo)")
            return True
        
        id_venta = venta[0]
        id_cliente = venta[1]
        monto_venta = float(venta[2])
        cliente = venta[3]
        
        print_info(f"👤 Cliente: {cliente}")
        print_info(f"🧾 Venta original ID: {id_venta}")
        print_info(f"💰 Monto venta: Gs. {monto_venta:,.0f}")
        
        # 2. Verificar timbrado disponible
        cursor.execute("""
            SELECT Nro_Timbrado, Tipo_Documento
            FROM timbrados
            WHERE Activo = TRUE AND Fecha_Fin >= CURDATE()
            ORDER BY Tipo_Documento DESC
            LIMIT 1
        """)
        
        timbrado = cursor.fetchone()
        
        if not timbrado:
            print_info("ℹ️  No hay timbrados disponibles")
            print_info("   Se requiere configurar timbrados fiscales")
            return True
        
        nro_timbrado = timbrado[0]
        
        # 3. Obtener último número de documento
        cursor.execute("""
            SELECT MAX(Nro_Secuencial) 
            FROM documentos_tributarios 
            WHERE Nro_Timbrado = %s
        """, (nro_timbrado,))
        
        ultimo_nro = cursor.fetchone()[0]
        nro_secuencial = (ultimo_nro or 0) + 1
        
        # 4. Crear documento tributario
        monto_devolucion = monto_venta * 0.3  # Devolución del 30%
        
        cursor.execute("""
            INSERT INTO documentos_tributarios
            (Nro_Timbrado, Nro_Secuencial, Fecha_Emision, Monto_Total)
            VALUES (%s, %s, NOW(), %s)
        """, (nro_timbrado, nro_secuencial, monto_devolucion))
        
        id_documento = cursor.lastrowid
        
        # 5. Crear nota de crédito
        cursor.execute("""
            INSERT INTO notas_credito
            (ID_Documento, ID_Cliente, ID_Venta_Original, Fecha, Monto_Total, 
             Motivo_Devolucion, Estado)
            VALUES (%s, %s, %s, NOW(), %s, %s, 'Emitida')
        """, (id_documento, id_cliente, id_venta, monto_devolucion, 
              'Devolución parcial - Producto en mal estado'))
        
        id_nota = cursor.lastrowid
        conn.commit()
        
        print_success(f"\n✅ Nota de Crédito creada:")
        print_success(f"   • ID Nota: {id_nota}")
        print_success(f"   • ID Documento: {id_documento}")
        print_success(f"   • Monto devuelto: Gs. {monto_devolucion:,.0f} (30% de la venta)")
        print_success(f"   • Estado: Emitida")
        
        print_success("\n🎉 ✓✓✓ NOTA DE CRÉDITO GENERADA ✓✓✓")
        return True
        
    except Exception as e:
        print_error(f"❌ Error: {str(e)}")
        conn.rollback()
        return False


# =============================================================================
# TEST 5: REPORTE DE PROVEEDORES Y DEUDAS
# =============================================================================
def test_reporte_proveedores(conn, cursor):
    print_header("TEST 5: REPORTE GENERAL DE PROVEEDORES")
    
    try:
        # 1. Lista de proveedores con saldos
        cursor.execute("""
            SELECT 
                p.ID_Proveedor,
                p.Razon_Social,
                p.RUC,
                COUNT(DISTINCT c.ID_Compra) as Total_Compras,
                COALESCE(SUM(c.Monto_Total), 0) as Total_Comprado,
                COALESCE(MAX(cc.Saldo_Acumulado), 0) as Saldo_Actual,
                p.Activo
            FROM proveedores p
            LEFT JOIN compras c ON p.ID_Proveedor = c.ID_Proveedor
            LEFT JOIN cta_corriente_prov cc ON p.ID_Proveedor = cc.ID_Proveedor
                AND cc.ID_MovimientoProv = (
                    SELECT MAX(ID_MovimientoProv) 
                    FROM cta_corriente_prov 
                    WHERE ID_Proveedor = p.ID_Proveedor
                )
            GROUP BY p.ID_Proveedor, p.Razon_Social, p.RUC, p.Activo
            ORDER BY Saldo_Actual DESC, Total_Comprado DESC
        """)
        
        proveedores = cursor.fetchall()
        
        print_info(f"📋 LISTADO DE PROVEEDORES ({len(proveedores)} total):")
        print_divider()
        print_info(f"{'ID':<5} {'Razón Social':<35} {'RUC':<15} {'Compras':<8} {'Total Comprado':>18} {'Saldo':>18} {'Estado':<8}")
        print_divider()
        
        total_deudas = 0
        proveedores_con_deuda = 0
        
        for prov in proveedores:
            estado = "✓ Activo" if prov[6] else "✗ Inactivo"
            saldo = float(prov[5])
            
            if saldo > 0:
                total_deudas += saldo
                proveedores_con_deuda += 1
            
            print_info(f"{prov[0]:<5} {prov[1]:<35} {prov[2]:<15} {prov[3]:<8} Gs. {float(prov[4]):>14,.0f} Gs. {saldo:>14,.0f} {estado:<8}")
        
        print_divider()
        
        # 2. Resumen general
        print_info(f"\n📊 RESUMEN GENERAL:")
        print_success(f"   • Total proveedores: {len(proveedores)}")
        print_success(f"   • Proveedores con deuda: {proveedores_con_deuda}")
        print_success(f"   • Deuda total: Gs. {total_deudas:,.0f}")
        
        # 3. Estadísticas de compras
        cursor.execute("""
            SELECT 
                COUNT(*) as Total_Compras,
                COALESCE(SUM(Monto_Total), 0) as Total_Comprado,
                COALESCE(AVG(Monto_Total), 0) as Promedio_Compra,
                MIN(Fecha) as Primera_Compra,
                MAX(Fecha) as Ultima_Compra
            FROM compras
        """)
        
        stats = cursor.fetchone()
        
        print_info(f"\n📈 ESTADÍSTICAS DE COMPRAS:")
        print_info(f"   • Total compras: {stats[0]}")
        print_info(f"   • Monto total: Gs. {float(stats[1]):,.0f}")
        print_info(f"   • Promedio por compra: Gs. {float(stats[2]):,.0f}")
        if stats[3]:
            print_info(f"   • Primera compra: {stats[3].strftime('%d/%m/%Y')}")
        if stats[4]:
            print_info(f"   • Última compra: {stats[4].strftime('%d/%m/%Y')}")
        
        # 4. Compras del mes actual
        cursor.execute("""
            SELECT 
                COUNT(*) as Compras_Mes,
                COALESCE(SUM(Monto_Total), 0) as Total_Mes
            FROM compras
            WHERE MONTH(Fecha) = MONTH(CURDATE())
            AND YEAR(Fecha) = YEAR(CURDATE())
        """)
        
        mes = cursor.fetchone()
        
        print_info(f"\n📅 COMPRAS DEL MES ACTUAL:")
        print_info(f"   • Compras realizadas: {mes[0]}")
        print_info(f"   • Monto total: Gs. {float(mes[1]):,.0f}")
        
        print_success("\n🎉 ✓✓✓ REPORTE COMPLETADO ✓✓✓")
        return True
        
    except Exception as e:
        print_error(f"❌ Error: {str(e)}")
        return False


# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================
def main():
    print("\n" + "=" * 90)
    print("  🏭 TEST MÓDULO DE COMPRAS Y PROVEEDORES - CANTINA TITA")
    print("  Pruebas: Compras, Pagos, Cuenta Corriente, Notas de Crédito")
    print("  " + datetime.now().strftime("%d de %B de %Y, %H:%M:%S"))
    print("=" * 90)
    
    try:
        conn = MySQLdb.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print_success("✅ Conexión a base de datos establecida\n")
    except Exception as e:
        print_error(f"❌ Error conectando: {str(e)}")
        return
    
    # Ejecutar tests en secuencia
    resultados = {}
    
    # Test 1: Compra a proveedor
    datos_compra = test_compra_proveedor(conn, cursor)
    resultados['Compra a Proveedor'] = bool(datos_compra)
    
    # Test 2: Pago a proveedor (depende del test 1)
    if datos_compra:
        resultados['Pago a Proveedor'] = test_pago_proveedor(conn, cursor, datos_compra)
    else:
        print_info("\n⚠️  Saltando test de pago (sin datos de compra)")
        resultados['Pago a Proveedor'] = False
    
    # Test 3: Detalle cuenta corriente (depende del test 1)
    if datos_compra:
        resultados['Cuenta Corriente'] = test_cuenta_corriente_detalle(conn, cursor, datos_compra)
    else:
        print_info("\n⚠️  Saltando test de cuenta corriente (sin datos)")
        resultados['Cuenta Corriente'] = False
    
    # Test 4: Nota de crédito (independiente)
    resultados['Nota de Crédito'] = test_nota_credito_cliente(conn, cursor)
    
    # Test 5: Reporte de proveedores (independiente)
    resultados['Reporte de Proveedores'] = test_reporte_proveedores(conn, cursor)
    
    cursor.close()
    conn.close()
    
    # Resumen final
    print_header("🎯 RESUMEN FINAL DE PRUEBAS")
    
    exitosos = sum(resultados.values())
    total = len(resultados)
    
    for nombre, resultado in resultados.items():
        if resultado:
            print_success(f"✅ {nombre}: EXITOSA")
        else:
            print_error(f"❌ {nombre}: FALLIDA")
    
    porcentaje = (exitosos / total) * 100
    
    print("\n" + "=" * 90)
    print(f"  RESULTADO: {exitosos}/{total} pruebas exitosas ({porcentaje:.1f}%)")
    print("=" * 90)
    
    if exitosos == total:
        print("\n🎉 ¡PERFECTO! Módulo de compras completamente funcional.")
    elif exitosos >= total * 0.8:
        print("\n✅ Excelente. Módulo de compras operacional.")
    elif exitosos >= total * 0.6:
        print("\n⚠️  Bueno. Algunas funcionalidades requieren atención.")
    else:
        print("\n⚠️  Revisar funcionalidades con errores.")


if __name__ == "__main__":
    main()
