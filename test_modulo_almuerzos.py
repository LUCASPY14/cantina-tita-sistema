#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST MÓDULO - ALMUERZOS MENSUALES (REDISEÑADO)
===============================================
Pruebas del sistema de suscripciones y consumo de almuerzos.

NOTA: Este módulo trabaja con las tablas reales:
- planes_almuerzo (catálogo de planes)
- suscripciones_almuerzo (suscripción hijo-plan)
- pagos_almuerzo_mensual (pagos mensuales)
- registro_consumo_almuerzo (consumos diarios)

COBERTURA:
- Gestión de suscripciones a planes
- Registro de pagos mensuales
- Registro de consumo diario
- Consultas de pagos y suscripciones
- Reportes de consumo
"""

import MySQLdb
from datetime import datetime, timedelta, date
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
# TEST 1: SUSCRIPCIÓN A PLAN DE ALMUERZO
# ============================================================================

def test_suscripcion_plan():
    """Prueba la suscripción de un hijo a un plan de almuerzo"""
    print_header("TEST 1: Suscripción a Plan de Almuerzo")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar un plan de almuerzo disponible
        cursor.execute("""
            SELECT ID_Plan_Almuerzo, Nombre_Plan, Precio_Mensual, Dias_Semana_Incluidos
            FROM planes_almuerzo
            ORDER BY ID_Plan_Almuerzo
            LIMIT 1
        """)
        
        plan = cursor.fetchone()
        if not plan:
            print_error("No hay planes de almuerzo disponibles")
            return False
        
        id_plan, nombre_plan, precio, dias = plan
        print_info(f"Plan: {nombre_plan}")
        print_info(f"Precio: Gs. {float(precio):,.0f}/mes")
        print_info(f"Días: {dias}")
        
        # Buscar un hijo sin suscripción activa
        cursor.execute("""
            SELECT h.ID_Hijo, h.Nombre, h.Apellido, h.ID_Cliente_Responsable
            FROM hijos h
            INNER JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
            WHERE c.Activo = TRUE
            AND NOT EXISTS (
                SELECT 1 FROM suscripciones_almuerzo sa
                WHERE sa.ID_Hijo = h.ID_Hijo
                AND sa.Estado = 'Activa'
            )
            LIMIT 1
        """)
        
        hijo = cursor.fetchone()
        if not hijo:
            # Si todos tienen suscripción, buscar cualquier hijo
            cursor.execute("""
                SELECT h.ID_Hijo, h.Nombre, h.Apellido, h.ID_Cliente_Responsable
                FROM hijos h
                INNER JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
                WHERE c.Activo = TRUE
                LIMIT 1
            """)
            hijo = cursor.fetchone()
        
        if not hijo:
            print_error("No hay estudiantes disponibles")
            return False
        
        id_hijo, nombre, apellido, id_cliente = hijo
        print_info(f"Estudiante: {nombre} {apellido} (ID: {id_hijo})")
        
        # Verificar suscripción existente
        cursor.execute("""
            SELECT ID_Suscripcion, Estado, Fecha_Inicio
            FROM suscripciones_almuerzo
            WHERE ID_Hijo = %s
            AND ID_Plan_Almuerzo = %s
            AND Estado = 'Activa'
        """, (id_hijo, id_plan))
        
        suscripcion_existente = cursor.fetchone()
        
        if suscripcion_existente:
            id_suscripcion, estado, fecha_inicio = suscripcion_existente
            print_info(f"\nYa existe suscripción activa:")
            print_info(f"  ID: {id_suscripcion}")
            print_info(f"  Desde: {fecha_inicio.strftime('%d/%m/%Y')}")
        else:
            # Crear nueva suscripción
            fecha_inicio = date.today()
            
            cursor.execute("""
                INSERT INTO suscripciones_almuerzo
                (ID_Hijo, ID_Plan_Almuerzo, Fecha_Inicio, Estado)
                VALUES (%s, %s, %s, 'Activa')
            """, (id_hijo, id_plan, fecha_inicio))
            
            id_suscripcion = cursor.lastrowid
            print_success(f"\n✅ Suscripción creada exitosamente")
            print_info(f"   ID Suscripción: {id_suscripcion}")
            print_info(f"   Plan: {nombre_plan}")
            print_info(f"   Estudiante: {nombre} {apellido}")
            print_info(f"   Fecha inicio: {fecha_inicio.strftime('%d/%m/%Y')}")
        
        # Consultar detalles completos
        cursor.execute("""
            SELECT 
                sa.ID_Suscripcion,
                h.Nombre,
                h.Apellido,
                pa.Nombre_Plan,
                pa.Precio_Mensual,
                sa.Fecha_Inicio,
                sa.Estado
            FROM suscripciones_almuerzo sa
            INNER JOIN hijos h ON sa.ID_Hijo = h.ID_Hijo
            INNER JOIN planes_almuerzo pa ON sa.ID_Plan_Almuerzo = pa.ID_Plan_Almuerzo
            WHERE sa.ID_Suscripcion = %s
        """, (id_suscripcion,))
        
        detalle = cursor.fetchone()
        if detalle:
            id_s, nom, ape, plan_nom, precio, fecha_ini, estado = detalle
            print_info(f"\n   📋 Resumen de suscripción:")
            print_info(f"     ID: {id_s}")
            print_info(f"     Estudiante: {nom} {ape}")
            print_info(f"     Plan: {plan_nom}")
            print_info(f"     Precio mensual: Gs. {float(precio):,.0f}")
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
# TEST 2: REGISTRO DE PAGO MENSUAL
# ============================================================================

def test_pago_mensual():
    """Prueba el registro de pago mensual de almuerzo"""
    print_header("TEST 2: Registro de Pago Mensual")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar suscripción activa
        cursor.execute("""
            SELECT 
                sa.ID_Suscripcion,
                h.Nombre,
                h.Apellido,
                pa.Nombre_Plan,
                pa.Precio_Mensual
            FROM suscripciones_almuerzo sa
            INNER JOIN hijos h ON sa.ID_Hijo = h.ID_Hijo
            INNER JOIN planes_almuerzo pa ON sa.ID_Plan_Almuerzo = pa.ID_Plan_Almuerzo
            WHERE sa.Estado = 'Activa'
            LIMIT 1
        """)
        
        suscripcion = cursor.fetchone()
        if not suscripcion:
            print_info("No hay suscripciones activas")
            return True
        
        id_suscripcion, nombre, apellido, plan, precio = suscripcion
        print_info(f"Suscripción ID: {id_suscripcion}")
        print_info(f"Estudiante: {nombre} {apellido}")
        print_info(f"Plan: {plan}")
        print_info(f"Precio: Gs. {float(precio):,.0f}")
        
        # Verificar si ya hay pago este mes
        mes_actual = date.today().replace(day=1)
        
        cursor.execute("""
            SELECT ID_Pago_Almuerzo, Monto_Pagado, Fecha_Pago, Estado
            FROM pagos_almuerzo_mensual
            WHERE ID_Suscripcion = %s
            AND Mes_Pagado = %s
        """, (id_suscripcion, mes_actual))
        
        pago_existente = cursor.fetchone()
        
        if pago_existente:
            id_pago, monto, fecha_pago, estado = pago_existente
            print_info(f"\nYa existe pago para este mes:")
            print_info(f"  ID Pago: {id_pago}")
            print_info(f"  Monto: Gs. {float(monto):,.0f}")
            print_info(f"  Fecha: {fecha_pago.strftime('%d/%m/%Y')}")
            print_info(f"  Estado: {estado}")
        else:
            # Registrar pago del mes
            cursor.execute("""
                INSERT INTO pagos_almuerzo_mensual
                (ID_Suscripcion, Fecha_Pago, Monto_Pagado, Mes_Pagado, Estado)
                VALUES (%s, NOW(), %s, %s, 'Pagado')
            """, (id_suscripcion, precio, mes_actual))
            
            id_pago = cursor.lastrowid
            print_success(f"\n✅ Pago registrado exitosamente")
            print_info(f"   ID Pago: {id_pago}")
            print_info(f"   Monto: Gs. {float(precio):,.0f}")
            print_info(f"   Mes: {mes_actual.strftime('%B %Y')}")
        
        # Consultar historial de pagos
        cursor.execute("""
            SELECT 
                pam.Mes_Pagado,
                pam.Monto_Pagado,
                pam.Fecha_Pago,
                pam.Estado
            FROM pagos_almuerzo_mensual pam
            WHERE pam.ID_Suscripcion = %s
            ORDER BY pam.Mes_Pagado DESC
            LIMIT 5
        """, (id_suscripcion,))
        
        historial = cursor.fetchall()
        
        if historial:
            print_info(f"\n   📊 Historial de pagos:")
            print_info(f"   {'Mes':<15} {'Monto':>15} {'Fecha Pago':<15} {'Estado':<10}")
            print_info(f"   {'-'*60}")
            for mes, monto, fecha, estado in historial:
                mes_str = mes.strftime('%Y-%m')
                fecha_str = fecha.strftime('%d/%m/%Y')
                print_info(f"   {mes_str:<15} Gs. {float(monto):>11,.0f} {fecha_str:<15} {estado:<10}")
        
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
# TEST 3: REGISTRO DE CONSUMO DIARIO
# ============================================================================

def test_consumo_diario():
    """Prueba el registro de consumo diario de almuerzo"""
    print_header("TEST 3: Registro de Consumo Diario")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar suscripción activa con pago al día
        cursor.execute("""
            SELECT 
                sa.ID_Suscripcion,
                sa.ID_Hijo,
                h.Nombre,
                h.Apellido,
                pa.Nombre_Plan
            FROM suscripciones_almuerzo sa
            INNER JOIN hijos h ON sa.ID_Hijo = h.ID_Hijo
            INNER JOIN planes_almuerzo pa ON sa.ID_Plan_Almuerzo = pa.ID_Plan_Almuerzo
            WHERE sa.Estado = 'Activa'
            LIMIT 1
        """)
        
        suscripcion = cursor.fetchone()
        if not suscripcion:
            print_info("No hay suscripciones activas")
            return True
        
        id_suscripcion, id_hijo, nombre, apellido, plan = suscripcion
        print_info(f"Estudiante: {nombre} {apellido}")
        print_info(f"Plan: {plan}")
        
        # Verificar si ya consumió hoy
        hoy = date.today()
        
        cursor.execute("""
            SELECT ID_Registro_Consumo, Fecha_Consumo
            FROM registro_consumo_almuerzo
            WHERE ID_Hijo = %s
            AND Fecha_Consumo = %s
        """, (id_hijo, hoy))
        
        consumo_existente = cursor.fetchone()
        
        if consumo_existente:
            id_registro, fecha = consumo_existente
            print_info(f"\nYa registró consumo hoy:")
            print_info(f"  ID Registro: {id_registro}")
            print_info(f"  Fecha: {fecha.strftime('%d/%m/%Y')}")
        else:
            # Registrar consumo del día
            cursor.execute("""
                INSERT INTO registro_consumo_almuerzo
                (ID_Hijo, Fecha_Consumo, ID_Suscripcion)
                VALUES (%s, %s, %s)
            """, (id_hijo, hoy, id_suscripcion))
            
            id_registro = cursor.lastrowid
            print_success(f"\n✅ Consumo registrado exitosamente")
            print_info(f"   ID Registro: {id_registro}")
            print_info(f"   Estudiante: {nombre} {apellido}")
            print_info(f"   Fecha: {hoy.strftime('%d/%m/%Y')}")
        
        # Consultar consumos del mes
        primer_dia_mes = hoy.replace(day=1)
        
        cursor.execute("""
            SELECT COUNT(*) as cantidad
            FROM registro_consumo_almuerzo
            WHERE ID_Hijo = %s
            AND Fecha_Consumo >= %s
        """, (id_hijo, primer_dia_mes))
        
        cantidad_mes = cursor.fetchone()[0]
        
        print_info(f"\n   📅 Consumos este mes: {cantidad_mes}")
        
        # Últimos 5 consumos
        cursor.execute("""
            SELECT 
                rca.Fecha_Consumo,
                h.Nombre,
                h.Apellido
            FROM registro_consumo_almuerzo rca
            INNER JOIN hijos h ON rca.ID_Hijo = h.ID_Hijo
            WHERE rca.ID_Hijo = %s
            ORDER BY rca.Fecha_Consumo DESC
            LIMIT 5
        """, (id_hijo,))
        
        ultimos = cursor.fetchall()
        
        if ultimos:
            print_info(f"\n   📋 Últimos consumos:")
            for fecha, nom, ape in ultimos:
                print_info(f"     {fecha.strftime('%d/%m/%Y')} - {nom} {ape}")
        
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
# TEST 4: CONSULTA DE SUSCRIPCIONES Y PAGOS
# ============================================================================

def test_consulta_pagos():
    """Prueba la consulta de suscripciones y pagos"""
    print_header("TEST 4: Consulta de Suscripciones y Pagos")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Suscripciones activas
        cursor.execute("""
            SELECT 
                sa.ID_Suscripcion,
                h.Nombre,
                h.Apellido,
                pa.Nombre_Plan,
                pa.Precio_Mensual,
                sa.Fecha_Inicio,
                sa.Estado
            FROM suscripciones_almuerzo sa
            INNER JOIN hijos h ON sa.ID_Hijo = h.ID_Hijo
            INNER JOIN planes_almuerzo pa ON sa.ID_Plan_Almuerzo = pa.ID_Plan_Almuerzo
            WHERE sa.Estado = 'Activa'
            ORDER BY h.Apellido, h.Nombre
            LIMIT 10
        """)
        
        suscripciones = cursor.fetchall()
        
        if not suscripciones:
            print_info("No hay suscripciones activas")
            return True
        
        print_success(f"✅ {len(suscripciones)} suscripción(es) activa(s)")
        
        print("\n   📋 Suscripciones activas:")
        print(f"   {'ID':<6} {'Estudiante':<25} {'Plan':<20} {'Precio':>15} {'Desde':<12}")
        print(f"   {'-'*85}")
        
        for sus in suscripciones:
            id_s, nom, ape, plan, precio, fecha, estado = sus
            estudiante = f"{nom} {ape}"[:23]
            plan_nom = plan[:18]
            fecha_str = fecha.strftime('%d/%m/%Y')
            print(f"   {id_s:<6} {estudiante:<25} {plan_nom:<20} Gs. {float(precio):>11,.0f} {fecha_str:<12}")
        
        # Pagos del mes actual
        mes_actual = date.today().replace(day=1)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as cantidad,
                SUM(Monto_Pagado) as total,
                COUNT(CASE WHEN Estado = 'Pagado' THEN 1 END) as pagados,
                COUNT(CASE WHEN Estado = 'Pendiente' THEN 1 END) as pendientes
            FROM pagos_almuerzo_mensual
            WHERE Mes_Pagado = %s
        """, (mes_actual,))
        
        stats = cursor.fetchone()
        if stats:
            cantidad, total, pagados, pendientes = stats
            total_val = float(total) if total else 0
            
            print(f"\n   💰 Pagos del mes actual ({mes_actual.strftime('%B %Y')}):")
            print_info(f"     Total pagos: {cantidad}")
            print_info(f"     Pagados: {pagados}")
            print_info(f"     Pendientes: {pendientes}")
            print_info(f"     Monto total: Gs. {total_val:,.0f}")
        
        # Pagos pendientes
        cursor.execute("""
            SELECT 
                h.Nombre,
                h.Apellido,
                pa.Nombre_Plan,
                pam.Monto_Pagado,
                pam.Mes_Pagado
            FROM pagos_almuerzo_mensual pam
            INNER JOIN suscripciones_almuerzo sa ON pam.ID_Suscripcion = sa.ID_Suscripcion
            INNER JOIN hijos h ON sa.ID_Hijo = h.ID_Hijo
            INNER JOIN planes_almuerzo pa ON sa.ID_Plan_Almuerzo = pa.ID_Plan_Almuerzo
            WHERE pam.Estado = 'Pendiente'
            ORDER BY pam.Mes_Pagado DESC
            LIMIT 5
        """)
        
        pendientes_lista = cursor.fetchall()
        
        if pendientes_lista:
            print(f"\n   ⚠️  Pagos pendientes:")
            print(f"   {'Estudiante':<25} {'Plan':<20} {'Monto':>15} {'Mes':<10}")
            print(f"   {'-'*75}")
            for nom, ape, plan, monto, mes in pendientes_lista:
                estudiante = f"{nom} {ape}"[:23]
                plan_nom = plan[:18]
                mes_str = mes.strftime('%Y-%m')
                print(f"   {estudiante:<25} {plan_nom:<20} Gs. {float(monto):>11,.0f} {mes_str:<10}")
        
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# TEST 5: REPORTES DE CONSUMO
# ============================================================================

def test_reportes_consumo():
    """Prueba la generación de reportes de consumo de almuerzos"""
    print_header("TEST 5: Reportes de Consumo de Almuerzos")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Estadísticas generales
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT sa.ID_Suscripcion) as suscripciones_activas,
                COUNT(DISTINCT sa.ID_Hijo) as estudiantes_suscritos,
                COUNT(DISTINCT pa.ID_Plan_Almuerzo) as planes_en_uso
            FROM suscripciones_almuerzo sa
            INNER JOIN planes_almuerzo pa ON sa.ID_Plan_Almuerzo = pa.ID_Plan_Almuerzo
            WHERE sa.Estado = 'Activa'
        """)
        
        stats = cursor.fetchone()
        if stats:
            suscripciones, estudiantes, planes = stats
            
            print_info("📊 Estadísticas generales:")
            print_info(f"  Suscripciones activas: {suscripciones}")
            print_info(f"  Estudiantes suscritos: {estudiantes}")
            print_info(f"  Planes en uso: {planes}")
        
        # Consumos del mes actual
        primer_dia_mes = date.today().replace(day=1)
        
        cursor.execute("""
            SELECT COUNT(*) as total_consumos
            FROM registro_consumo_almuerzo
            WHERE Fecha_Consumo >= %s
        """, (primer_dia_mes,))
        
        total_consumos = cursor.fetchone()[0]
        print_info(f"\n  💵 Total consumos este mes: {total_consumos}")
        
        # Top 5 estudiantes con más consumos este mes
        cursor.execute("""
            SELECT 
                h.Nombre,
                h.Apellido,
                COUNT(*) as cantidad_consumos
            FROM registro_consumo_almuerzo rca
            INNER JOIN hijos h ON rca.ID_Hijo = h.ID_Hijo
            WHERE rca.Fecha_Consumo >= %s
            GROUP BY h.ID_Hijo, h.Nombre, h.Apellido
            ORDER BY cantidad_consumos DESC
            LIMIT 5
        """, (primer_dia_mes,))
        
        top_consumidores = cursor.fetchall()
        
        if top_consumidores:
            print(f"\n   🏆 Top estudiantes este mes:")
            print(f"   {'Estudiante':<30} {'Consumos':>10}")
            print(f"   {'-'*45}")
            for nom, ape, cant in top_consumidores:
                estudiante = f"{nom} {ape}"[:28]
                print(f"   {estudiante:<30} {cant:>10}")
        
        # Planes más populares
        cursor.execute("""
            SELECT 
                pa.Nombre_Plan,
                COUNT(sa.ID_Suscripcion) as cantidad_suscripciones,
                pa.Precio_Mensual
            FROM planes_almuerzo pa
            LEFT JOIN suscripciones_almuerzo sa ON pa.ID_Plan_Almuerzo = sa.ID_Plan_Almuerzo
                AND sa.Estado = 'Activa'
            GROUP BY pa.ID_Plan_Almuerzo, pa.Nombre_Plan, pa.Precio_Mensual
            ORDER BY cantidad_suscripciones DESC
        """)
        
        planes_stats = cursor.fetchall()
        
        if planes_stats:
            print(f"\n   📈 Popularidad de planes:")
            print(f"   {'Plan':<30} {'Suscripciones':>15} {'Precio':>15}")
            print(f"   {'-'*65}")
            for plan, cant, precio in planes_stats:
                plan_nom = plan[:28]
                print(f"   {plan_nom:<30} {cant:>15} Gs. {float(precio):>11,.0f}")
        
        # Consumos por día de la semana
        cursor.execute("""
            SELECT 
                DAYNAME(Fecha_Consumo) as dia_semana,
                COUNT(*) as cantidad
            FROM registro_consumo_almuerzo
            WHERE Fecha_Consumo >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY DAYOFWEEK(Fecha_Consumo), DAYNAME(Fecha_Consumo)
            ORDER BY DAYOFWEEK(Fecha_Consumo)
        """)
        
        por_dia = cursor.fetchall()
        
        if por_dia:
            print(f"\n   📅 Consumos por día de la semana (últimos 30 días):")
            print(f"   {'Día':<15} {'Cantidad':>10}")
            print(f"   {'-'*30}")
            for dia, cant in por_dia:
                print(f"   {dia:<15} {cant:>10}")
        
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
    print("█          TEST COMPLETO - ALMUERZOS MENSUALES (REDISEÑADO)         █")
    print("█                                                                    █")
    print("█" * 70)
    
    tests = [
        ("Suscripción a Plan", test_suscripcion_plan),
        ("Registro de Pago Mensual", test_pago_mensual),
        ("Registro de Consumo Diario", test_consumo_diario),
        ("Consulta de Suscripciones y Pagos", test_consulta_pagos),
        ("Reportes de Consumo", test_reportes_consumo),
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
        print("\n🎉 ¡PERFECTO! Todos los tests de almuerzos pasaron.")
    else:
        print(f"\n⚠️  {total - exitosos} test(s) fallaron.")
    
    print("\n")
    return exitosos == total

if __name__ == "__main__":
    exit(0 if main() else 1)
