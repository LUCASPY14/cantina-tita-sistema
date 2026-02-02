#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST MÓDULO - DOCUMENTOS TRIBUTARIOS
====================================
Pruebas del sistema de control de documentos.

COBERTURA:
- Gestión de timbrados
- Control de numeración de facturas
- Validez de documentos
- Alertas de vencimiento
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
# TEST 1: GESTIÓN DE TIMBRADOS
# ============================================================================

def test_gestion_timbrados():
    """Prueba la gestión de timbrados fiscales"""
    print_header("TEST 1: Gestión de Nro_Timbrados")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Crear nuevo timbrado
        timbrado = f"1234567890{datetime.now().strftime('%Y%m')}"
        tipo_doc = "Factura"
        numero_inicial = 1000
        numero_final = 2000
        fecha_emision = datetime.now().date()
        fecha_vencimiento = fecha_emision + timedelta(days=365)
        
        print_info(f"Nro_Timbrado: {timbrado}")
        print_info(f"Tipo: {tipo_doc}")
        print_info(f"Rango: {numero_inicial} - {numero_final}")
        
        cursor.execute("""
            INSERT INTO documentos_tributarios
            (Nro_Timbrado, Nro_Secuencial, Fecha_Emision, Monto_Total, 
             Monto_Neto, IVA_10, IVA_5, IVA_Exento)
            VALUES (%s, %s, NOW(), 0, 0, 0, 0, 0)
        """, (tipo_doc, timbrado, numero_inicial, numero_final, 
              numero_inicial, fecha_emision, fecha_vencimiento))
        
        id_documento = cursor.lastrowid
        
        print_success(f"\n✅ Nro_Timbrado creado exitosamente")
        print_info(f"   ID: {id_documento}")
        print_info(f"   Nro_Timbrado: {timbrado}")
        print_info(f"   Vigencia: {fecha_emision} a {fecha_vencimiento}")
        print_info(f"   Documentos disponibles: {numero_final - numero_inicial}")
        
        # Consultar todos los timbrados
        cursor.execute("""
            SELECT 
                ID_Documento,
                Nro_Timbrado,
                Nro_Secuencial,
                Fecha_Emision
            FROM documentos_tributarios
            ORDER BY Fecha_Emision DESC
            LIMIT 10
        """)
        
        timbrados = cursor.fetchall()
        
        print(f"\n   📋 Nro_Timbrados registrados ({len(timbrados)}):")
        print(f"   {'Tipo':<15} {'Nro_Timbrado':<15} {'Actual':<10} {'Final':<10} {'Vencimiento':<15} {'Estado':<10}")
        print(f"   {'-'*85}")
        
        for timb in timbrados:
            id_d, tipo, timb_num, actual, final, venc = timb
            estado = "Activo"
            venc_str = venc.strftime('%d/%m/%Y')
            
            print(f"   {tipo:<15} {timb_num:<15} {actual:<10} {final:<10} {venc_str:<15} {estado:<10}")
        
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
# TEST 2: CONTROL DE NUMERACIÓN
# ============================================================================

def test_control_numeracion():
    """Prueba el control de numeración consecutiva"""
    print_header("TEST 2: Control de Numeración")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar documento activo
        cursor.execute("""
            SELECT 
                ID_Documento,
                Nro_Timbrado,
                Nro_Secuencial,
                Fecha_Emision
            FROM documentos_tributarios
            WHERE Fecha_Emision > CURDATE()
            LIMIT 1
        """)
        
        documento = cursor.fetchone()
        
        if not documento:
            print_error("No hay documentos activos disponibles")
            return False
        
        id_doc, tipo, timbrado, actual, final = documento
        
        print_info(f"Documento: {tipo}")
        print_info(f"Nro_Timbrado: {timbrado}")
        print_info(f"Número actual: {actual}")
        print_info(f"Número final: {final}")
        
        disponibles = final - actual
        print_info(f"Disponibles: {disponibles} documentos")
        
        # Simular emisión de documentos
        print_info("\n   📄 Simulando emisión de 3 documentos...")
        
        for i in range(3):
            numero_emitido = actual + i
            
            if numero_emitido <= final:
                print_info(f"     Documento #{numero_emitido} emitido")
            else:
                print_error(f"     ❌ Documento #{numero_emitido} excede el rango")
                break
        
        # Actualizar número actual
        nuevo_actual = actual + 3
        
        if nuevo_actual <= final:
            cursor.execute("""
                UPDATE documentos_tributarios
                SET Nro_Secuencial = %s
                WHERE ID_Documento = %s
            """, (nuevo_actual, id_doc))
            
            print_success(f"\n   ✅ Numeración actualizada a {nuevo_actual}")
            
            nuevos_disponibles = final - nuevo_actual
            print_info(f"     Documentos restantes: {nuevos_disponibles}")
            
            # Verificar umbral de alerta (10% restante)
            umbral_alerta = (final - actual) * 0.1
            
            if nuevos_disponibles <= umbral_alerta:
                print_error(f"   ⚠️  ALERTA: Quedan menos del 10% de documentos")
        else:
            print_error(f"   ❌ No se puede actualizar: excedería el límite")
        
        # Validar numeración consecutiva en ventas
        cursor.execute("""
            SELECT 
                v.ID_Venta,
                dt.Nro_Secuencial,
                v.Fecha
            FROM ventas v
            INNER JOIN documentos_tributarios dt ON v.ID_Documento = dt.ID_Documento
            WHERE v.ID_Documento = %s
            ORDER BY v.Fecha DESC
            LIMIT 5
        """)
        
        ventas = cursor.fetchall()
        
        if ventas:
            print(f"\n   📊 Últimas emisiones:")
            for id_v, numero, fecha in ventas:
                print_info(f"     Venta #{id_v}: Documento #{numero} - {fecha.strftime('%d/%m/%Y')}")
        
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
# TEST 3: VALIDACIÓN DE DOCUMENTOS
# ============================================================================

def test_validacion_documentos():
    """Prueba la validación de vigencia de documentos"""
    print_header("TEST 3: Validación de Documentos")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Consultar todos los documentos con su estado
        cursor.execute("""
            SELECT 
                ID_Documento,
                Nro_Timbrado,
                Nro_Secuencial,
                Fecha_Emision
            FROM documentos_tributarios
            ORDER BY Fecha_Emision
        """)
        
        documentos = cursor.fetchall()
        
        # Clasificar documentos
        vigentes = []
        por_vencer = []
        vencidos = []
        agotados = []
        
        for doc in documentos:
            id_d, tipo, timb, emision, venc, actual, final, dias = doc
            
            if dias < 0:
                vencidos.append(doc)
            elif dias <= 30:
                por_vencer.append(doc)
            elif actual >= final:
                agotados.append(doc)
            else:
                vigentes.append(doc)
        
        print_success(f"✅ Análisis de {len(documentos)} documento(s)")
        
        # Documentos vigentes
        if vigentes:
            print(f"\n   ✅ Documentos vigentes: {len(vigentes)}")
            print(f"   {'Tipo':<15} {'Nro_Timbrado':<15} {'Vencimiento':<15} {'Disponibles':>12}")
            print(f"   {'-'*60}")
            
            for doc in vigentes[:5]:
                id_d, tipo, timb, emision, venc, actual, final, dias = doc
                disp = final - actual
                venc_str = venc.strftime('%d/%m/%Y')
                print(f"   {tipo:<15} {timb:<15} {venc_str:<15} {disp:>12}")
        
        # Documentos por vencer
        if por_vencer:
            print(f"\n   ⚠️  Documentos por vencer (30 días): {len(por_vencer)}")
            for doc in por_vencer:
                id_d, tipo, timb, emision, venc, actual, final, dias = doc
                print_info(f"     {tipo} - Nro_Timbrado {timb}: {dias} días restantes")
        
        # Documentos vencidos
        if vencidos:
            print(f"\n   ❌ Documentos vencidos: {len(vencidos)}")
            for doc in vencidos[:5]:
                id_d, tipo, timb, emision, venc, actual, final, dias = doc
                print_error(f"     {tipo} - Nro_Timbrado {timb}: Vencido hace {abs(dias)} días")
        
        # Documentos agotados
        if agotados:
            print(f"\n   📝 Documentos agotados: {len(agotados)}")
            for doc in agotados:
                id_d, tipo, timb, emision, venc, actual, final, dias = doc
                print_info(f"     {tipo} - Nro_Timbrado {timb}: Sin números disponibles")
        
        # Estadísticas generales
        print(f"\n   📈 Resumen:")
        print_info(f"     Total documentos: {len(documentos)}")
        print_info(f"     Vigentes: {len(vigentes)}")
        print_info(f"     Por vencer: {len(por_vencer)}")
        print_info(f"     Vencidos: {len(vencidos)}")
        print_info(f"     Agotados: {len(agotados)}")
        
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
# TEST 4: ALERTAS DE VENCIMIENTO
# ============================================================================

def test_alertas_vencimiento():
    """Prueba el sistema de alertas de vencimiento"""
    print_header("TEST 4: Alertas de Vencimiento")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Documentos que vencen en los próximos 60 días
        cursor.execute("""
            SELECT 
                ID_Documento,
                Nro_Timbrado,
                Nro_Secuencial,
                Fecha_Emision
            FROM documentos_tributarios
            WHERE Fecha_Emision BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 60 DAY)
            ORDER BY Fecha_Emision
        """)
        
        alertas_tiempo = cursor.fetchall()
        
        if alertas_tiempo:
            print(f"   ⚠️  {len(alertas_tiempo)} documento(s) próximo(s) a vencer:")
            print(f"   {'Tipo':<15} {'Nro_Timbrado':<15} {'Vencimiento':<15} {'Días':>8}")
            print(f"   {'-'*60}")
            
            for doc in alertas_tiempo:
                id_d, tipo, timb, venc, actual, final, dias = doc
                venc_str = venc.strftime('%d/%m/%Y')
                
                if dias <= 15:
                    urgencia = "🔴"
                elif dias <= 30:
                    urgencia = "🟠"
                else:
                    urgencia = "🟡"
                
                print(f"   {tipo:<15} {timb:<15} {venc_str:<15} {dias:>7}d {urgencia}")
        else:
            print_success("   ✅ No hay documentos próximos a vencer")
        
        # Documentos con numeración baja
        cursor.execute("""
            SELECT 
                ID_Documento,
                Nro_Timbrado,
                Nro_Secuencial,
                Fecha_Emision
            FROM documentos_tributarios
            WHERE Fecha_Emision > CURDATE()
            HAVING porcentaje_disponible < 20
            ORDER BY porcentaje_disponible
        """)
        
        alertas_numero = cursor.fetchall()
        
        if alertas_numero:
            print(f"\n   📉 {len(alertas_numero)} documento(s) con bajo stock:")
            print(f"   {'Tipo':<15} {'Nro_Timbrado':<15} {'Disponibles':>12} {'%':>8}")
            print(f"   {'-'*55}")
            
            for doc in alertas_numero:
                id_d, tipo, timb, actual, final, porcentaje = doc
                disponibles = final - actual
                print(f"   {tipo:<15} {timb:<15} {disponibles:>12} {float(porcentaje):>7.1f}%")
        else:
            print_success("\n   ✅ Todos los documentos tienen stock suficiente")
        
        # Generar recomendaciones
        print(f"\n   💡 Recomendaciones:")
        
        if alertas_tiempo:
            print_info(f"     • Gestionar {len(alertas_tiempo)} timbrado(s) nuevo(s)")
        
        if alertas_numero:
            print_info(f"     • Solicitar nuevos documentos para {len(alertas_numero)} tipo(s)")
        
        if not alertas_tiempo and not alertas_numero:
            print_success("     ✅ Sistema de documentos en óptimas condiciones")
        
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
# TEST 5: REPORTES DE USO
# ============================================================================

def test_reportes_uso():
    """Prueba los reportes de uso de documentos"""
    print_header("TEST 5: Reportes de Uso de Documentos")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Documentos más utilizados
        cursor.execute("""
            SELECT 
                dt.ID_Documento,
                dt.Nro_Timbrado,
                COUNT(v.ID_Venta) as cantidad_usada,
                dt.Nro_Secuencial - dt.Nro_Secuencial as capacidad_total,
                (COUNT(v.ID_Venta) / (dt.Nro_Secuencial - dt.Nro_Secuencial) * 100) as porcentaje_uso
            FROM documentos_tributarios dt
            LEFT JOIN ventas v ON dt.ID_Documento = v.ID_Documento
            GROUP BY dt.ID_Documento, dt.ID_Documento, dt.Nro_Timbrado, capacidad_total
            HAVING cantidad_usada > 0
            ORDER BY cantidad_usada DESC
            LIMIT 10
        """)
        
        uso_documentos = cursor.fetchall()
        
        print_success(f"✅ Reporte de uso generado")
        
        if uso_documentos:
            print(f"\n   📊 Documentos más utilizados:")
            print(f"   {'Tipo':<15} {'Nro_Timbrado':<15} {'Usados':>10} {'Capacidad':>10} {'Uso %':>10}")
            print(f"   {'-'*70}")
            
            for doc in uso_documentos:
                tipo, timb, usados, capacidad, porcentaje = doc
                print(f"   {tipo:<15} {timb:<15} {usados:>10} {capacidad:>10} {float(porcentaje):>9.1f}%")
        
        # Uso por tipo de documento
        cursor.execute("""
            SELECT 
                dt.ID_Documento,
                COUNT(DISTINCT dt.ID_Documento) as timbrados,
                COUNT(v.ID_Venta) as documentos_emitidos,
                SUM(v.Monto_Total) as monto_total
            FROM documentos_tributarios dt
            LEFT JOIN ventas v ON dt.ID_Documento = v.ID_Documento
            GROUP BY dt.ID_Documento
            ORDER BY documentos_emitidos DESC
        """)
        
        por_tipo = cursor.fetchall()
        
        if por_tipo:
            print(f"\n   📈 Uso por tipo de documento:")
            print(f"   {'Tipo':<20} {'Nro_Timbrados':>12} {'Emitidos':>12} {'Monto Total':>20}")
            print(f"   {'-'*70}")
            
            for tipo, timb, emitidos, monto in por_tipo:
                monto_val = float(monto or 0)
                print(f"   {tipo:<20} {timb:>12} {emitidos:>12} Gs. {monto_val:>15,.0f}")
        
        # Tendencia de uso mensual
        cursor.execute("""
            SELECT 
                DATE_FORMAT(v.Fecha, '%%Y-%%m') as mes,
                dt.ID_Documento,
                COUNT(*) as cantidad
            FROM ventas v
            INNER JOIN documentos_tributarios dt ON v.ID_Documento = dt.ID_Documento
            WHERE v.Fecha >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
            GROUP BY mes, dt.ID_Documento
            ORDER BY mes DESC, cantidad DESC
            LIMIT 15
        """)
        
        tendencia = cursor.fetchall()
        
        if tendencia:
            print(f"\n   📅 Tendencia de uso (últimos 3 meses):")
            print(f"   {'Mes':<10} {'Tipo':<20} {'Cantidad':>10}")
            print(f"   {'-'*45}")
            
            for mes, tipo, cant in tendencia:
                print(f"   {mes:<10} {tipo:<20} {cant:>10}")
        
        # Proyección de agotamiento
        cursor.execute("""
            SELECT 
                dt.ID_Documento,
                dt.Nro_Timbrado,
                dt.Nro_Secuencial - dt.Nro_Secuencial as disponibles,
                COUNT(v.ID_Venta) / DATEDIFF(CURDATE(), dt.Fecha_Emision) as promedio_diario
            FROM documentos_tributarios dt
            LEFT JOIN ventas v ON dt.ID_Documento = v.ID_Documento
            WHERE dt.Fecha_Emision > CURDATE()
            AND dt.Fecha_Emision < CURDATE()
            GROUP BY dt.ID_Documento, dt.ID_Documento, dt.Nro_Timbrado, disponibles
            HAVING promedio_diario > 0
        """)
        
        proyeccion = cursor.fetchall()
        
        if proyeccion:
            print(f"\n   🔮 Proyección de agotamiento:")
            print(f"   {'Tipo':<20} {'Disponibles':>12} {'Promedio/día':>15} {'Días rest.':>12}")
            print(f"   {'-'*65}")
            
            for tipo, timb, disp, promedio in proyeccion:
                if promedio > 0:
                    dias_restantes = int(disp / promedio)
                    print(f"   {tipo:<20} {disp:>12} {promedio:>14.1f} {dias_restantes:>12}")
        
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
    print("█            TEST COMPLETO - DOCUMENTOS TRIBUTARIOS                  █")
    print("█                                                                    █")
    print("█" * 70)
    
    tests = [
        ("Gestión de Nro_Timbrados", test_gestion_timbrados),
        ("Control de Numeración", test_control_numeracion),
        ("Validación de Documentos", test_validacion_documentos),
        ("Alertas de Vencimiento", test_alertas_vencimiento),
        ("Reportes de Uso", test_reportes_uso),
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
        print("\n🎉 ¡PERFECTO! Todos los tests de documentos tributarios pasaron.")
    else:
        print(f"\n⚠️  {total - exitosos} test(s) fallaron.")
    
    print("\n")

if __name__ == "__main__":
    main()
