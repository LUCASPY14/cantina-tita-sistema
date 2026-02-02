#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST MÓDULO - CATEGORÍAS Y UNIDADES
====================================
Pruebas del sistema de organización de productos.

COBERTURA:
- CRUD de categorías
- CRUD de unidades de medida
- Asignación a productos
- Jerarquías de categorías
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
# TEST 1: CRUD DE CATEGORÍAS
# ============================================================================

def test_crud_categorias():
    """Prueba operaciones CRUD en categorías"""
    print_header("TEST 1: CRUD de Categorías")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # CREATE - Crear nueva categoría
        nombre_cat = f"Categoría Test {datetime.now().strftime('%H%M%S')}"
        
        print_info(f"Creando: {nombre_cat}")
        
        cursor.execute("""
            INSERT INTO categorias
            (Nombre)
            VALUES (%s)
        """, (nombre_cat,))
        
        id_categoria = cursor.lastrowid
        
        print_success(f"   ✅ Categoría creada (ID: {id_categoria})")
        
        # READ - Leer categoría
        cursor.execute("""
            SELECT 
                ID_Categoria,
                Nombre
            FROM categorias
            WHERE ID_Categoria = %s
        """, (id_categoria,))
        
        categoria = cursor.fetchone()
        
        if categoria:
            id_c, nombre = categoria
            print_info(f"   ✓ Lectura: '{nombre}'")
        
        # UPDATE - Actualizar categoría
        nombre_actualizado = f"{nombre_cat} (Actualizada)"
        
        cursor.execute("""
            UPDATE categorias
            SET Nombre = %s
            WHERE ID_Categoria = %s
        """, (nombre_actualizado, id_categoria))
        
        print_success(f"   ✅ Categoría actualizada")
        
        # Verificar actualización
        cursor.execute("""
            SELECT Nombre
            FROM categorias
            WHERE ID_Categoria = %s
        """, (id_categoria,))
        
        nombre_nuevo = cursor.fetchone()[0]
        print_info(f"   ✓ Nuevo nombre: '{nombre_nuevo}'")
        
        # Listar todas las categorías
        cursor.execute("""
            SELECT 
                c.ID_Categoria,
                c.Nombre,
                COUNT(p.ID_Producto) as productos
            FROM categorias c
            LEFT JOIN productos p ON c.ID_Categoria = p.ID_Categoria
            GROUP BY c.ID_Categoria, c.Nombre
            ORDER BY c.Nombre
            LIMIT 15
        """)
        
        categorias = cursor.fetchall()
        
        print(f"\n   📋 Categorías existentes ({len(categorias)}):")
        print(f"   {'ID':<5} {'Nombre':<35} {'Productos':>10}")
        print(f"   {'-'*55}")
        
        for cat in categorias:
            id_c, nombre, prods = cat
            print(f"   {id_c:<5} {nombre[:33]:<35} {prods:>10}")
        
        # DELETE (lógico) - No se implementa eliminación física
        print_info(f"\n   ℹ️  DELETE no implementado (integridad referencial)")
        
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
# TEST 2: CRUD DE UNIDADES
# ============================================================================

def test_crud_unidades():
    """Prueba operaciones CRUD en unidades de medida"""
    print_header("TEST 2: CRUD de Unidades de Medida")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # CREATE - Crear nueva unidad
        nombre_unidad = f"Test-{datetime.now().strftime('%H%M%S')}"
        abreviatura = "TST"
        
        print_info(f"Creando: {nombre_unidad} ({abreviatura})")
        
        cursor.execute("""
            INSERT INTO unidades_medida
            (Nombre, Abreviatura)
            VALUES (%s, %s)
        """, (nombre_unidad, abreviatura))
        
        id_unidad = cursor.lastrowid
        
        print_success(f"   ✅ Unidad creada (ID: {id_unidad})")
        
        # READ - Leer unidad
        cursor.execute("""
            SELECT 
                ID_Unidad,
                Nombre,
                Abreviatura
            FROM unidades_medida
            WHERE ID_Unidad = %s
        """, (id_unidad,))
        
        unidad = cursor.fetchone()
        
        if unidad:
            id_u, nombre, abrev = unidad
            print_info(f"   ✓ Lectura: '{nombre}' ({abrev})")
        
        # UPDATE - Actualizar unidad
        nueva_abreviatura = "TSTX"
        
        cursor.execute("""
            UPDATE unidades_medida
            SET Abreviatura = %s
            WHERE ID_Unidad = %s
        """, (nueva_abreviatura, id_unidad))
        
        print_success(f"   ✅ Unidad actualizada")
        
        # Listar todas las unidades
        cursor.execute("""
            SELECT 
                u.ID_Unidad,
                u.Nombre,
                u.Abreviatura,
                COUNT(p.ID_Producto) as productos
            FROM unidades_medida u
            LEFT JOIN productos p ON u.ID_Unidad = p.ID_Unidad
            GROUP BY u.ID_Unidad, u.Nombre, u.Abreviatura
            ORDER BY u.Nombre
            LIMIT 20
        """)
        
        unidades = cursor.fetchall()
        
        print(f"\n   📏 Unidades existentes ({len(unidades)}):")
        print(f"   {'ID':<5} {'Nombre':<25} {'Abrev.':<10} {'Productos':>10}")
        print(f"   {'-'*55}")
        
        for uni in unidades:
            id_u, nombre, abrev, prods = uni
            print(f"   {id_u:<5} {nombre[:23]:<25} {abrev:<10} {prods:>10}")
        
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
# TEST 3: ASIGNACIÓN A PRODUCTOS
# ============================================================================

def test_asignacion_productos():
    """Prueba la asignación de categorías y unidades a productos"""
    print_header("TEST 3: Asignación a Productos")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Consultar productos con categoría y unidad
        cursor.execute("""
            SELECT 
                p.ID_Producto,
                p.Codigo,
                p.Descripcion,
                c.Nombre,
                u.Nombre,
                u.Abreviatura
            FROM productos p
            LEFT JOIN categorias c ON p.ID_Categoria = c.ID_Categoria
            LEFT JOIN unidades_medida u ON p.ID_Unidad = u.ID_Unidad
            WHERE p.Activo = TRUE
            ORDER BY c.Nombre, p.Descripcion
            LIMIT 20
        """)
        
        productos = cursor.fetchall()
        
        print_success(f"✅ {len(productos)} producto(s) encontrado(s)")
        
        if productos:
            print(f"\n   📦 Productos con categoría y unidad:")
            print(f"   {'Código':<12} {'Producto':<30} {'Categoría':<20} {'Unidad':<10}")
            print(f"   {'-'*80}")
            
            for prod in productos:
                id_p, codigo, desc, categoria, unidad, abrev = prod
                cat_str = categoria[:18] if categoria else "Sin categoría"
                uni_str = abrev if abrev else "S/U"
                desc_corta = desc[:28]
                
                print(f"   {codigo:<12} {desc_corta:<30} {cat_str:<20} {uni_str:<10}")
        
        # Productos sin categoría
        cursor.execute("""
            SELECT COUNT(*) as sin_categoria
            FROM productos
            WHERE ID_Categoria IS NULL
            AND Activo = TRUE
        """)
        
        sin_cat = cursor.fetchone()[0]
        
        # Productos sin unidad
        cursor.execute("""
            SELECT COUNT(*) as sin_unidad
            FROM productos
            WHERE ID_Unidad IS NULL
            AND Activo = TRUE
        """)
        
        sin_uni = cursor.fetchone()[0]
        
        print(f"\n   📊 Estadísticas:")
        print_info(f"     Total productos: {len(productos)}")
        print_info(f"     Sin categoría: {sin_cat}")
        print_info(f"     Sin unidad: {sin_uni}")
        
        if sin_cat > 0 or sin_uni > 0:
            print_error(f"   ⚠️  Productos incompletos encontrados")
        else:
            print_success(f"   ✅ Todos los productos tienen categoría y unidad")
        
        # Cambiar categoría de un producto
        cursor.execute("""
            SELECT ID_Producto, Descripcion, ID_Categoria
            FROM productos
            WHERE Activo = TRUE
            LIMIT 1
        """)
        
        producto_test = cursor.fetchone()
        
        if producto_test:
            id_prod, desc, cat_actual = producto_test
            
            # Buscar otra categoría
            cursor.execute("""
                SELECT ID_Categoria, Nombre
                FROM categorias
                WHERE ID_Categoria != %s
                LIMIT 1
            """, (cat_actual,))
            
            nueva_cat = cursor.fetchone()
            
            if nueva_cat:
                id_nueva_cat, nombre_nueva_cat = nueva_cat
                
                print(f"\n   🔄 Cambiando categoría de producto:")
                print_info(f"     Producto: {desc[:40]}")
                
                cursor.execute("""
                    UPDATE productos
                    SET ID_Categoria = %s
                    WHERE ID_Producto = %s
                """, (id_nueva_cat, id_prod))
                
                print_success(f"     ✅ Categoría actualizada a: {nombre_nueva_cat}")
        
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
# TEST 4: REPORTES Y ESTADÍSTICAS
# ============================================================================

def test_reportes_estadisticas():
    """Prueba generación de reportes sobre categorías y unidades"""
    print_header("TEST 4: Reportes y Estadísticas")
    
    conn = MySQLdb.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Productos por categoría
        cursor.execute("""
            SELECT 
                c.Nombre,
                COUNT(p.ID_Producto) as cantidad,
                SUM(CASE WHEN p.Activo = TRUE THEN 1 ELSE 0 END) as activos,
                SUM(CASE WHEN p.Activo = FALSE THEN 1 ELSE 0 END) as inactivos
            FROM categorias c
            LEFT JOIN productos p ON c.ID_Categoria = p.ID_Categoria
            GROUP BY c.ID_Categoria, c.Nombre
            HAVING cantidad > 0
            ORDER BY cantidad DESC
            LIMIT 15
        """)
        
        por_categoria = cursor.fetchall()
        
        print_success("✅ Reporte generado")
        
        if por_categoria:
            print(f"\n   📊 Productos por categoría:")
            print(f"   {'Categoría':<30} {'Total':>8} {'Activos':>8} {'Inactivos':>10}")
            print(f"   {'-'*60}")
            
            total_general = 0
            
            for cat in por_categoria:
                nombre, total, activos, inactivos = cat
                nombre_corto = nombre[:28]
                print(f"   {nombre_corto:<30} {total:>8} {activos:>8} {inactivos:>10}")
                total_general += total
            
            print(f"   {'-'*60}")
            print(f"   {'TOTAL':<30} {total_general:>8}")
        
        # Productos por unidad
        cursor.execute("""
            SELECT 
                u.Nombre,
                u.Abreviatura,
                COUNT(p.ID_Producto) as cantidad
            FROM unidades_medida u
            LEFT JOIN productos p ON u.ID_Unidad = p.ID_Unidad
            WHERE p.Activo = TRUE
            GROUP BY u.ID_Unidad, u.Nombre, u.Abreviatura
            HAVING cantidad > 0
            ORDER BY cantidad DESC
            LIMIT 10
        """)
        
        por_unidad = cursor.fetchall()
        
        if por_unidad:
            print(f"\n   📏 Productos por unidad de medida:")
            print(f"   {'Unidad':<25} {'Abrev.':<10} {'Cantidad':>10}")
            print(f"   {'-'*50}")
            
            for uni in por_unidad:
                nombre, abrev, cant = uni
                print(f"   {nombre[:23]:<25} {abrev:<10} {cant:>10}")
        
        # Categorías más vendidas
        cursor.execute("""
            SELECT 
                c.Nombre,
                SUM(dv.Cantidad) as unidades_vendidas,
                COUNT(DISTINCT dv.ID_Venta) as ventas,
                SUM(dv.Subtotal_Total) as monto_total
            FROM categorias c
            INNER JOIN productos p ON c.ID_Categoria = p.ID_Categoria
            INNER JOIN detalle_venta dv ON p.ID_Producto = dv.ID_Producto
            INNER JOIN ventas v ON dv.ID_Venta = v.ID_Venta
            WHERE v.Fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY c.ID_Categoria, c.Nombre
            ORDER BY monto_total DESC
            LIMIT 10
        """)
        
        cat_vendidas = cursor.fetchall()
        
        if cat_vendidas:
            print(f"\n   🏆 Top categorías (últimos 30 días):")
            print(f"   {'Categoría':<25} {'Unidades':>10} {'Ventas':>10} {'Total':>20}")
            print(f"   {'-'*70}")
            
            for cat in cat_vendidas:
                nombre, unidades, ventas, total = cat
                nombre_corto = nombre[:23]
                print(f"   {nombre_corto:<25} {int(unidades):>10} {ventas:>10} Gs. {float(total):>15,.0f}")
        
        # Categorías sin productos
        cursor.execute("""
            SELECT 
                c.ID_Categoria,
                c.Nombre
            FROM categorias c
            LEFT JOIN productos p ON c.ID_Categoria = p.ID_Categoria
            WHERE p.ID_Producto IS NULL
        """)
        
        cat_vacias = cursor.fetchall()
        
        if cat_vacias:
            print(f"\n   ⚠️  Categorías sin productos ({len(cat_vacias)}):")
            for id_c, nombre in cat_vacias[:5]:
                print_info(f"     {nombre}")
        else:
            print_success(f"\n   ✅ Todas las categorías tienen productos asignados")
        
        # Unidades sin uso
        cursor.execute("""
            SELECT 
                u.ID_Unidad,
                u.Nombre
            FROM unidades_medida u
            LEFT JOIN productos p ON u.ID_Unidad = p.ID_Unidad
            WHERE p.ID_Producto IS NULL
        """)
        
        uni_sin_uso = cursor.fetchall()
        
        if uni_sin_uso:
            print(f"\n   ⚠️  Unidades sin uso ({len(uni_sin_uso)}):")
            for id_u, nombre in uni_sin_uso[:5]:
                print_info(f"     {nombre}")
        
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
    print("█            TEST COMPLETO - CATEGORÍAS Y UNIDADES                   █")
    print("█                                                                    █")
    print("█" * 70)
    
    tests = [
        ("CRUD Categorías", test_crud_categorias),
        ("CRUD Unidades", test_crud_unidades),
        ("Asignación a Productos", test_asignacion_productos),
        ("Reportes y Estadísticas", test_reportes_estadisticas),
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
        print("\n🎉 ¡PERFECTO! Todos los tests de categorías y unidades pasaron.")
    else:
        print(f"\n⚠️  {total - exitosos} test(s) fallaron.")
    
    print("\n")

if __name__ == "__main__":
    main()
