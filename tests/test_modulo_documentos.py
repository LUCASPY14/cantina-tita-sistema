#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST MÓDULO - DOCUMENTOS TRIBUTARIOS (REDISEÑADO)
==================================================
Pruebas del sistema de documentos tributarios emitidos.

NOTA: Este módulo trabaja con documentos YA EMITIDOS,
no con control de rangos de timbrados.

COBERTURA:
- Creación de documentos tributarios
- Consulta de documentos emitidos
- Validación de integridad
- Estadísticas de documentos
- Reportes de uso
"""

import MySQLdb
from datetime import datetime, timedelta

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
# TEST 1: CREACIÓN DE DOCUMENTOS TRIBUTARIOS
# ============================================================================

def test_crear_documentos():
    """Prueba la creación de nuevos documentos tributarios"""
    print_header("TEST 1: Creación de Documentos Tributarios")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Crear 3 documentos tributarios de prueba
        timbrado = "12345678"
        documentos_creados = []
        
        print_info("Creando 3 documentos tributarios...")
        
        for i in range(3):
            secuencial = 5000 + i
            monto = 50000 + (i * 10000)
            
            cursor.execute("""
                INSERT INTO documentos_tributarios
                (Nro_Timbrado, Nro_Secuencial, Fecha_Emision, Monto_Total, 
                 Monto_Exento, Monto_Gravado_5, Monto_IVA_5, Monto_Gravado_10, Monto_IVA_10)
                VALUES (%s, %s, NOW(), %s, 0, 0, 0, 0, 0)
            """, (timbrado, secuencial, monto))
            
            id_doc = cursor.lastrowid
            documentos_creados.append((id_doc, secuencial, monto))
            print_info(f"  Doc #{id_doc}: Timbrado {timbrado}, Secuencial {secuencial}, Monto Gs. {monto:,}")
        
        # Verificar que se crearon correctamente
        cursor.execute("""
            SELECT COUNT(*) 
            FROM documentos_tributarios 
            WHERE Nro_Timbrado = %s
            AND Nro_Secuencial >= 5000
        """, (timbrado,))
        
        count = cursor.fetchone()[0]
        
        if count >= 3:
            print_success(f"\n✅ {count} documento(s) creado(s) exitosamente")
            print_info(f"   Timbrado: {timbrado}")
            print_info(f"   Rango secuencial: 5000-5002")
        else:
            print_error(f"Error: Solo se encontraron {count} documentos")
            return False
        
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
# TEST 2: CONSULTA DE DOCUMENTOS EMITIDOS
# ============================================================================

def test_consulta_documentos():
    """Prueba la consulta de documentos tributarios emitidos"""
    print_header("TEST 2: Consulta de Documentos Emitidos")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Consultar documentos recientes (últimos 30 días)
        cursor.execute("""
            SELECT 
                ID_Documento,
                Nro_Timbrado,
                Nro_Secuencial,
                Fecha_Emision,
                Monto_Total
            FROM documentos_tributarios
            WHERE Fecha_Emision > DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            ORDER BY Fecha_Emision DESC
            LIMIT 10
        """)
        
        documentos = cursor.fetchall()
        
        if not documentos:
            print_error("No se encontraron documentos recientes")
            return False
        
        print_success(f"✅ {len(documentos)} documento(s) encontrado(s)")
        print(f"\n   {'ID':<8} {'Timbrado':<12} {'Secuencial':<12} {'Monto':>15} {'Fecha':<20}")
        print(f"   {'-'*72}")
        
        total_monto = 0
        for doc in documentos:
            id_doc, timbrado, secuencial, fecha, monto = doc
            fecha_str = fecha.strftime('%d/%m/%Y %H:%M')
            print(f"   {id_doc:<8} {timbrado:<12} {secuencial:<12} Gs. {float(monto):>11,.0f} {fecha_str:<20}")
            total_monto += float(monto)
        
        print(f"\n   💰 Monto total: Gs. {total_monto:,.0f}")
        
        # Verificar secuenciales únicos
        cursor.execute("""
            SELECT 
                Nro_Timbrado,
                Nro_Secuencial,
                COUNT(*) as duplicados
            FROM documentos_tributarios
            GROUP BY Nro_Timbrado, Nro_Secuencial
            HAVING duplicados > 1
        """)
        
        duplicados = cursor.fetchall()
        
        if duplicados:
            print_error(f"\n⚠️  {len(duplicados)} secuencial(es) duplicado(s) encontrado(s)")
            for timb, sec, count in duplicados:
                print_info(f"     Timbrado {timb}, Secuencial {sec}: {count} veces")
        else:
            print_success(f"\n✅ Todos los secuenciales son únicos")
        
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# TEST 3: VALIDACIÓN DE INTEGRIDAD
# ============================================================================

def test_validacion_integridad():
    """Prueba la validación de integridad de documentos"""
    print_header("TEST 3: Validación de Integridad")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Verificar documentos con montos inválidos
        cursor.execute("""
            SELECT ID_Documento, Nro_Timbrado, Nro_Secuencial, Monto_Total
            FROM documentos_tributarios
            WHERE Monto_Total <= 0
        """)
        
        invalidos = cursor.fetchall()
        
        if invalidos:
            print_error(f"❌ {len(invalidos)} documento(s) con monto inválido:")
            for id_doc, timb, sec, monto in invalidos:
                print_info(f"     Doc #{id_doc} (Timb {timb}, Sec {sec}): Gs. {float(monto):,.0f}")
        else:
            print_success("✅ Todos los documentos tienen montos válidos")
        
        # Verificar documentos con timbrados válidos (8 dígitos)
        cursor.execute("""
            SELECT ID_Documento, Nro_Timbrado, Nro_Secuencial
            FROM documentos_tributarios
            WHERE LENGTH(Nro_Timbrado) != 8
        """)
        
        timbrados_invalidos = cursor.fetchall()
        
        if timbrados_invalidos:
            print_error(f"\n❌ {len(timbrados_invalidos)} documento(s) con timbrado inválido:")
            for id_doc, timb, sec in timbrados_invalidos:
                print_info(f"     Doc #{id_doc}: Timbrado '{timb}' (longitud: {len(str(timb))})")
        else:
            print_success("\n✅ Todos los timbrados tienen formato válido")
        
        # Verificar consistencia de IVA
        cursor.execute("""
            SELECT 
                ID_Documento,
                Nro_Timbrado,
                Nro_Secuencial,
                Monto_Total,
                (COALESCE(Monto_Exento, 0) + 
                 COALESCE(Monto_Gravado_5, 0) + 
                 COALESCE(Monto_Gravado_10, 0)) as suma_montos
            FROM documentos_tributarios
            WHERE ABS(Monto_Total - (COALESCE(Monto_Exento, 0) + 
                                     COALESCE(Monto_Gravado_5, 0) + 
                                     COALESCE(Monto_Gravado_10, 0))) > 1
            LIMIT 10
        """)
        
        inconsistentes = cursor.fetchall()
        
        if inconsistentes:
            print_error(f"\n⚠️  {len(inconsistentes)} documento(s) con inconsistencia en montos:")
            for id_doc, timb, sec, total, suma in inconsistentes:
                diff = abs(float(total) - float(suma))
                print_info(f"     Doc #{id_doc}: Total Gs. {float(total):,.0f} vs Suma Gs. {float(suma):,.0f} (Diff: Gs. {diff:,.0f})")
        else:
            print_success("\n✅ Montos consistentes en todos los documentos")
        
        # Estadísticas generales
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                MIN(Fecha_Emision) as primera_emision,
                MAX(Fecha_Emision) as ultima_emision,
                SUM(Monto_Total) as monto_total
            FROM documentos_tributarios
        """)
        
        stats = cursor.fetchone()
        total, primera, ultima, monto_total = stats
        
        print(f"\n   📊 Estadísticas generales:")
        print_info(f"     Total documentos: {total}")
        print_info(f"     Primera emisión: {primera.strftime('%d/%m/%Y') if primera else 'N/A'}")
        print_info(f"     Última emisión: {ultima.strftime('%d/%m/%Y') if ultima else 'N/A'}")
        print_info(f"     Monto total: Gs. {float(monto_total):,.0f}" if monto_total else "     Monto total: Gs. 0")
        
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# TEST 4: ESTADÍSTICAS DE DOCUMENTOS
# ============================================================================

def test_estadisticas_documentos():
    """Prueba las estadísticas de documentos por timbrado"""
    print_header("TEST 4: Estadísticas por Timbrado")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Documentos por timbrado
        cursor.execute("""
            SELECT 
                Nro_Timbrado,
                COUNT(*) as cantidad,
                SUM(Monto_Total) as monto_total,
                MIN(Fecha_Emision) as primera,
                MAX(Fecha_Emision) as ultima
            FROM documentos_tributarios
            GROUP BY Nro_Timbrado
            ORDER BY cantidad DESC
        """)
        
        timbrados = cursor.fetchall()
        
        if not timbrados:
            print_error("No se encontraron timbrados")
            return False
        
        print_success(f"✅ {len(timbrados)} timbrado(s) encontrado(s)")
        print(f"\n   {'Timbrado':<12} {'Docs':>8} {'Monto Total':>18} {'Primera':>12} {'Última':>12}")
        print(f"   {'-'*72}")
        
        for timb, cant, monto, primera, ultima in timbrados:
            primera_str = primera.strftime('%d/%m/%Y') if primera else 'N/A'
            ultima_str = ultima.strftime('%d/%m/%Y') if ultima else 'N/A'
            print(f"   {timb:<12} {cant:>8} Gs. {float(monto):>14,.0f} {primera_str:>12} {ultima_str:>12}")
        
        # Documentos por mes
        cursor.execute("""
            SELECT 
                DATE_FORMAT(Fecha_Emision, '%Y-%m') as mes,
                COUNT(*) as cantidad,
                SUM(Monto_Total) as monto_total
            FROM documentos_tributarios
            WHERE Fecha_Emision > DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY mes
            ORDER BY mes DESC
        """)
        
        meses = cursor.fetchall()
        
        if meses:
            print(f"\n   📅 Documentos por mes (últimos 6 meses):")
            print(f"   {'Mes':<10} {'Cantidad':>10} {'Monto Total':>20}")
            print(f"   {'-'*45}")
            
            for mes, cant, monto in meses:
                print(f"   {mes:<10} {cant:>10} Gs. {float(monto):>16,.0f}")
        
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# TEST 5: REPORTES DE USO
# ============================================================================

def test_reportes_uso():
    """Prueba los reportes de uso de documentos"""
    print_header("TEST 5: Reportes de Uso de Documentos")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Documentos vinculados a ventas
        cursor.execute("""
            SELECT 
                dt.Nro_Timbrado,
                COUNT(DISTINCT v.ID_Venta) as ventas_asociadas,
                SUM(v.Monto_Total) as monto_ventas,
                COUNT(DISTINCT dt.ID_Documento) as docs_usados
            FROM documentos_tributarios dt
            LEFT JOIN ventas v ON dt.ID_Documento = v.ID_Documento
            GROUP BY dt.Nro_Timbrado
            ORDER BY ventas_asociadas DESC
        """)
        
        uso = cursor.fetchall()
        
        if not uso:
            print_error("No se encontraron datos de uso")
            return False
        
        print_success(f"✅ Reporte generado para {len(uso)} timbrado(s)")
        print(f"\n   {'Timbrado':<12} {'Ventas':>8} {'Docs Usados':>12} {'Monto Ventas':>20}")
        print(f"   {'-'*60}")
        
        total_ventas = 0
        total_docs = 0
        
        for timb, ventas, monto, docs in uso:
            ventas_count = ventas if ventas else 0
            monto_val = float(monto) if monto else 0
            docs_count = docs if docs else 0
            
            total_ventas += ventas_count
            total_docs += docs_count
            
            print(f"   {timb:<12} {ventas_count:>8} {docs_count:>12} Gs. {monto_val:>16,.0f}")
        
        print(f"   {'-'*60}")
        print(f"   {'TOTAL':<12} {total_ventas:>8} {total_docs:>12}")
        
        # Documentos sin usar
        cursor.execute("""
            SELECT COUNT(*)
            FROM documentos_tributarios dt
            LEFT JOIN ventas v ON dt.ID_Documento = v.ID_Documento
            WHERE v.ID_Venta IS NULL
        """)
        
        sin_usar = cursor.fetchone()[0]
        
        if sin_usar > 0:
            print(f"\n   ℹ️  {sin_usar} documento(s) aún no vinculado(s) a ventas")
        else:
            print(f"\n   ✅ Todos los documentos están vinculados a ventas")
        
        # Promedio de uso
        if total_docs > 0 and len(uso) > 0:
            promedio_ventas = total_ventas / len(uso)
            promedio_docs = total_docs / len(uso)
            print(f"\n   📊 Promedios:")
            print_info(f"     Ventas por timbrado: {promedio_ventas:.1f}")
            print_info(f"     Documentos por timbrado: {promedio_docs:.1f}")
        
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# EJECUCIÓN DE TODOS LOS TESTS
# ============================================================================

def main():
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "    TEST COMPLETO - DOCUMENTOS TRIBUTARIOS (REDISEÑADO)".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    tests = [
        ("Creación de Documentos", test_crear_documentos),
        ("Consulta de Documentos", test_consulta_documentos),
        ("Validación de Integridad", test_validacion_integridad),
        ("Estadísticas de Documentos", test_estadisticas_documentos),
        ("Reportes de Uso", test_reportes_uso)
    ]
    
    resultados = {}
    
    for nombre, test_func in tests:
        resultado = test_func()
        resultados[nombre] = resultado
    
    # Resumen final
    print_header("RESUMEN DE RESULTADOS")
    
    exitosos = sum(1 for r in resultados.values() if r)
    total = len(resultados)
    
    for nombre, resultado in resultados.items():
        simbolo = "✅ PASS" if resultado else "❌ FAIL"
        print(f"{simbolo} - {nombre}")
    
    print(f"\n{'='*70}")
    print(f"Total: {exitosos}/{total} tests exitosos ({exitosos/total*100:.1f}%)")
    print(f"{'='*70}\n")
    
    if exitosos == total:
        print("🎉 ¡PERFECTO! Todos los tests de documentos tributarios pasaron.")
    else:
        print(f"⚠️  {total - exitosos} test(s) fallaron.")
    
    return exitosos == total

if __name__ == "__main__":
    exit(0 if main() else 1)
