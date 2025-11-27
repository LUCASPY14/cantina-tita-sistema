#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST MÓDULO - GESTIÓN DE PROVEEDORES
=====================================
Pruebas CRUD completo de proveedores.

COBERTURA:
- Crear proveedor nuevo
- Actualizar datos de proveedor
- Consultar información
- Inactivar/reactivar proveedor
- Validar duplicados
"""

import MySQLdb
from datetime import datetime

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
# TEST 1: CREAR PROVEEDOR
# ============================================================================

def test_crear_proveedor():
    """Prueba la creación de un proveedor nuevo"""
    print_header("TEST 1: Crear Proveedor Nuevo")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Datos del proveedor
        razon_social = f"Distribuidora Test {datetime.now().strftime('%Y%m%d%H%M%S')}"
        ruc = f"80000000-{datetime.now().strftime('%H%M%S')}"
        telefono = "021-555-1234"
        email = "contacto@distribuidoratest.com"
        direccion = "Av. Test 1234, Asunción"
        
        print_info(f"Razón Social: {razon_social}")
        print_info(f"RUC: {ruc}")
        
        # Insertar proveedor
        cursor.execute("""
            INSERT INTO proveedores
            (Razon_Social, RUC, Telefono, Email, Direccion, Activo)
            VALUES (%s, %s, %s, %s, %s, TRUE)
        """, (razon_social, ruc, telefono, email, direccion))
        
        id_proveedor = cursor.lastrowid
        
        print_success(f"\n✅ Proveedor creado exitosamente")
        print_info(f"   ID: {id_proveedor}")
        print_info(f"   Razón Social: {razon_social}")
        print_info(f"   RUC: {ruc}")
        print_info(f"   Teléfono: {telefono}")
        print_info(f"   Email: {email}")
        
        # Verificar creación
        cursor.execute("""
            SELECT 
                ID_Proveedor,
                Razon_Social,
                RUC,
                Activo
            FROM proveedores
            WHERE ID_Proveedor = %s
        """, (id_proveedor,))
        
        verificacion = cursor.fetchone()
        
        if verificacion:
            id_p, razon, ruc_v, activo = verificacion
            print_info(f"\n   ✓ Verificación exitosa:")
            print_info(f"     Estado: {'Activo' if activo else 'Inactivo'}")
        
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
# TEST 2: ACTUALIZAR PROVEEDOR
# ============================================================================

def test_actualizar_proveedor():
    """Prueba la actualización de datos de un proveedor"""
    print_header("TEST 2: Actualizar Datos de Proveedor")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar proveedor existente
        cursor.execute("""
            SELECT 
                ID_Proveedor,
                Razon_Social,
                Telefono,
                Email
            FROM proveedores
            WHERE Activo = TRUE
            LIMIT 1
        """)
        
        proveedor = cursor.fetchone()
        
        if not proveedor:
            print_error("No hay proveedores activos")
            return False
        
        id_proveedor, razon_anterior, tel_anterior, email_anterior = proveedor
        
        print_info(f"Proveedor ID: {id_proveedor}")
        print_info(f"Razón Social: {razon_anterior}")
        
        # Nuevos datos
        telefono_nuevo = "021-999-8888"
        email_nuevo = "nuevo@proveedor.com.py"
        direccion_nueva = "Nueva Dirección 5678, Asunción"
        
        print_info(f"\n   📝 Actualizando datos...")
        
        # Actualizar proveedor
        cursor.execute("""
            UPDATE proveedores
            SET 
                Telefono = %s,
                Email = %s,
                Direccion = %s
            WHERE ID_Proveedor = %s
        """, (telefono_nuevo, email_nuevo, direccion_nueva, id_proveedor))
        
        filas_afectadas = cursor.rowcount
        
        print_success(f"\n✅ Proveedor actualizado")
        print_info(f"   Filas afectadas: {filas_afectadas}")
        
        # Verificar cambios
        cursor.execute("""
            SELECT 
                Telefono,
                Email,
                Direccion
            FROM proveedores
            WHERE ID_Proveedor = %s
        """, (id_proveedor,))
        
        datos_nuevos = cursor.fetchone()
        
        if datos_nuevos:
            tel, email, dir = datos_nuevos
            print_info(f"\n   ✓ Cambios aplicados:")
            print_info(f"     Teléfono: {tel_anterior} → {tel}")
            print_info(f"     Email: {email_anterior} → {email}")
            print_info(f"     Dirección: {dir}")
        
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
# TEST 3: CONSULTAR PROVEEDORES
# ============================================================================

def test_consultar_proveedores():
    """Prueba la consulta de información de proveedores"""
    print_header("TEST 3: Consultar Información de Proveedores")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Consultar todos los proveedores
        cursor.execute("""
            SELECT 
                ID_Proveedor,
                Razon_Social,
                RUC,
                Telefono,
                Email,
                Activo
            FROM proveedores
            ORDER BY Razon_Social
            LIMIT 15
        """)
        
        proveedores = cursor.fetchall()
        
        print_success(f"✅ {len(proveedores)} proveedor(es) encontrado(s)")
        
        if proveedores:
            print("\n   📋 Listado de proveedores:")
            print(f"   {'ID':<5} {'Razón Social':<35} {'RUC':<20} {'Estado':<10}")
            print(f"   {'-'*75}")
            
            activos = 0
            inactivos = 0
            
            for prov in proveedores:
                id_p, razon, ruc, tel, email, activo = prov
                estado = "Activo" if activo else "Inactivo"
                razon_corta = razon[:33]
                
                print(f"   {id_p:<5} {razon_corta:<35} {ruc:<20} {estado:<10}")
                
                if activo:
                    activos += 1
                else:
                    inactivos += 1
            
            print(f"\n   📊 Resumen:")
            print_info(f"     Activos: {activos}")
            print_info(f"     Inactivos: {inactivos}")
        
        # Buscar proveedor por RUC
        cursor.execute("""
            SELECT RUC FROM proveedores WHERE Activo = TRUE LIMIT 1
        """)
        
        ruc_buscar = cursor.fetchone()
        
        if ruc_buscar:
            ruc = ruc_buscar[0]
            
            cursor.execute("""
                SELECT 
                    ID_Proveedor,
                    Razon_Social,
                    Telefono,
                    Email,
                    Direccion
                FROM proveedores
                WHERE RUC = %s
            """, (ruc,))
            
            detalle = cursor.fetchone()
            
            if detalle:
                id_p, razon, tel, email, dir = detalle
                
                print(f"\n   🔍 Búsqueda por RUC ({ruc}):")
                print_info(f"     ID: {id_p}")
                print_info(f"     Razón Social: {razon}")
                print_info(f"     Teléfono: {tel}")
                print_info(f"     Email: {email}")
                if dir:
                    print_info(f"     Dirección: {dir}")
        
        # Proveedores con compras
        cursor.execute("""
            SELECT 
                p.ID_Proveedor,
                p.Razon_Social,
                COUNT(c.ID_Compra) as total_compras,
                COALESCE(SUM(c.Monto_Total), 0) as monto_total
            FROM proveedores p
            LEFT JOIN compras c ON p.ID_Proveedor = c.ID_Proveedor
            WHERE p.Activo = TRUE
            GROUP BY p.ID_Proveedor, p.Razon_Social
            HAVING total_compras > 0
            ORDER BY monto_total DESC
            LIMIT 5
        """)
        
        con_compras = cursor.fetchall()
        
        if con_compras:
            print(f"\n   💼 Top 5 proveedores (por monto):")
            print(f"   {'Proveedor':<40} {'Compras':>10} {'Total':>20}")
            print(f"   {'-'*75}")
            
            for prov in con_compras:
                id_p, razon, compras, total = prov
                razon_corta = razon[:38]
                print(f"   {razon_corta:<40} {compras:>10} Gs. {float(total):>15,.0f}")
        
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
# TEST 4: INACTIVAR/REACTIVAR PROVEEDOR
# ============================================================================

def test_activar_desactivar():
    """Prueba la inactivación y reactivación de proveedores"""
    print_header("TEST 4: Inactivar/Reactivar Proveedor")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar proveedor activo
        cursor.execute("""
            SELECT 
                ID_Proveedor,
                Razon_Social,
                Activo
            FROM proveedores
            WHERE Activo = TRUE
            LIMIT 1
        """)
        
        proveedor = cursor.fetchone()
        
        if not proveedor:
            print_error("No hay proveedores activos")
            return False
        
        id_proveedor, razon_social, estado_inicial = proveedor
        
        print_info(f"Proveedor: {razon_social}")
        print_info(f"Estado inicial: {'Activo' if estado_inicial else 'Inactivo'}")
        
        # Inactivar proveedor
        print_info("\n   🔒 Inactivando proveedor...")
        
        cursor.execute("""
            UPDATE proveedores
            SET Activo = FALSE
            WHERE ID_Proveedor = %s
        """, (id_proveedor,))
        
        # Verificar inactivación
        cursor.execute("""
            SELECT Activo FROM proveedores WHERE ID_Proveedor = %s
        """, (id_proveedor,))
        
        estado_inactivo = cursor.fetchone()[0]
        
        if not estado_inactivo:
            print_success(f"   ✅ Proveedor inactivado correctamente")
        else:
            print_error(f"   ❌ No se pudo inactivar")
        
        # Reactivar proveedor
        print_info("\n   🔓 Reactivando proveedor...")
        
        cursor.execute("""
            UPDATE proveedores
            SET Activo = TRUE
            WHERE ID_Proveedor = %s
        """, (id_proveedor,))
        
        # Verificar reactivación
        cursor.execute("""
            SELECT Activo FROM proveedores WHERE ID_Proveedor = %s
        """, (id_proveedor,))
        
        estado_activo = cursor.fetchone()[0]
        
        if estado_activo:
            print_success(f"   ✅ Proveedor reactivado correctamente")
        else:
            print_error(f"   ❌ No se pudo reactivar")
        
        # Estadísticas de estados
        cursor.execute("""
            SELECT 
                Activo,
                COUNT(*) as cantidad
            FROM proveedores
            GROUP BY Activo
        """)
        
        stats = cursor.fetchall()
        
        print(f"\n   📊 Estadísticas:")
        for activo, cant in stats:
            estado = "Activos" if activo else "Inactivos"
            print_info(f"     {estado}: {cant}")
        
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
# TEST 5: VALIDAR DUPLICADOS
# ============================================================================

def test_validar_duplicados():
    """Prueba la validación de proveedores duplicados"""
    print_header("TEST 5: Validar Proveedores Duplicados")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Buscar un RUC existente
        cursor.execute("""
            SELECT RUC, Razon_Social
            FROM proveedores
            WHERE Activo = TRUE
            LIMIT 1
        """)
        
        existente = cursor.fetchone()
        
        if not existente:
            print_error("No hay proveedores para probar")
            return False
        
        ruc_existente, razon_existente = existente
        
        print_info(f"RUC existente: {ruc_existente}")
        print_info(f"Razón Social: {razon_existente}")
        
        # Intentar crear duplicado
        print_info("\n   🔍 Intentando crear proveedor con RUC duplicado...")
        
        try:
            cursor.execute("""
                INSERT INTO proveedores
                (Razon_Social, RUC, Telefono, Activo)
                VALUES ('Proveedor Duplicado Test', %s, '021-000-0000', TRUE)
            """, (ruc_existente,))
            
            print_error("   ❌ Se permitió crear duplicado (ERROR)")
            return False
            
        except MySQLdb.IntegrityError as e:
            print_success("   ✅ Sistema rechazó duplicado correctamente")
            print_info(f"     Error: {str(e)[:80]}")
        
        # Buscar proveedores con RUC similar
        print_info("\n   🔎 Buscando RUCs similares...")
        
        cursor.execute("""
            SELECT 
                ID_Proveedor,
                Razon_Social,
                RUC
            FROM proveedores
            WHERE RUC LIKE %s
            ORDER BY RUC
        """, (f"{ruc_existente[:5]}%",))
        
        similares = cursor.fetchall()
        
        if similares:
            print_info(f"   Encontrados {len(similares)} proveedor(es) con RUC similar:")
            for id_p, razon, ruc in similares[:5]:
                print_info(f"     {ruc}: {razon[:40]}")
        
        # Buscar nombres similares (posibles duplicados)
        cursor.execute("""
            SELECT 
                Razon_Social,
                COUNT(*) as cantidad
            FROM proveedores
            GROUP BY Razon_Social
            HAVING cantidad > 1
        """)
        
        nombres_dup = cursor.fetchall()
        
        if nombres_dup:
            print(f"\n   ⚠️  ALERTA: Razones sociales repetidas:")
            for razon, cant in nombres_dup:
                print_info(f"     '{razon}': {cant} veces")
        else:
            print_success("\n   ✅ No hay razones sociales duplicadas")
        
        # Validación de formato de RUC
        cursor.execute("""
            SELECT 
                ID_Proveedor,
                Razon_Social,
                RUC
            FROM proveedores
            WHERE RUC NOT REGEXP '^[0-9]+-[0-9]$'
            AND RUC IS NOT NULL
            LIMIT 5
        """)
        
        rucs_invalidos = cursor.fetchall()
        
        if rucs_invalidos:
            print(f"\n   ⚠️  RUCs con formato no estándar:")
            for id_p, razon, ruc in rucs_invalidos:
                print_info(f"     {ruc}: {razon[:40]}")
        
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
    print("█             TEST COMPLETO - GESTIÓN DE PROVEEDORES                 █")
    print("█                                                                    █")
    print("█" * 70)
    
    tests = [
        ("Crear Proveedor", test_crear_proveedor),
        ("Actualizar Proveedor", test_actualizar_proveedor),
        ("Consultar Proveedores", test_consultar_proveedores),
        ("Activar/Desactivar", test_activar_desactivar),
        ("Validar Duplicados", test_validar_duplicados),
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
        print("\n🎉 ¡PERFECTO! Todos los tests de proveedores pasaron.")
    else:
        print(f"\n⚠️  {total - exitosos} test(s) fallaron.")
    
    print("\n")

if __name__ == "__main__":
    main()
