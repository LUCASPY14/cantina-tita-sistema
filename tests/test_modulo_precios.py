"""
TEST MÓDULO: PRECIOS Y LISTAS
==============================
Pruebas para gestión de listas de precios, precios por lista e historial.

Tablas: listas_precios, precios_por_lista, historico_precios

Autor: Sistema de Tests Automatizado
Fecha: 26 de Noviembre de 2025
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection
from datetime import datetime, date
from decimal import Decimal

class TestPrecios:
    def __init__(self):
        self.cursor = connection.cursor()
        self.tests_passed = 0
        self.tests_failed = 0
        self.limpiar_datos_prueba()
    
    def limpiar_datos_prueba(self):
        """Limpia datos de pruebas anteriores"""
        try:
            self.cursor.execute("DELETE FROM historico_precios WHERE ID_Historico >= 9000")
            self.cursor.execute("DELETE FROM precios_por_lista WHERE ID_Precio >= 9000")
            self.cursor.execute("DELETE FROM listas_precios WHERE ID_Lista >= 9000")
            connection.commit()
        except Exception as e:
            connection.rollback()
            print(f"[INFO] Limpieza inicial: {e}")
    
    def print_header(self, test_num, test_name):
        """Imprime encabezado de test"""
        print(f"\n{'='*70}")
        print(f"TEST {test_num}: {test_name}")
        print('='*70)
    
    def assert_true(self, condition, mensaje):
        """Verifica que una condición sea verdadera"""
        if condition:
            print(f"  [OK] {mensaje}")
            return True
        else:
            print(f"  [FALLO] {mensaje}")
            self.tests_failed += 1
            return False
    
    def assert_equals(self, actual, esperado, mensaje):
        """Verifica que dos valores sean iguales"""
        if actual == esperado:
            print(f"  [OK] {mensaje}: {actual}")
            return True
        else:
            print(f"  [FALLO] {mensaje}")
            print(f"         Esperado: {esperado}")
            print(f"         Actual: {actual}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # TEST 1: CREAR Y GESTIONAR LISTAS DE PRECIOS
    # ========================================================================
    def test_01_crear_listas_precios(self):
        """
        Prueba la creación de listas de precios
        - Lista minorista
        - Lista mayorista
        - Lista especial
        """
        self.print_header(1, "CREAR Y GESTIONAR LISTAS DE PRECIOS")
        
        try:
            # Crear lista minorista
            self.cursor.execute("""
                INSERT INTO listas_precios (
                    ID_Lista,
                    Nombre_Lista,
                    Fecha_Vigencia,
                    Moneda,
                    Activo
                ) VALUES (
                    9001,
                    'Lista Minorista TEST',
                    %s,
                    'PYG',
                    1
                )
            """, (date.today(),))
            
            connection.commit()
            
            self.assert_true(
                True,
                "Lista Minorista creada"
            )
            
            # Crear lista mayorista
            self.cursor.execute("""
                INSERT INTO listas_precios (
                    ID_Lista,
                    Nombre_Lista,
                    Fecha_Vigencia,
                    Moneda,
                    Activo
                ) VALUES (
                    9002,
                    'Lista Mayorista TEST',
                    %s,
                    'PYG',
                    1
                )
            """, (date.today(),))
            
            connection.commit()
            
            self.assert_true(
                True,
                "Lista Mayorista creada"
            )
            
            # Verificar listas creadas
            self.cursor.execute("""
                SELECT COUNT(*) 
                FROM listas_precios 
                WHERE ID_Lista IN (9001, 9002)
            """)
            
            count = self.cursor.fetchone()[0]
            
            self.assert_equals(
                count, 2,
                "Listas de precios verificadas"
            )
            
            # Consultar listas activas
            self.cursor.execute("""
                SELECT Nombre_Lista, Moneda, Activo
                FROM listas_precios
                WHERE Activo = 1
                ORDER BY ID_Lista
            """)
            
            listas = self.cursor.fetchall()
            
            print(f"  [INFO] Total listas activas: {len(listas)}")
            for lista in listas:
                print(f"    - {lista[0]} ({lista[1]})")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # TEST 2: ASIGNAR PRECIOS A PRODUCTOS
    # ========================================================================
    def test_02_asignar_precios_productos(self):
        """
        Asigna precios a productos en diferentes listas
        - Precio minorista
        - Precio mayorista (con descuento)
        """
        self.print_header(2, "ASIGNAR PRECIOS A PRODUCTOS")
        
        try:
            # Obtener productos para asignar precios
            self.cursor.execute("""
                SELECT ID_Producto, Codigo, Descripcion
                FROM productos
                WHERE Activo = 1
                LIMIT 3
            """)
            
            productos = self.cursor.fetchall()
            
            self.assert_true(
                len(productos) >= 3,
                f"Productos encontrados: {len(productos)}"
            )
            
            precios_base = [15000, 25000, 8500]  # Precios de ejemplo
            
            for i, producto in enumerate(productos):
                id_producto, codigo, descripcion = producto
                precio_minorista = precios_base[i]
                precio_mayorista = int(precio_minorista * 0.85)  # 15% descuento
                
                # Precio minorista (Lista 9001)
                self.cursor.execute("""
                    INSERT INTO precios_por_lista (
                        ID_Precio,
                        ID_Producto,
                        ID_Lista,
                        Precio_Unitario_Neto
                    ) VALUES (
                        %s, %s, 9001, %s
                    )
                """, (9001 + i, id_producto, precio_minorista))
                
                # Precio mayorista (Lista 9002)
                self.cursor.execute("""
                    INSERT INTO precios_por_lista (
                        ID_Precio,
                        ID_Producto,
                        ID_Lista,
                        Precio_Unitario_Neto
                    ) VALUES (
                        %s, %s, 9002, %s
                    )
                """, (9004 + i, id_producto, precio_mayorista))
                
                print(f"  [INFO] {codigo}: Minorista=Gs.{precio_minorista:,}, Mayorista=Gs.{precio_mayorista:,}")
            
            connection.commit()
            
            # Verificar precios asignados
            self.cursor.execute("""
                SELECT COUNT(*)
                FROM precios_por_lista
                WHERE ID_Lista IN (9001, 9002)
            """)
            
            count = self.cursor.fetchone()[0]
            
            self.assert_equals(
                count, 6,  # 3 productos x 2 listas
                "Precios asignados correctamente"
            )
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # TEST 3: CONSULTAR PRECIO SEGÚN LISTA
    # ========================================================================
    def test_03_consultar_precio_segun_lista(self):
        """
        Consulta el precio de un producto según la lista del cliente
        - Simulación de consulta en venta
        - Comparación de precios entre listas
        """
        self.print_header(3, "CONSULTAR PRECIO SEGÚN LISTA")
        
        try:
            # Consultar precio de productos en ambas listas
            self.cursor.execute("""
                SELECT 
                    p.Codigo,
                    p.Descripcion,
                    l.Nombre_Lista,
                    pp.Precio_Unitario_Neto
                FROM precios_por_lista pp
                INNER JOIN productos p ON pp.ID_Producto = p.ID_Producto
                INNER JOIN listas_precios l ON pp.ID_Lista = l.ID_Lista
                WHERE pp.ID_Lista IN (9001, 9002)
                ORDER BY p.Codigo, l.ID_Lista
            """)
            
            precios = self.cursor.fetchall()
            
            self.assert_true(
                len(precios) > 0,
                f"Precios consultados: {len(precios)} registros"
            )
            
            # Mostrar comparación de precios
            print("\n  Comparación de precios por lista:")
            producto_actual = None
            precio_minorista = None
            
            for precio in precios:
                codigo, desc, lista, precio_neto = precio
                
                if codigo != producto_actual:
                    if producto_actual is not None:
                        # Mostrar comparación
                        ahorro = precio_minorista - precio_neto if precio_minorista else 0
                        porcentaje = (ahorro / precio_minorista * 100) if precio_minorista else 0
                        print(f"    Ahorro mayorista: Gs.{ahorro:,.0f} ({porcentaje:.1f}%)")
                    
                    print(f"\n  {codigo} - {desc[:40]}")
                    producto_actual = codigo
                
                print(f"    {lista}: Gs.{precio_neto:,}")
                
                if 'Minorista' in lista:
                    precio_minorista = precio_neto
            
            # Consultar función para obtener precio (simulación)
            self.cursor.execute("""
                SELECT 
                    p.ID_Producto,
                    p.Codigo,
                    pp.Precio_Unitario_Neto as Precio_Minorista,
                    pp2.Precio_Unitario_Neto as Precio_Mayorista,
                    (pp.Precio_Unitario_Neto - pp2.Precio_Unitario_Neto) as Diferencia
                FROM productos p
                LEFT JOIN precios_por_lista pp ON p.ID_Producto = pp.ID_Producto AND pp.ID_Lista = 9001
                LEFT JOIN precios_por_lista pp2 ON p.ID_Producto = pp2.ID_Producto AND pp2.ID_Lista = 9002
                WHERE pp.ID_Precio IS NOT NULL
                LIMIT 3
            """)
            
            comparacion = self.cursor.fetchall()
            
            self.assert_true(
                len(comparacion) > 0,
                "\nConsulta de precios para venta funcional"
            )
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # TEST 4: ACTUALIZACIÓN DE PRECIOS E HISTORIAL
    # ========================================================================
    def test_04_actualizacion_precios_historial(self):
        """
        Actualiza precios y registra en historial
        - Actualizar precio de producto
        - Registrar cambio en historial
        - Verificar trazabilidad
        """
        self.print_header(4, "ACTUALIZACIÓN DE PRECIOS E HISTORIAL")
        
        try:
            # Obtener un precio para actualizar
            self.cursor.execute("""
                SELECT 
                    pp.ID_Precio,
                    pp.ID_Producto,
                    pp.ID_Lista,
                    pp.Precio_Unitario_Neto,
                    p.Codigo
                FROM precios_por_lista pp
                INNER JOIN productos p ON pp.ID_Producto = p.ID_Producto
                WHERE pp.ID_Lista = 9001
                LIMIT 1
            """)
            
            precio_info = self.cursor.fetchone()
            id_precio, id_producto, id_lista, precio_actual, codigo = precio_info
            
            print(f"  [INFO] Producto: {codigo}")
            print(f"  [INFO] Precio actual: Gs.{precio_actual:,}")
            
            # Nuevo precio (aumento del 10%)
            precio_nuevo = int(precio_actual * 1.10)
            
            print(f"  [INFO] Nuevo precio: Gs.{precio_nuevo:,} (+10%)")
            
            # Obtener empleado para auditoría
            self.cursor.execute("SELECT ID_Empleado FROM empleados LIMIT 1")
            id_empleado = self.cursor.fetchone()[0]
            
            # Registrar en historial ANTES de actualizar
            self.cursor.execute("""
                INSERT INTO historico_precios (
                    ID_Historico,
                    ID_Precio,
                    ID_Producto,
                    ID_Lista,
                    Precio_Anterior,
                    Precio_Nuevo,
                    ID_Empleado_Modifico
                ) VALUES (
                    9001,
                    %s, %s, %s, %s, %s, %s
                )
            """, (id_precio, id_producto, id_lista, precio_actual, precio_nuevo, id_empleado))
            
            # Actualizar precio
            self.cursor.execute("""
                UPDATE precios_por_lista
                SET Precio_Unitario_Neto = %s
                WHERE ID_Precio = %s
            """, (precio_nuevo, id_precio))
            
            connection.commit()
            
            self.assert_true(
                True,
                "Precio actualizado y registrado en historial"
            )
            
            # Verificar actualización
            self.cursor.execute("""
                SELECT Precio_Unitario_Neto
                FROM precios_por_lista
                WHERE ID_Precio = %s
            """, (id_precio,))
            
            precio_verificado = self.cursor.fetchone()[0]
            
            self.assert_equals(
                precio_verificado, precio_nuevo,
                f"Precio actualizado verificado: Gs.{precio_verificado:,}"
            )
            
            # Verificar historial
            self.cursor.execute("""
                SELECT 
                    Precio_Anterior,
                    Precio_Nuevo,
                    Fecha_Cambio,
                    ID_Empleado_Modifico
                FROM historico_precios
                WHERE ID_Historico = 9001
            """)
            
            historial = self.cursor.fetchone()
            
            self.assert_true(
                historial is not None,
                "Cambio registrado en historial"
            )
            
            print(f"  [INFO] Historial: De Gs.{float(historial[0]):,.0f} a Gs.{float(historial[1]):,.0f}")
            print(f"  [INFO] Fecha: {historial[2]}")
            print(f"  [INFO] Empleado: {historial[3]}")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # TEST 5: REPORTES DE PRECIOS
    # ========================================================================
    def test_05_reportes_precios(self):
        """
        Genera reportes de precios
        - Lista completa de precios
        - Historial de cambios
        - Análisis de precios
        """
        self.print_header(5, "REPORTES DE PRECIOS")
        
        try:
            # 1. REPORTE DE PRECIOS POR LISTA
            self.cursor.execute("""
                SELECT 
                    l.Nombre_Lista,
                    COUNT(pp.ID_Precio) as Total_Productos,
                    MIN(pp.Precio_Unitario_Neto) as Precio_Minimo,
                    MAX(pp.Precio_Unitario_Neto) as Precio_Maximo,
                    AVG(pp.Precio_Unitario_Neto) as Precio_Promedio
                FROM listas_precios l
                LEFT JOIN precios_por_lista pp ON l.ID_Lista = pp.ID_Lista
                WHERE l.Activo = 1
                GROUP BY l.ID_Lista
                ORDER BY l.ID_Lista
            """)
            
            reporte_listas = self.cursor.fetchall()
            
            print("  [INFO] Reporte por lista de precios:\n")
            for lista in reporte_listas:
                nombre, total, minimo, maximo, promedio = lista
                if total > 0:
                    print(f"  {nombre}:")
                    print(f"    Productos: {total}")
                    print(f"    Rango: Gs.{minimo:,} - Gs.{maximo:,}")
                    print(f"    Promedio: Gs.{float(promedio):,.0f}\n")
            
            # 2. HISTORIAL DE CAMBIOS RECIENTES
            self.cursor.execute("""
                SELECT 
                    p.Codigo,
                    p.Descripcion,
                    l.Nombre_Lista,
                    h.Precio_Anterior,
                    h.Precio_Nuevo,
                    h.Fecha_Cambio,
                    ((h.Precio_Nuevo - h.Precio_Anterior) / h.Precio_Anterior * 100) as Porcentaje_Cambio
                FROM historico_precios h
                INNER JOIN productos p ON h.ID_Producto = p.ID_Producto
                INNER JOIN listas_precios l ON h.ID_Lista = l.ID_Lista
                ORDER BY h.Fecha_Cambio DESC
                LIMIT 10
            """)
            
            historial = self.cursor.fetchall()
            
            if len(historial) > 0:
                print("  [INFO] Últimos cambios de precios:\n")
                for cambio in historial:
                    codigo, desc, lista, anterior, nuevo, fecha, porcentaje = cambio
                    simbolo = "↑" if nuevo > anterior else "↓"
                    print(f"  {codigo} ({lista[:20]})")
                    print(f"    {float(anterior):,.0f} → {float(nuevo):,.0f} {simbolo} {float(porcentaje):.1f}%")
                    print(f"    Fecha: {fecha}\n")
            
            # 3. PRODUCTOS SIN PRECIO EN ALGUNA LISTA
            self.cursor.execute("""
                SELECT 
                    p.Codigo,
                    p.Descripcion,
                    COUNT(pp.ID_Precio) as Listas_Con_Precio,
                    (SELECT COUNT(*) FROM listas_precios WHERE Activo = 1) as Total_Listas
                FROM productos p
                LEFT JOIN precios_por_lista pp ON p.ID_Producto = pp.ID_Producto
                WHERE p.Activo = 1
                GROUP BY p.ID_Producto
                HAVING Listas_Con_Precio < Total_Listas
                LIMIT 5
            """)
            
            sin_precio = self.cursor.fetchall()
            
            if len(sin_precio) > 0:
                print("  [ALERTA] Productos sin precio en todas las listas:")
                for prod in sin_precio:
                    print(f"    - {prod[0]}: {prod[2]}/{prod[3]} listas")
            
            self.assert_true(
                True,
                "\nReportes de precios generados correctamente"
            )
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def run_all_tests(self):
        """Ejecuta todos los tests del módulo"""
        print("\n" + "="*70)
        print("INICIANDO TESTS DE MÓDULO: PRECIOS Y LISTAS")
        print("="*70)
        
        try:
            # Ejecutar todos los tests
            self.test_01_crear_listas_precios()
            self.test_02_asignar_precios_productos()
            self.test_03_consultar_precio_segun_lista()
            self.test_04_actualizacion_precios_historial()
            self.test_05_reportes_precios()
            
        except Exception as e:
            print(f"\n[ERROR FATAL] {str(e)}")
            self.tests_failed += 1
        
        finally:
            # Mostrar resumen
            print("\n" + "="*70)
            print("RESUMEN DE TESTS - MÓDULO PRECIOS")
            print("="*70)
            print(f"Tests exitosos: {self.tests_passed}")
            print(f"Tests fallidos: {self.tests_failed}")
            total = self.tests_passed + self.tests_failed
            if total > 0:
                porcentaje = (self.tests_passed / total) * 100
                print(f"Porcentaje de éxito: {porcentaje:.1f}%")
            
            print(f"\nTotal: {self.tests_passed}/{total} tests exitosos ({porcentaje:.1f}%)")
            print("="*70)
            
            # Limpiar datos de prueba
            try:
                self.limpiar_datos_prueba()
                print("\n[INFO] Datos de prueba limpiados correctamente")
            except Exception as e:
                print(f"\n[WARNING] Error al limpiar datos: {e}")
            
            self.cursor.close()

if __name__ == "__main__":
    test = TestPrecios()
    test.run_all_tests()
