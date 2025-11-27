#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST MÓDULO - CIERRES DE CAJA (REDISEÑADO)
==========================================
Pruebas del sistema de control de caja.

NOTA: Este módulo trabaja solo con las tablas reales:
- cierres_caja (control de apertura/cierre)
- ventas (ingresos por ventas)
- cargas_saldo (ingresos por recargas)

COBERTURA:
- Apertura de caja diaria
- Verificación de operaciones del día
- Conteo de efectivo y diferencias
- Cierre de caja
- Consultas y reportes
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
        # Buscar un empleado activo
        cursor.execute("""
            SELECT ID_Empleado, Nombre, Apellido
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
        
        # Buscar una caja disponible
        cursor.execute("""
            SELECT ID_Caja, Nombre_Caja, Ubicacion
            FROM cajas
            WHERE Activo = TRUE
            LIMIT 1
        """)
        
        caja_info = cursor.fetchone()
        
        if not caja_info:
            print_error("No hay cajas disponibles")
            return False
        
        id_caja, nombre_caja, ubicacion = caja_info
        print_info(f"Caja: {nombre_caja} ({ubicacion})")
        
        # Verificar si ya hay caja abierta hoy para este empleado/caja
        cursor.execute("""
            SELECT ID_Cierre, Fecha_Hora_Apertura, Monto_Inicial
            FROM cierres_caja
            WHERE ID_Empleado = %s 
            AND ID_Caja = %s
            AND DATE(Fecha_Hora_Apertura) = CURDATE()
            AND Estado = 'Abierto'
        """, (id_empleado, id_caja))
        
        caja_existente = cursor.fetchone()
        
        if caja_existente:
            id_cierre, fecha, monto = caja_existente
            print_info(f"\nYa existe caja abierta:")
            print_info(f"  ID Cierre: {id_cierre}")
            print_info(f"  Apertura: {fecha.strftime('%d/%m/%Y %H:%M')}")
            print_info(f"  Monto inicial: Gs. {float(monto):,.0f}")
        else:
            # Abrir nueva caja
            monto_inicial = 100000  # Gs. 100,000 de fondo fijo
            
            cursor.execute("""
                INSERT INTO cierres_caja
                (ID_Caja, ID_Empleado, Fecha_Hora_Apertura, Monto_Inicial, Estado)
                VALUES (%s, %s, NOW(), %s, 'Abierto')
            """, (id_caja, id_empleado, monto_inicial))
            
            id_cierre = cursor.lastrowid
            print_success(f"\n✅ Caja abierta exitosamente")
            print_info(f"   ID Cierre: {id_cierre}")
            print_info(f"   Caja: {nombre_caja}")
            print_info(f"   Cajero: {nombres} {apellidos}")
            print_info(f"   Monto inicial: Gs. {monto_inicial:,.0f}")
            print_info(f"   Estado: Abierto")
        
        # Verificar estado
        cursor.execute("""
            SELECT COUNT(*) 
            FROM cierres_caja 
            WHERE Estado = 'Abierto'
            AND DATE(Fecha_Hora_Apertura) = CURDATE()
        """)
        
        count = cursor.fetchone()[0]
        print_info(f"\n📊 Total de cajas abiertas hoy: {count}")
        
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
# TEST 2: OPERACIONES DEL DÍA
# ============================================================================

def test_operaciones_caja():
    """Verifica las operaciones registradas del día"""
    print_header("TEST 2: Verificación de Operaciones del Día")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar caja abierta
        cursor.execute("""
            SELECT 
                cc.ID_Cierre,
                cc.ID_Caja,
                c.Nombre_Caja,
                cc.Monto_Inicial,
                e.Nombre,
                e.Apellido,
                cc.Fecha_Hora_Apertura
            FROM cierres_caja cc
            INNER JOIN cajas c ON cc.ID_Caja = c.ID_Caja
            INNER JOIN empleados e ON cc.ID_Empleado = e.ID_Empleado
            WHERE cc.Estado = 'Abierto'
            AND DATE(cc.Fecha_Hora_Apertura) = CURDATE()
            LIMIT 1
        """)
        
        caja = cursor.fetchone()
        
        if not caja:
            print_info("No hay cajas abiertas hoy")
            # Buscar última caja cerrada
            cursor.execute("""
                SELECT 
                    cc.ID_Cierre,
                    cc.ID_Caja,
                    c.Nombre_Caja,
                    cc.Monto_Inicial,
                    e.Nombre,
                    e.Apellido,
                    cc.Fecha_Hora_Apertura
                FROM cierres_caja cc
                INNER JOIN cajas c ON cc.ID_Caja = c.ID_Caja
                INNER JOIN empleados e ON cc.ID_Empleado = e.ID_Empleado
                ORDER BY cc.Fecha_Hora_Apertura DESC
                LIMIT 1
            """)
            
            caja = cursor.fetchone()
            
            if not caja:
                print_error("No hay cierres de caja en el sistema")
                return False
        
        id_cierre, id_caja, nombre_caja, monto_inicial, nombres, apellidos, fecha_apertura = caja
        
        print_info(f"Caja ID: {id_cierre} - {nombre_caja}")
        print_info(f"Cajero: {nombres} {apellidos}")
        print_info(f"Apertura: {fecha_apertura.strftime('%d/%m/%Y %H:%M')}")
        print_info(f"Monto inicial: Gs. {float(monto_inicial):,.0f}")
        
        # Contar ventas del día
        cursor.execute("""
            SELECT 
                COUNT(*) as cantidad_ventas,
                COALESCE(SUM(Monto_Total), 0) as total_ventas
            FROM ventas
            WHERE DATE(Fecha) = DATE(%s)
        """, (fecha_apertura,))
        
        ventas_info = cursor.fetchone()
        cant_ventas, total_ventas = ventas_info
        
        print_info(f"\n💰 Operaciones del día:")
        print_info(f"  Ventas registradas: {cant_ventas}")
        print_info(f"  Total ventas: Gs. {float(total_ventas):,.0f}")
        
        # Contar recargas del día
        cursor.execute("""
            SELECT 
                COUNT(*) as cantidad_recargas,
                COALESCE(SUM(Monto_Cargado), 0) as total_recargas
            FROM cargas_saldo
            WHERE DATE(Fecha_Carga) = DATE(%s)
        """, (fecha_apertura,))
        
        recargas_info = cursor.fetchone()
        cant_recargas, total_recargas = recargas_info
        
        print_info(f"  Recargas registradas: {cant_recargas}")
        print_info(f"  Total recargas: Gs. {float(total_recargas):,.0f}")
        
        # Total de ingresos del día
        total_ingresos = float(total_ventas) + float(total_recargas)
        saldo_teorico = float(monto_inicial) + total_ingresos
        
        print_success(f"\n✅ Resumen financiero:")
        print_info(f"  Monto inicial: Gs. {float(monto_inicial):,.0f}")
        print_info(f"  Total ingresos: Gs. {total_ingresos:,.0f}")
        print_info(f"  Saldo teórico: Gs. {saldo_teorico:,.0f}")
        
        # Desglose por tipo de pago en ventas
        cursor.execute("""
            SELECT 
                tp.Descripcion as tipo_pago,
                COUNT(*) as cantidad,
                SUM(v.Monto_Total) as total
            FROM ventas v
            INNER JOIN tipos_pago tp ON v.ID_Tipo_Pago = tp.ID_Tipo_Pago
            WHERE DATE(v.Fecha) = DATE(%s)
            GROUP BY tp.ID_Tipo_Pago, tp.Descripcion
        """, (fecha_apertura,))
        
        tipos_pago = cursor.fetchall()
        
        if tipos_pago:
            print_info(f"\n📊 Ventas por tipo de pago:")
            for tipo, cant, total in tipos_pago:
                print_info(f"  {tipo}: {cant} ventas - Gs. {float(total):,.0f}")
        
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# TEST 3: CONTEO DE EFECTIVO
# ============================================================================

def test_conteo_efectivo():
    """Prueba el conteo de efectivo y detección de diferencias"""
    print_header("TEST 3: Conteo de Efectivo y Diferencias")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar caja abierta
        cursor.execute("""
            SELECT 
                cc.ID_Cierre,
                cc.Monto_Inicial,
                cc.Fecha_Hora_Apertura
            FROM cierres_caja cc
            WHERE cc.Estado = 'Abierto'
            LIMIT 1
        """)
        
        caja = cursor.fetchone()
        
        if not caja:
            print_info("No hay cajas abiertas para conteo")
            return True  # No es error, simplemente no hay cajas abiertas
        
        id_cierre, monto_inicial, fecha_apertura = caja
        print_info(f"Caja ID: {id_cierre}")
        print_info(f"Monto inicial: Gs. {float(monto_inicial):,.0f}")
        
        # Calcular saldo teórico
        cursor.execute("""
            SELECT COALESCE(SUM(Monto_Total), 0)
            FROM ventas
            WHERE DATE(Fecha) = DATE(%s)
        """, (fecha_apertura,))
        
        total_ventas = float(cursor.fetchone()[0])
        
        cursor.execute("""
            SELECT COALESCE(SUM(Monto_Cargado), 0)
            FROM cargas_saldo
            WHERE DATE(Fecha_Carga) = DATE(%s)
        """, (fecha_apertura,))
        
        total_recargas = float(cursor.fetchone()[0])
        
        saldo_teorico = float(monto_inicial) + total_ventas + total_recargas
        
        print_info(f"\n💵 Cálculo teórico:")
        print_info(f"  Monto inicial: Gs. {float(monto_inicial):,.0f}")
        print_info(f"  + Ventas: Gs. {total_ventas:,.0f}")
        print_info(f"  + Recargas: Gs. {total_recargas:,.0f}")
        print_info(f"  = Saldo teórico: Gs. {saldo_teorico:,.0f}")
        
        # Simular conteo físico (con pequeña diferencia para prueba)
        monto_fisico = saldo_teorico - 1500  # Simulamos faltante de Gs. 1,500
        diferencia = monto_fisico - saldo_teorico
        
        print_info(f"\n🧮 Conteo físico:")
        print_info(f"  Monto contado: Gs. {monto_fisico:,.0f}")
        print_info(f"  Diferencia: Gs. {diferencia:,.0f}")
        
        if abs(diferencia) < 100:
            print_success(f"  ✅ Caja cuadrada (diferencia menor a Gs. 100)")
            estado_conteo = "Cuadrada"
        elif diferencia < 0:
            print_error(f"  ❌ Faltante: Gs. {abs(diferencia):,.0f}")
            estado_conteo = "Faltante"
        else:
            print_info(f"  ⚠️  Sobrante: Gs. {diferencia:,.0f}")
            estado_conteo = "Sobrante"
        
        # Actualizar con monto contado y diferencia (sin cerrar)
        cursor.execute("""
            UPDATE cierres_caja
            SET 
                Monto_Contado_Fisico = %s,
                Diferencia_Efectivo = %s
            WHERE ID_Cierre = %s
        """, (monto_fisico, diferencia, id_cierre))
        
        print_success(f"\n✅ Conteo registrado")
        print_info(f"  Estado: {estado_conteo}")
        
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
    """Prueba el cierre de caja"""
    print_header("TEST 4: Cierre de Caja")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar caja abierta
        cursor.execute("""
            SELECT 
                cc.ID_Cierre,
                cc.Monto_Inicial,
                cc.Monto_Contado_Fisico,
                cc.Diferencia_Efectivo,
                cc.Fecha_Hora_Apertura,
                c.Nombre_Caja,
                e.Nombre,
                e.Apellido
            FROM cierres_caja cc
            INNER JOIN cajas c ON cc.ID_Caja = c.ID_Caja
            INNER JOIN empleados e ON cc.ID_Empleado = e.ID_Empleado
            WHERE cc.Estado = 'Abierto'
            LIMIT 1
        """)
        
        caja = cursor.fetchone()
        
        if not caja:
            print_info("No hay cajas abiertas para cerrar")
            return True  # No es error
        
        (id_cierre, monto_inicial, monto_fisico, diferencia, 
         fecha_apertura, nombre_caja, nombres, apellidos) = caja
        
        print_info(f"Caja: {nombre_caja}")
        print_info(f"Cajero: {nombres} {apellidos}")
        print_info(f"Apertura: {fecha_apertura.strftime('%d/%m/%Y %H:%M')}")
        
        # Calcular totales del día
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(Monto_Total), 0)
            FROM ventas
            WHERE DATE(Fecha) = DATE(%s)
        """, (fecha_apertura,))
        
        cant_ventas, total_ventas = cursor.fetchone()
        
        cursor.execute("""
            SELECT COUNT(*), COALESCE(SUM(Monto_Cargado), 0)
            FROM cargas_saldo
            WHERE DATE(Fecha_Carga) = DATE(%s)
        """, (fecha_apertura,))
        
        cant_recargas, total_recargas = cursor.fetchone()
        
        total_ingresos = float(total_ventas) + float(total_recargas)
        monto_final_teorico = float(monto_inicial) + total_ingresos
        
        print_info(f"\n💰 Resumen del día:")
        print_info(f"  Monto inicial: Gs. {float(monto_inicial):,.0f}")
        print_info(f"  Ventas ({cant_ventas}): Gs. {float(total_ventas):,.0f}")
        print_info(f"  Recargas ({cant_recargas}): Gs. {float(total_recargas):,.0f}")
        print_info(f"  Monto final teórico: Gs. {monto_final_teorico:,.0f}")
        
        if monto_fisico:
            print_info(f"  Monto físico contado: Gs. {float(monto_fisico):,.0f}")
            if diferencia:
                print_info(f"  Diferencia: Gs. {float(diferencia):,.0f}")
        
        # Cerrar caja
        cursor.execute("""
            UPDATE cierres_caja
            SET 
                Fecha_Hora_Cierre = NOW(),
                Estado = 'Cerrado'
            WHERE ID_Cierre = %s
        """, (id_cierre,))
        
        print_success(f"\n✅ Caja cerrada exitosamente")
        
        # Verificar cierre
        cursor.execute("""
            SELECT 
                Fecha_Hora_Cierre,
                Estado
            FROM cierres_caja
            WHERE ID_Cierre = %s
        """, (id_cierre,))
        
        verificacion = cursor.fetchone()
        if verificacion:
            fecha_cierre, estado = verificacion
            print_info(f"  Fecha cierre: {fecha_cierre.strftime('%d/%m/%Y %H:%M')}")
            print_info(f"  Estado: {estado}")
        
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
# TEST 5: REPORTES Y CONSULTAS
# ============================================================================

def test_reportes_cierres():
    """Prueba la generación de reportes de cierres"""
    print_header("TEST 5: Reportes y Consultas de Cierres")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Historial de cierres
        cursor.execute("""
            SELECT 
                cc.ID_Cierre,
                DATE(cc.Fecha_Hora_Apertura) as fecha,
                c.Nombre_Caja,
                e.Nombre,
                e.Apellido,
                cc.Monto_Inicial,
                cc.Monto_Contado_Fisico,
                cc.Diferencia_Efectivo,
                cc.Estado
            FROM cierres_caja cc
            INNER JOIN cajas c ON cc.ID_Caja = c.ID_Caja
            INNER JOIN empleados e ON cc.ID_Empleado = e.ID_Empleado
            WHERE cc.Fecha_Hora_Apertura >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            ORDER BY cc.Fecha_Hora_Apertura DESC
            LIMIT 10
        """)
        
        cierres = cursor.fetchall()
        
        if not cierres:
            print_info("No se encontraron cierres en los últimos 30 días")
            return True
        
        print_success(f"✅ {len(cierres)} cierre(s) encontrado(s)")
        
        print("\n   📊 Historial de cierres:")
        print(f"   {'Fecha':<12} {'Caja':<15} {'Cajero':<20} {'Inicial':>15} {'Final':>15} {'Dif':>12} {'Estado':<8}")
        print(f"   {'-'*105}")
        
        for cierre in cierres:
            (id_c, fecha, caja, nom, ape, inicial, final, dif, estado) = cierre
            cajero = f"{nom} {ape}"[:18]
            fecha_str = fecha.strftime('%d/%m/%Y')
            ini = float(inicial)
            fin = float(final) if final else ini
            diferencia = float(dif) if dif else 0
            
            print(f"   {fecha_str:<12} {caja:<15} {cajero:<20} Gs. {ini:>12,.0f} Gs. {fin:>12,.0f} Gs. {diferencia:>9,.0f} {estado:<8}")
        
        # Estadísticas generales
        cursor.execute("""
            SELECT 
                COUNT(*) as total_cierres,
                COUNT(DISTINCT ID_Empleado) as cajeros_activos,
                COUNT(DISTINCT ID_Caja) as cajas_usadas,
                SUM(CASE WHEN Estado = 'Cerrado' THEN 1 ELSE 0 END) as cierres_completados,
                SUM(CASE WHEN Estado = 'Abierto' THEN 1 ELSE 0 END) as cajas_abiertas
            FROM cierres_caja
            WHERE Fecha_Hora_Apertura >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """)
        
        stats = cursor.fetchone()
        
        if stats:
            total, cajeros, cajas, cerrados, abiertos = stats
            
            print(f"\n   📈 Estadísticas últimos 30 días:")
            print_info(f"     Total de cierres: {total}")
            print_info(f"     Cajeros activos: {cajeros}")
            print_info(f"     Cajas utilizadas: {cajas}")
            print_info(f"     Cierres completados: {cerrados}")
            print_info(f"     Cajas aún abiertas: {abiertos}")
        
        # Cierres con diferencias significativas
        cursor.execute("""
            SELECT 
                DATE(cc.Fecha_Hora_Apertura) as fecha,
                c.Nombre_Caja,
                e.Nombre,
                e.Apellido,
                cc.Monto_Inicial,
                cc.Monto_Contado_Fisico,
                cc.Diferencia_Efectivo
            FROM cierres_caja cc
            INNER JOIN cajas c ON cc.ID_Caja = c.ID_Caja
            INNER JOIN empleados e ON cc.ID_Empleado = e.ID_Empleado
            WHERE ABS(COALESCE(cc.Diferencia_Efectivo, 0)) > 1000
            AND cc.Fecha_Hora_Apertura >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            ORDER BY ABS(cc.Diferencia_Efectivo) DESC
            LIMIT 5
        """)
        
        diferencias = cursor.fetchall()
        
        if diferencias:
            print(f"\n   ⚠️  Cierres con diferencias significativas (> Gs. 1,000):")
            print(f"   {'Fecha':<12} {'Caja':<15} {'Cajero':<20} {'Inicial':>15} {'Final':>15} {'Diferencia':>15}")
            print(f"   {'-'*100}")
            
            for dif in diferencias:
                fecha, caja, nom, ape, inicial, final, diferencia = dif
                cajero = f"{nom} {ape}"[:18]
                fecha_str = fecha.strftime('%d/%m/%Y')
                ini = float(inicial)
                fin = float(final) if final else ini
                dif_val = float(diferencia) if diferencia else 0
                
                print(f"   {fecha_str:<12} {caja:<15} {cajero:<20} Gs. {ini:>12,.0f} Gs. {fin:>12,.0f} Gs. {dif_val:>12,.0f}")
        else:
            print_success(f"\n   ✅ No hay diferencias significativas en los últimos 30 días")
        
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
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
    print("█            TEST COMPLETO - CIERRES DE CAJA (REDISEÑADO)           █")
    print("█                                                                    █")
    print("█" * 70)
    
    tests = [
        ("Apertura de Caja", test_apertura_caja),
        ("Verificación de Operaciones", test_operaciones_caja),
        ("Conteo de Efectivo", test_conteo_efectivo),
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
    return exitosos == total

if __name__ == "__main__":
    exit(0 if main() else 1)
