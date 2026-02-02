#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST MÓDULO - ALMUERZOS MENSUALES
==================================
Pruebas del sistema de registro y cobro de almuerzos.

COBERTURA:
- Registro mensual de almuerzos
- Cobro automático mensual
- Registro de asistencia diaria
- Consulta de pagos
- Reportes mensuales
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
# TEST 1: REGISTRO MENSUAL DE ALMUERZO
# ============================================================================

def test_registro_almuerzo():
    """Prueba el registro de un alumno para almuerzos del mes"""
    print_header("TEST 1: Registro Mensual de Almuerzo")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar un hijo/estudiante activo
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
        
        # Verificar si ya tiene registro este mes
        mes_actual = datetime.now().strftime('%Y-%m-01')
        
        cursor.execute("""
            SELECT ID_Almuerzo 
            FROM pagos_almuerzo_mensual 
            WHERE ID_Hijo = %s 
            AND DATE_FORMAT(Mes, '%%Y-%%m') = DATE_FORMAT(%s, '%%Y-%%m')
        """, (id_hijo, mes_actual))
        
        registro_existente = cursor.fetchone()
        
        if registro_existente:
            print_info(f"Ya existe registro para este mes (ID: {registro_existente[0]})")
            id_almuerzo = registro_existente[0]
        else:
            # Registrar almuerzo mensual
            precio_mes = 180000  # Gs. 180,000 por mes
            
            cursor.execute("""
                INSERT INTO pagos_almuerzo_mensual
                (ID_Hijo, ID_Cliente, Mes, Precio_Mensual, Estado_Pago)
                VALUES (%s, %s, %s, %s, 'Pendiente')
            """, (id_hijo, id_cliente, mes_actual, precio_mes))
            
            id_almuerzo = cursor.lastrowid
            print_success(f"✅ Almuerzo registrado (ID: {id_almuerzo})")
        
        # Consultar detalles del registro
        cursor.execute("""
            SELECT 
                am.ID_Almuerzo,
                h.Nombre,
                h.Apellido,
                am.Mes,
                am.Precio_Mensual,
                am.Estado_Pago
            FROM pagos_almuerzo_mensual am
            INNER JOIN hijos h ON am.ID_Hijo = h.ID_Hijo
            WHERE am.ID_Almuerzo = %s
        """, (id_almuerzo,))
        
        detalle = cursor.fetchone()
        if detalle:
            id_alm, nom, ape, mes, precio, estado = detalle
            print_info(f"   Estudiante: {nom} {ape}")
            print_info(f"   Mes: {mes.strftime('%B %Y')}")
            print_info(f"   Precio: Gs. {float(precio):,.0f}")
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
# TEST 2: COBRO AUTOMÁTICO MENSUAL
# ============================================================================

def test_cobro_mensual():
    """Prueba el cobro automático de almuerzos mensuales"""
    print_header("TEST 2: Cobro Automático Mensual")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Crear registro de almuerzo pendiente
        cursor.execute("""
            SELECT h.ID_Hijo, h.ID_Cliente_Responsable
            FROM hijos h
            INNER JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
            WHERE c.Activo = TRUE
            LIMIT 1
        """)
        
        hijo = cursor.fetchone()
        if not hijo:
            print_error("No hay estudiantes disponibles")
            return False
        
        id_hijo, id_cliente = hijo
        mes_actual = datetime.now().strftime('%Y-%m-01')
        precio_mes = 180000
        
        # Registrar almuerzo
        cursor.execute("""
            INSERT INTO pagos_almuerzo_mensual
            (ID_Hijo, ID_Cliente, Mes, Precio_Mensual, Estado_Pago)
            VALUES (%s, %s, %s, %s, 'Pendiente')
        """, (id_hijo, id_cliente, mes_actual, precio_mes))
        
        id_almuerzo = cursor.lastrowid
        print_info(f"Almuerzo creado: ID {id_almuerzo} - Gs. {precio_mes:,.0f}")
        
        # Procesar cobro (simular generación de venta/documento)
        cursor.execute("""
            SELECT ID_Documento 
            FROM documentos_tributarios 
            WHERE Activo = TRUE 
            LIMIT 1
        """)
        
        doc = cursor.fetchone()
        id_documento = doc[0] if doc else None
        
        # Registrar pago
        cursor.execute("""
            INSERT INTO pagos_almuerzo_mensual
            (ID_Almuerzo, Monto_Pagado, Fecha_Pago, Medio_Pago, ID_Documento)
            VALUES (%s, %s, NOW(), 'Efectivo', %s)
        """, (id_almuerzo, precio_mes, id_documento))
        
        id_pago = cursor.lastrowid
        
        # Actualizar estado del almuerzo
        cursor.execute("""
            UPDATE almuerzos_mensuales
            SET Estado_Pago = 'Pagado'
            WHERE ID_Almuerzo = %s
        """, (id_almuerzo,))
        
        print_success(f"\n✅ Cobro procesado exitosamente")
        print_info(f"   ID Pago: {id_pago}")
        print_info(f"   Monto: Gs. {precio_mes:,.0f}")
        print_info(f"   Medio: Efectivo")
        print_info(f"   Estado actualizado: Pagado")
        
        # Verificar pago registrado
        cursor.execute("""
            SELECT 
                pa.ID_Pago_Almuerzo,
                pa.Monto_Pagado,
                pa.Fecha_Pago,
                am.Estado_Pago
            FROM pagos_almuerzo_mensual pa
            INNER JOIN almuerzos_mensuales am ON pa.ID_Almuerzo = am.ID_Almuerzo
            WHERE pa.ID_Pago_Almuerzo = %s
        """, (id_pago,))
        
        verificacion = cursor.fetchone()
        if verificacion:
            id_p, monto, fecha, estado = verificacion
            print_info(f"\n   ✓ Verificación exitosa:")
            print_info(f"     Pago ID {id_p} registrado")
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
# TEST 3: REGISTRO DE ASISTENCIA DIARIA
# ============================================================================

def test_asistencia_diaria():
    """Prueba el registro de asistencia diaria al almuerzo"""
    print_header("TEST 3: Registro de Asistencia Diaria")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar almuerzo pagado del mes actual
        cursor.execute("""
            SELECT am.ID_Almuerzo, h.Nombre, h.Apellido
            FROM pagos_almuerzo_mensual am
            INNER JOIN hijos h ON am.ID_Hijo = h.ID_Hijo
            WHERE am.Estado_Pago = 'Pagado'
            AND DATE_FORMAT(am.Mes, '%%Y-%%m') = DATE_FORMAT(NOW(), '%%Y-%%m')
            LIMIT 1
        """)
        
        almuerzo = cursor.fetchone()
        
        if not almuerzo:
            # Crear uno para probar
            cursor.execute("""
                SELECT h.ID_Hijo, h.ID_Cliente_Responsable, h.Nombre, h.Apellido
                FROM hijos h
                INNER JOIN clientes c ON h.ID_Cliente_Responsable = c.ID_Cliente
                WHERE c.Activo = TRUE
                LIMIT 1
            """)
            
            hijo = cursor.fetchone()
            if not hijo:
                print_error("No hay estudiantes disponibles")
                return False
            
            id_hijo, id_cliente, nombre, apellido = hijo
            mes_actual = datetime.now().strftime('%Y-%m-01')
            
            cursor.execute("""
                INSERT INTO pagos_almuerzo_mensual
                (ID_Hijo, ID_Cliente, Mes, Precio_Mensual, Estado_Pago)
                VALUES (%s, %s, %s, 180000, 'Pagado')
            """, (id_hijo, id_cliente, mes_actual))
            
            id_almuerzo = cursor.lastrowid
        else:
            id_almuerzo, nombre, apellido = almuerzo
        
        print_info(f"Estudiante: {nombre} {apellido} (Almuerzo ID: {id_almuerzo})")
        
        # Registrar asistencia de varios días
        fechas_asistencia = [
            datetime.now().date(),
            datetime.now().date() - timedelta(days=1),
            datetime.now().date() - timedelta(days=2),
        ]
        
        registros_creados = 0
        
        for fecha in fechas_asistencia:
            # Verificar si ya existe registro
            cursor.execute("""
                SELECT ID_Asistencia 
                FROM asistencia_almuerzos 
                WHERE ID_Almuerzo = %s 
                AND DATE(Fecha_Asistencia) = %s
            """, (id_almuerzo, fecha))
            
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO asistencia_almuerzos
                    (ID_Almuerzo, Fecha_Asistencia, Asistio)
                    VALUES (%s, %s, TRUE)
                """, (id_almuerzo, fecha))
                
                registros_creados += 1
        
        print_success(f"\n✅ {registros_creados} registro(s) de asistencia creados")
        
        # Consultar asistencias del mes
        cursor.execute("""
            SELECT 
                DATE(aa.Fecha_Asistencia) as fecha,
                aa.Asistio
            FROM asistencia_almuerzos aa
            WHERE aa.ID_Almuerzo = %s
            ORDER BY aa.Fecha_Asistencia DESC
            LIMIT 10
        """, (id_almuerzo,))
        
        asistencias = cursor.fetchall()
        
        if asistencias:
            print_info(f"\n   📅 Registro de asistencias:")
            for fecha, asistio in asistencias:
                estado = "✓ Presente" if asistio else "✗ Ausente"
                print_info(f"     {fecha.strftime('%d/%m/%Y')}: {estado}")
            
            presentes = sum(1 for _, a in asistencias if a)
            print_info(f"\n   Total: {presentes}/{len(asistencias)} días presentes")
        
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
# TEST 4: CONSULTA DE PAGOS
# ============================================================================

def test_consulta_pagos():
    """Prueba la consulta de pagos de almuerzos"""
    print_header("TEST 4: Consulta de Pagos")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Consultar todos los pagos de almuerzos
        cursor.execute("""
            SELECT 
                pa.ID_Pago_Almuerzo,
                h.Nombre,
                h.Apellido,
                c.Nombres as nombre_padre,
                c.Apellidos as apellido_padre,
                am.Mes,
                pa.Monto_Pagado,
                pa.Fecha_Pago,
                pa.Medio_Pago
            FROM pagos_almuerzo_mensual pa
            INNER JOIN almuerzos_mensuales am ON pa.ID_Almuerzo = am.ID_Almuerzo
            INNER JOIN hijos h ON am.ID_Hijo = h.ID_Hijo
            INNER JOIN clientes c ON am.ID_Cliente = c.ID_Cliente
            ORDER BY pa.Fecha_Pago DESC
            LIMIT 10
        """)
        
        pagos = cursor.fetchall()
        
        print_success(f"✅ Consulta realizada: {len(pagos)} pago(s) encontrado(s)")
        
        if pagos:
            print("\n   📊 Últimos pagos registrados:")
            print(f"   {'Estudiante':<25} {'Padre/Tutor':<25} {'Mes':<12} {'Monto':>15} {'Fecha':<12}")
            print(f"   {'-'*95}")
            
            for pago in pagos:
                id_pago, nom_hijo, ape_hijo, nom_padre, ape_padre, mes, monto, fecha, medio = pago
                estudiante = f"{nom_hijo} {ape_hijo}"[:23]
                padre = f"{nom_padre} {ape_padre}"[:23]
                mes_str = mes.strftime('%Y-%m')
                fecha_str = fecha.strftime('%d/%m/%Y')
                
                print(f"   {estudiante:<25} {padre:<25} {mes_str:<12} Gs. {float(monto):>12,.0f} {fecha_str:<12}")
        
        # Estadísticas de pagos
        cursor.execute("""
            SELECT 
                COUNT(*) as total_pagos,
                SUM(Monto_Pagado) as total_recaudado,
                AVG(Monto_Pagado) as promedio,
                COUNT(DISTINCT am.ID_Cliente) as familias
            FROM pagos_almuerzo_mensual pa
            INNER JOIN almuerzos_mensuales am ON pa.ID_Almuerzo = am.ID_Almuerzo
            WHERE YEAR(pa.Fecha_Pago) = YEAR(NOW())
        """)
        
        stats = cursor.fetchone()
        if stats:
            total, recaudado, promedio, familias = stats
            
            print(f"\n   📈 Estadísticas del año:")
            print(f"   Total de pagos: {total}")
            print(f"   Total recaudado: Gs. {float(recaudado or 0):,.0f}")
            print(f"   Promedio por pago: Gs. {float(promedio or 0):,.0f}")
            print(f"   Familias participantes: {familias}")
        
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
# TEST 5: REPORTES MENSUALES
# ============================================================================

def test_reportes_mensuales():
    """Prueba la generación de reportes mensuales de almuerzos"""
    print_header("TEST 5: Reportes Mensuales")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Reporte del mes actual
        cursor.execute("""
            SELECT 
                am.Estado_Pago,
                COUNT(*) as cantidad,
                SUM(am.Precio_Mensual) as total
            FROM pagos_almuerzo_mensual am
            WHERE DATE_FORMAT(am.Mes, '%%Y-%%m') = DATE_FORMAT(NOW(), '%%Y-%%m')
            GROUP BY am.Estado_Pago
        """)
        
        resumen = cursor.fetchall()
        
        print_success("✅ Reporte mensual generado")
        
        if resumen:
            print(f"\n   📊 Resumen del mes actual:")
            print(f"   {'Estado':<15} {'Cantidad':>10} {'Total':>20}")
            print(f"   {'-'*50}")
            
            total_general = 0
            total_alumnos = 0
            
            for estado, cant, total in resumen:
                print(f"   {estado:<15} {cant:>10} Gs. {float(total):>15,.0f}")
                total_general += float(total)
                total_alumnos += cant
            
            print(f"   {'-'*50}")
            print(f"   {'TOTAL':<15} {total_alumnos:>10} Gs. {total_general:>15,.0f}")
        else:
            print_info("   No hay registros para el mes actual")
        
        # Listado detallado con asistencia
        cursor.execute("""
            SELECT 
                h.Nombre,
                h.Apellido,
                am.Estado_Pago,
                COUNT(aa.ID_Asistencia) as dias_asistidos
            FROM pagos_almuerzo_mensual am
            INNER JOIN hijos h ON am.ID_Hijo = h.ID_Hijo
            LEFT JOIN asistencia_almuerzos aa ON am.ID_Almuerzo = aa.ID_Almuerzo AND aa.Asistio = TRUE
            WHERE DATE_FORMAT(am.Mes, '%%Y-%%m') = DATE_FORMAT(NOW(), '%%Y-%%m')
            GROUP BY h.ID_Hijo, h.Nombre, h.Apellido, am.Estado_Pago
            ORDER BY h.Apellido, h.Nombre
            LIMIT 15
        """)
        
        detalle = cursor.fetchall()
        
        if detalle:
            print(f"\n   📋 Detalle por estudiante:")
            print(f"   {'Estudiante':<30} {'Estado':<15} {'Asistencias':>12}")
            print(f"   {'-'*60}")
            
            for nom, ape, estado, asist in detalle:
                estudiante = f"{nom} {ape}"[:28]
                print(f"   {estudiante:<30} {estado:<15} {asist:>12} días")
        
        # Comparación con meses anteriores
        cursor.execute("""
            SELECT 
                DATE_FORMAT(am.Mes, '%%Y-%%m') as mes,
                COUNT(*) as alumnos,
                SUM(CASE WHEN am.Estado_Pago = 'Pagado' THEN 1 ELSE 0 END) as pagados,
                SUM(am.Precio_Mensual) as total
            FROM pagos_almuerzo_mensual am
            WHERE am.Mes >= DATE_SUB(NOW(), INTERVAL 3 MONTH)
            GROUP BY mes
            ORDER BY mes DESC
        """)
        
        tendencia = cursor.fetchall()
        
        if tendencia:
            print(f"\n   📈 Tendencia últimos meses:")
            print(f"   {'Mes':<10} {'Alumnos':>10} {'Pagados':>10} {'Total':>20}")
            print(f"   {'-'*55}")
            
            for mes, alum, pag, tot in tendencia:
                print(f"   {mes:<10} {alum:>10} {pag:>10} Gs. {float(tot):>15,.0f}")
        
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
    print("█              TEST COMPLETO - ALMUERZOS MENSUALES                   █")
    print("█                                                                    █")
    print("█" * 70)
    
    tests = [
        ("Registro Mensual", test_registro_almuerzo),
        ("Cobro Automático", test_cobro_mensual),
        ("Asistencia Diaria", test_asistencia_diaria),
        ("Consulta de Pagos", test_consulta_pagos),
        ("Reportes Mensuales", test_reportes_mensuales),
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
        print("\n🎉 ¡PERFECTO! Todos los tests de almuerzos pasaron exitosamente.")
    else:
        print(f"\n⚠️  {total - exitosos} test(s) fallaron.")
    
    print("\n")

if __name__ == "__main__":
    main()
