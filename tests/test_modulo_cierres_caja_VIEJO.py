#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST MÓDULO - CIERRES DE CAJA
==============================
Pruebas del sistema de control de caja.

COBERTURA:
- Apertura de caja diaria
- Registro de operaciones (ventas/recargas)
- Arqueo de caja con diferencias
- Cierre con totales y cuadre
- Consultas y reportes de cierres
"""

import MySQLdb
from datetime import datetime, timedelta
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
# TEST 1: APERTURA DE CAJA
# ============================================================================

def test_apertura_caja():
    """Prueba la apertura de caja diaria"""
    print_header("TEST 1: Apertura de Caja Diaria")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar un empleado cajero
        cursor.execute("""
            SELECT e.ID_Empleado, e.Nombre, e.Apellido
            FROM empleados e
            WHERE e.Activo = TRUE
            LIMIT 1
        """)
        
        empleado = cursor.fetchone()
        
        if not empleado:
            # Si no hay cajero, buscar cualquier empleado
            cursor.execute("""
                SELECT ID_Empleado, Nombres, Apellidos
                FROM empleados
                WHERE Activo = TRUE
                LIMIT 1
            """)
            empleado = cursor.fetchone()
        
        if not empleado:
            print_error("No hay empleados disponibles")
            return False
        
        id_empleado, nombres, apellidos = empleado
        print_info(f"Cajero: {nombres} {apellidos} (ID: {id_empleado})")
        
        # Verificar si ya hay caja abierta hoy
        cursor.execute("""
            SELECT ID_Cierre 
            FROM cierres_caja 
            WHERE ID_Empleado = %s 
            AND DATE(Fecha_Hora_Apertura) = CURDATE()
            AND Estado = 'Abierta'
        """, (id_empleado,))
        
        caja_existente = cursor.fetchone()
        
        if caja_existente:
            print_info(f"Ya existe caja abierta (ID: {caja_existente[0]})")
            id_cierre = caja_existente[0]
        else:
            # Abrir nueva caja
            monto_inicial = 100000  # Gs. 100,000 de fondo fijo
            
            cursor.execute("""
                INSERT INTO cierres_caja
                (ID_Caja, ID_Empleado, Fecha_Hora_Apertura, Monto_Inicial)
                VALUES (1, %s, NOW(), %s)
            """, (id_empleado, monto_inicial))
            
            id_cierre = cursor.lastrowid
            print_success(f"\n✅ Caja abierta exitosamente")
            print_info(f"   ID Cierre: {id_cierre}")
            print_info(f"   Monto inicial: Gs. {monto_inicial:,.0f}")
        
        # Consultar detalles de la caja
        cursor.execute("""
            SELECT 
                cc.ID_Cierre,
                cc.Fecha_Hora_Apertura,
                cc.Monto_Inicial,
                cc.Estado,
                e.Nombre,
                e.Apellido
            FROM cierres_caja cc
            INNER JOIN empleados e ON cc.ID_Empleado = e.ID_Empleado
            WHERE cc.ID_Cierre = %s
        """, (id_cierre,))
        
        detalle = cursor.fetchone()
        if detalle:
            id_c, fecha, monto, estado, nom, ape = detalle
            print_info(f"\n   📋 Detalles de la caja:")
            print_info(f"     ID: {id_c}")
            print_info(f"     Cajero: {nom} {ape}")
            print_info(f"     Apertura: {fecha.strftime('%d/%m/%Y %H:%M')}")
            print_info(f"     Monto inicial: Gs. {float(monto):,.0f}")
            print_info(f"     Estado: {estado}")
        
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
# TEST 2: REGISTRO DE OPERACIONES
# ============================================================================

def test_operaciones_caja():
    """Prueba el registro de operaciones durante el día"""
    print_header("TEST 2: Registro de Operaciones de Caja")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar o crear caja abierta
        cursor.execute("""
            SELECT cc.ID_Cierre, e.Nombre, e.Apellido
            FROM cierres_caja cc
            INNER JOIN empleados e ON cc.ID_Empleado = e.ID_Empleado
            WHERE cc.Estado = 'Abierta'
            AND DATE(cc.Fecha_Hora_Apertura) = CURDATE()
            LIMIT 1
        """)
        
        caja = cursor.fetchone()
        
        if not caja:
            # Crear caja para prueba
            cursor.execute("""
                SELECT ID_Empleado FROM empleados WHERE Activo = TRUE LIMIT 1
            """)
            empleado = cursor.fetchone()
            
            if not empleado:
                print_error("No hay empleados disponibles")
                return False
            
            cursor.execute("""
                INSERT INTO cierres_caja
                (ID_Caja, ID_Empleado, Fecha_Hora_Apertura, Monto_Inicial)
                VALUES (%s, NOW(), 100000, 'Abierta')
            """, (empleado[0],))
            
            id_cierre = cursor.lastrowid
            
            cursor.execute("""
                SELECT e.Nombre, e.Apellido
                FROM empleados e
                WHERE e.ID_Empleado = %s
            """, (empleado[0],))
            
            emp = cursor.fetchone()
            nombres, apellidos = emp
        else:
            id_cierre, nombres, apellidos = caja
        
        print_info(f"Caja ID: {id_cierre} - Cajero: {nombres} {apellidos}")
        
        # Simular ventas del día
        ventas_simuladas = [
            ('Venta Efectivo', 25000),
            ('Recarga Tarjeta', 50000),
            ('Venta Efectivo', 18000),
            ('Cobro Almuerzo', 180000),
            ('Venta Efectivo', 12500),
        ]
        
        total_ingresos = 0
        
        print_info("\n   💰 Registrando operaciones:")
        
        for concepto, monto in ventas_simuladas:
            cursor.execute("""
                INSERT INTO movimientos_caja
                (ID_Cierre, Tipo_Movimiento, Monto, Concepto, Fecha_Movimiento)
                VALUES (%s, 'INGRESO', %s, %s, NOW())
            """, (id_cierre, monto, concepto))
            
            total_ingresos += monto
            print_info(f"     + {concepto}: Gs. {monto:,.0f}")
        
        # Simular egresos
        egresos_simulados = [
            ('Compra proveedor', 50000),
            ('Gastos varios', 15000),
        ]
        
        total_egresos = 0
        
        for concepto, monto in egresos_simulados:
            cursor.execute("""
                INSERT INTO movimientos_caja
                (ID_Cierre, Tipo_Movimiento, Monto, Concepto, Fecha_Movimiento)
                VALUES (%s, 'EGRESO', %s, %s, NOW())
            """, (id_cierre, monto, concepto))
            
            total_egresos += monto
            print_info(f"     - {concepto}: Gs. {monto:,.0f}")
        
        print_success(f"\n✅ Operaciones registradas")
        print_info(f"   Total ingresos: Gs. {total_ingresos:,.0f}")
        print_info(f"   Total egresos: Gs. {total_egresos:,.0f}")
        
        # Consultar movimientos de la caja
        cursor.execute("""
            SELECT 
                Tipo_Movimiento,
                COUNT(*) as cantidad,
                SUM(Monto) as total
            FROM movimientos_caja
            WHERE ID_Cierre = %s
            GROUP BY Tipo_Movimiento
        """, (id_cierre,))
        
        resumen = cursor.fetchall()
        
        if resumen:
            print_info("\n   📊 Resumen de movimientos:")
            for tipo, cant, total in resumen:
                print_info(f"     {tipo}: {cant} operaciones - Gs. {float(total):,.0f}")
        
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
# TEST 3: ARQUEO DE CAJA
# ============================================================================

def test_arqueo_caja():
    """Prueba el arqueo de caja con detección de diferencias"""
    print_header("TEST 3: Arqueo de Caja")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar caja abierta con movimientos
        cursor.execute("""
            SELECT cc.ID_Cierre, cc.Monto_Inicial
            FROM cierres_caja cc
            WHERE cc.Estado = 'Abierta'
            LIMIT 1
        """)
        
        caja = cursor.fetchone()
        
        if not caja:
            print_error("No hay cajas abiertas para arqueo")
            return False
        
        id_cierre, monto_inicial = caja
        print_info(f"Caja ID: {id_cierre}")
        print_info(f"Monto inicial: Gs. {float(monto_inicial):,.0f}")
        
        # Calcular saldo teórico (esperado)
        cursor.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN Tipo_Movimiento = 'INGRESO' THEN Monto ELSE 0 END), 0) as ingresos,
                COALESCE(SUM(CASE WHEN Tipo_Movimiento = 'EGRESO' THEN Monto ELSE 0 END), 0) as egresos
            FROM movimientos_caja
            WHERE ID_Cierre = %s
        """, (id_cierre,))
        
        movs = cursor.fetchone()
        ingresos, egresos = movs
        ingresos = float(ingresos)
        egresos = float(egresos)
        
        saldo_teorico = float(monto_inicial) + ingresos - egresos
        
        print_info(f"\n   💵 Cálculo teórico:")
        print_info(f"     Monto inicial: Gs. {float(monto_inicial):,.0f}")
        print_info(f"     + Ingresos: Gs. {ingresos:,.0f}")
        print_info(f"     - Egresos: Gs. {egresos:,.0f}")
        print_info(f"     = Saldo teórico: Gs. {saldo_teorico:,.0f}")
        
        # Simular conteo físico (con pequeña diferencia)
        monto_fisico = saldo_teorico - 2500  # Diferencia de Gs. 2,500 (faltante)
        diferencia = monto_fisico - saldo_teorico
        
        print_info(f"\n   🧮 Arqueo físico:")
        print_info(f"     Monto contado: Gs. {monto_fisico:,.0f}")
        
        if abs(diferencia) < 100:
            print_success(f"     ✅ Caja cuadrada (diferencia: Gs. {abs(diferencia):,.0f})")
            estado_arqueo = "Cuadrada"
        elif diferencia < 0:
            print_error(f"     ❌ Faltante: Gs. {abs(diferencia):,.0f}")
            estado_arqueo = "Faltante"
        else:
            print_info(f"     ⚠️  Sobrante: Gs. {diferencia:,.0f}")
            estado_arqueo = "Sobrante"
        
        # Registrar arqueo
        cursor.execute("""
            INSERT INTO arqueos_caja
            (ID_Cierre, Monto_Teorico, Monto_Fisico, Diferencia, Fecha_Arqueo, Observaciones)
            VALUES (%s, %s, %s, %s, NOW(), %s)
        """, (id_cierre, saldo_teorico, monto_fisico, diferencia, 
              f'Arqueo - Estado: {estado_arqueo}'))
        
        id_arqueo = cursor.lastrowid
        
        print_success(f"\n✅ Arqueo registrado (ID: {id_arqueo})")
        print_info(f"   Estado: {estado_arqueo}")
        print_info(f"   Diferencia: Gs. {diferencia:,.0f}")
        
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
# TEST 4: CIERRE DE CAJA
# ============================================================================

def test_cierre_caja():
    """Prueba el cierre de caja con totales finales"""
    print_header("TEST 4: Cierre de Caja")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar caja abierta
        cursor.execute("""
            SELECT 
                cc.ID_Cierre,
                cc.Monto_Inicial,
                cc.Fecha_Hora_Apertura,
                e.Nombre,
                e.Apellido
            FROM cierres_caja cc
            INNER JOIN empleados e ON cc.ID_Empleado = e.ID_Empleado
            WHERE cc.Estado = 'Abierta'
            LIMIT 1
        """)
        
        caja = cursor.fetchone()
        
        if not caja:
            print_error("No hay cajas abiertas para cerrar")
            return False
        
        id_cierre, monto_inicial, fecha_apertura, nombres, apellidos = caja
        
        print_info(f"Caja ID: {id_cierre}")
        print_info(f"Cajero: {nombres} {apellidos}")
        print_info(f"Apertura: {fecha_apertura.strftime('%d/%m/%Y %H:%M')}")
        
        # Calcular totales del día
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN Tipo_Movimiento = 'INGRESO' THEN Monto ELSE 0 END) as total_ingresos,
                SUM(CASE WHEN Tipo_Movimiento = 'EGRESO' THEN Monto ELSE 0 END) as total_egresos,
                COUNT(CASE WHEN Tipo_Movimiento = 'INGRESO' THEN 1 END) as cant_ingresos,
                COUNT(CASE WHEN Tipo_Movimiento = 'EGRESO' THEN 1 END) as cant_egresos
            FROM movimientos_caja
            WHERE ID_Cierre = %s
        """, (id_cierre,))
        
        totales = cursor.fetchone()
        ingresos, egresos, cant_ing, cant_egr = totales
        ingresos = float(ingresos or 0)
        egresos = float(egresos or 0)
        
        monto_final = float(monto_inicial) + ingresos - egresos
        
        print_info(f"\n   💰 Totales del día:")
        print_info(f"     Monto inicial: Gs. {float(monto_inicial):,.0f}")
        print_info(f"     Ingresos ({cant_ing}): Gs. {ingresos:,.0f}")
        print_info(f"     Egresos ({cant_egr}): Gs. {egresos:,.0f}")
        print_info(f"     Monto final: Gs. {monto_final:,.0f}")
        
        # Obtener último arqueo
        cursor.execute("""
            SELECT Monto_Fisico, Diferencia
            FROM arqueos_caja
            WHERE ID_Cierre = %s
            ORDER BY Fecha_Arqueo DESC
            LIMIT 1
        """, (id_cierre,))
        
        arqueo = cursor.fetchone()
        
        if arqueo:
            monto_fisico, diferencia = arqueo
            print_info(f"\n   🧮 Último arqueo:")
            print_info(f"     Monto físico: Gs. {float(monto_fisico):,.0f}")
            print_info(f"     Diferencia: Gs. {float(diferencia):,.0f}")
        else:
            monto_fisico = monto_final
        
        # Registrar cierre
        cursor.execute("""
            UPDATE cierres_caja
            SET 
                Fecha_Hora_Cierre = NOW(),
                Monto_Contado_Fisico = %s,
                Total_Ingresos = %s,
                Total_Egresos = %s
            WHERE ID_Cierre = %s
        """, (monto_final, ingresos, egresos, id_cierre))
        
        print_success(f"\n✅ Caja cerrada exitosamente")
        
        # Verificar cierre
        cursor.execute("""
            SELECT 
                Fecha_Hora_Cierre,
                Monto_Contado_Fisico,
                Estado
            FROM cierres_caja
            WHERE ID_Cierre = %s
        """, (id_cierre,))
        
        cierre_verificado = cursor.fetchone()
        if cierre_verificado:
            fecha_cierre, monto, estado = cierre_verificado
            print_info(f"   Fecha cierre: {fecha_cierre.strftime('%d/%m/%Y %H:%M')}")
            print_info(f"   Monto final: Gs. {float(monto):,.0f}")
            print_info(f"   Estado: {estado}")
        
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
# TEST 5: CONSULTAS Y REPORTES
# ============================================================================

def test_reportes_cierres():
    """Prueba la generación de reportes de cierres"""
    print_header("TEST 5: Consultas y Reportes de Cierres")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Cierres de los últimos días
        cursor.execute("""
            SELECT 
                cc.ID_Cierre,
                DATE(cc.Fecha_Hora_Apertura) as fecha,
                e.Nombre,
                e.Apellido,
                cc.Monto_Inicial,
                cc.Monto_Contado_Fisico,
                cc.Total_Ingresos,
                cc.Total_Egresos,
                cc.Estado
            FROM cierres_caja cc
            INNER JOIN empleados e ON cc.ID_Empleado = e.ID_Empleado
            WHERE cc.Fecha_Hora_Apertura >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            ORDER BY cc.Fecha_Hora_Apertura DESC
            LIMIT 10
        """)
        
        cierres = cursor.fetchall()
        
        print_success(f"✅ {len(cierres)} cierre(s) encontrado(s)")
        
        if cierres:
            print("\n   📊 Historial de cierres:")
            print(f"   {'Fecha':<12} {'Cajero':<20} {'Inicial':>15} {'Final':>15} {'Estado':<10}")
            print(f"   {'-'*80}")
            
            for cierre in cierres:
                id_c, fecha, nom, ape, inicial, final, ing, egr, estado = cierre
                cajero = f"{nom} {ape}"[:18]
                fecha_str = fecha.strftime('%d/%m/%Y')
                ini = float(inicial)
                fin = float(final or inicial)
                
                print(f"   {fecha_str:<12} {cajero:<20} Gs. {ini:>12,.0f} Gs. {fin:>12,.0f} {estado:<10}")
        
        # Estadísticas generales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_cierres,
                SUM(Total_Ingresos) as suma_ingresos,
                SUM(Total_Egresos) as suma_egresos,
                AVG(Monto_Contado_Fisico - Monto_Inicial) as ganancia_promedio,
                COUNT(DISTINCT ID_Empleado) as cajeros
            FROM cierres_caja
            WHERE Fecha_Hora_Apertura >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            AND Estado = 'Cerrada'
        """)
        
        stats = cursor.fetchone()
        
        if stats:
            total, ingresos, egresos, promedio, cajeros = stats
            
            print(f"\n   📈 Estadísticas últimos 30 días:")
            print(f"   Total de cierres: {total}")
            print(f"   Cajeros activos: {cajeros}")
            if ingresos:
                print(f"   Total ingresos: Gs. {float(ingresos):,.0f}")
            if egresos:
                print(f"   Total egresos: Gs. {float(egresos):,.0f}")
            if promedio:
                print(f"   Ganancia promedio/día: Gs. {float(promedio):,.0f}")
        
        # Arqueos con diferencias significativas
        cursor.execute("""
            SELECT 
                ac.ID_Arqueo,
                DATE(ac.Fecha_Arqueo) as fecha,
                e.Nombre,
                e.Apellido,
                ac.Monto_Teorico,
                ac.Monto_Fisico,
                ac.Diferencia
            FROM arqueos_caja ac
            INNER JOIN cierres_caja cc ON ac.ID_Cierre = cc.ID_Cierre
            INNER JOIN empleados e ON cc.ID_Empleado = e.ID_Empleado
            WHERE ABS(ac.Diferencia) > 1000
            ORDER BY ac.Fecha_Arqueo DESC
            LIMIT 5
        """)
        
        diferencias = cursor.fetchall()
        
        if diferencias:
            print(f"\n   ⚠️  Arqueos con diferencias significativas:")
            print(f"   {'Fecha':<12} {'Cajero':<20} {'Teórico':>15} {'Físico':>15} {'Diferencia':>15}")
            print(f"   {'-'*85}")
            
            for arq in diferencias:
                id_arq, fecha, nom, ape, teorico, fisico, dif = arq
                cajero = f"{nom} {ape}"[:18]
                fecha_str = fecha.strftime('%d/%m/%Y')
                
                print(f"   {fecha_str:<12} {cajero:<20} Gs. {float(teorico):>12,.0f} Gs. {float(fisico):>12,.0f} Gs. {float(dif):>12,.0f}")
        
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
    print("█                 TEST COMPLETO - CIERRES DE CAJA                    █")
    print("█                                                                    █")
    print("█" * 70)
    
    tests = [
        ("Apertura de Caja", test_apertura_caja),
        ("Operaciones de Caja", test_operaciones_caja),
        ("Arqueo de Caja", test_arqueo_caja),
        ("Cierre de Caja", test_cierre_caja),
        ("Reportes de Cierres", test_reportes_cierres),
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
        print("\n🎉 ¡PERFECTO! Todos los tests de cierres de caja pasaron.")
    else:
        print(f"\n⚠️  {total - exitosos} test(s) fallaron.")
    
    print("\n")

if __name__ == "__main__":
    main()
