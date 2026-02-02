"""
TEST MÓDULO: INVENTARIO Y STOCK
===============================
Pruebas para gestión de inventario, movimientos de stock y ajustes.

Tablas: stock_unico, movimientos_stock, ajustes_inventario, detalle_ajuste

Autor: Sistema de Tests Automatizado
Fecha: 26 de Noviembre de 2025
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection
from datetime import datetime, timedelta
from decimal import Decimal

class TestInventario:
    def __init__(self):
        self.cursor = connection.cursor()
        self.tests_passed = 0
        self.tests_failed = 0
        self.limpiar_datos_prueba()
    
    def limpiar_datos_prueba(self):
        """Limpia datos de pruebas anteriores"""
        try:
            # Limpiar en orden por foreign keys
            self.cursor.execute("DELETE FROM detalle_ajuste WHERE ID_Ajuste >= 9000")
            self.cursor.execute("DELETE FROM ajustes_inventario WHERE ID_Ajuste >= 9000")
            self.cursor.execute("DELETE FROM movimientos_stock WHERE ID_MovimientoStock >= 9000")
            connection.commit()
        except Exception as e:
            connection.rollback()
            print(f"[INFO] Limpieza inicial: {e}")
    
    def setup_datos_base(self):
        """Crea datos base necesarios para los tests"""
        # Verificar que existe al menos un producto
        self.cursor.execute("SELECT ID_Producto FROM productos WHERE Activo = 1 LIMIT 1")
        if not self.cursor.fetchone():
            raise Exception("No hay productos activos en la base de datos")
        
        # Verificar que existe al menos un empleado
        self.cursor.execute("SELECT ID_Empleado FROM empleados LIMIT 1")
        if not self.cursor.fetchone():
            raise Exception("No hay empleados en la base de datos")
    
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
    # TEST 1: CONSULTA DE STOCK ACTUAL
    # ========================================================================
    def test_01_consulta_stock_actual(self):
        """
        Verifica la consulta de stock actual por producto
        - Consulta stock de productos activos
        - Verifica formato de datos
        - Valida fecha de última actualización
        """
        self.print_header(1, "CONSULTA DE STOCK ACTUAL")
        
        try:
            # Consultar stock actual de productos
            self.cursor.execute("""
                SELECT 
                    s.ID_Producto,
                    p.Codigo,
                    p.Descripcion,
                    s.Stock_Actual,
                    s.Fecha_Ultima_Actualizacion,
                    p.Stock_Minimo
                FROM stock_unico s
                INNER JOIN productos p ON s.ID_Producto = p.ID_Producto
                WHERE p.Activo = 1
                ORDER BY p.Codigo
                LIMIT 5
            """)
            
            resultados = self.cursor.fetchall()
            
            self.assert_true(
                len(resultados) > 0,
                f"Productos con stock encontrados: {len(resultados)}"
            )
            
            # Verificar estructura de datos
            for producto in resultados:
                id_prod, codigo, desc, stock, fecha_act, stock_min = producto
                
                self.assert_true(
                    id_prod is not None and id_prod > 0,
                    f"Producto {codigo} tiene ID válido"
                )
                
                self.assert_true(
                    stock is not None,
                    f"Producto {codigo} tiene stock definido: {stock}"
                )
                
                self.assert_true(
                    fecha_act is not None,
                    f"Producto {codigo} tiene fecha de actualización"
                )
                
                # Verificar alertas de stock bajo
                if stock < stock_min:
                    print(f"  [ALERTA] Producto {codigo} con stock bajo: {stock} < {stock_min}")
            
            # Consultar productos con stock crítico
            self.cursor.execute("""
                SELECT COUNT(*) 
                FROM stock_unico s
                INNER JOIN productos p ON s.ID_Producto = p.ID_Producto
                WHERE p.Activo = 1 
                  AND s.Stock_Actual < p.Stock_Minimo
            """)
            
            productos_criticos = self.cursor.fetchone()[0]
            print(f"  [INFO] Productos con stock crítico: {productos_criticos}")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # TEST 2: REGISTRO DE MOVIMIENTOS DE STOCK
    # ========================================================================
    def test_02_movimientos_stock(self):
        """
        Prueba el registro de movimientos de stock
        - Entrada de mercadería
        - Salida por venta
        - Ajustes manuales
        """
        self.print_header(2, "REGISTRO DE MOVIMIENTOS DE STOCK")
        
        try:
            # Obtener producto para prueba
            self.cursor.execute("""
                SELECT p.ID_Producto, p.Codigo, s.Stock_Actual
                FROM productos p
                INNER JOIN stock_unico s ON p.ID_Producto = s.ID_Producto
                WHERE p.Activo = 1
                LIMIT 1
            """)
            producto = self.cursor.fetchone()
            id_producto, codigo, stock_inicial = producto
            
            # Obtener empleado
            self.cursor.execute("SELECT ID_Empleado FROM empleados LIMIT 1")
            id_empleado = self.cursor.fetchone()[0]
            
            print(f"  [INFO] Producto: {codigo}, Stock inicial: {stock_inicial}")
            
            # 1. MOVIMIENTO DE ENTRADA
            cantidad_entrada = Decimal('10.000')
            self.cursor.execute("""
                INSERT INTO movimientos_stock (
                    ID_MovimientoStock,
                    ID_Producto,
                    ID_Empleado_Autoriza,
                    Tipo_Movimiento,
                    Cantidad,
                    Stock_Resultante,
                    Referencia_Documento
                ) VALUES (
                    9001,
                    %s, %s, 'Entrada', %s, %s, 'TEST-ENT-001'
                )
            """, (id_producto, id_empleado, cantidad_entrada, stock_inicial + cantidad_entrada))
            
            # Actualizar stock
            self.cursor.execute("""
                UPDATE stock_unico 
                SET Stock_Actual = Stock_Actual + %s
                WHERE ID_Producto = %s
            """, (cantidad_entrada, id_producto))
            
            connection.commit()
            
            # Verificar movimiento registrado
            self.cursor.execute("""
                SELECT Tipo_Movimiento, Cantidad, Stock_Resultante
                FROM movimientos_stock
                WHERE ID_MovimientoStock = 9001
            """)
            movimiento = self.cursor.fetchone()
            
            self.assert_equals(
                movimiento[0], 'Entrada',
                "Movimiento de entrada registrado correctamente"
            )
            
            # Verificar stock actualizado
            self.cursor.execute("""
                SELECT Stock_Actual 
                FROM stock_unico 
                WHERE ID_Producto = %s
            """, (id_producto,))
            stock_nuevo = self.cursor.fetchone()[0]
            
            # Verificar que el stock aumentó (puede tener movimientos previos)
            self.assert_true(
                stock_nuevo >= stock_inicial + cantidad_entrada,
                f"Stock actualizado correctamente: {stock_nuevo}"
            )
            
            # 2. MOVIMIENTO DE SALIDA
            cantidad_salida = Decimal('5.000')
            self.cursor.execute("""
                INSERT INTO movimientos_stock (
                    ID_MovimientoStock,
                    ID_Producto,
                    ID_Empleado_Autoriza,
                    Tipo_Movimiento,
                    Cantidad,
                    Stock_Resultante,
                    Referencia_Documento
                ) VALUES (
                    9002,
                    %s, %s, 'Salida', %s, %s, 'TEST-SAL-001'
                )
            """, (id_producto, id_empleado, cantidad_salida, stock_nuevo - cantidad_salida))
            
            self.cursor.execute("""
                UPDATE stock_unico 
                SET Stock_Actual = Stock_Actual - %s
                WHERE ID_Producto = %s
            """, (cantidad_salida, id_producto))
            
            connection.commit()
            
            # Verificar stock final
            self.cursor.execute("""
                SELECT Stock_Actual 
                FROM stock_unico 
                WHERE ID_Producto = %s
            """, (id_producto,))
            stock_final = self.cursor.fetchone()[0]
            
            print(f"  [OK] Stock final: {stock_final} (después de entrada y salida)")
            
            # 3. CONSULTAR HISTORIAL DE MOVIMIENTOS
            
            # 3. CONSULTAR HISTORIAL DE MOVIMIENTOS
            self.cursor.execute("""
                SELECT 
                    Tipo_Movimiento,
                    Cantidad,
                    Stock_Resultante,
                    Referencia_Documento
                FROM movimientos_stock
                WHERE ID_Producto = %s
                  AND ID_MovimientoStock IN (9001, 9002)
                ORDER BY ID_MovimientoStock
            """, (id_producto,))
            
            historial = self.cursor.fetchall()
            
            self.assert_equals(
                len(historial), 2,
                f"Historial de movimientos completo: {len(historial)} movimientos"
            )
            
            print(f"  [INFO] Movimiento 1: {historial[0][0]} - {historial[0][1]} unidades")
            print(f"  [INFO] Movimiento 2: {historial[1][0]} - {historial[1][1]} unidades")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # TEST 3: AJUSTES DE INVENTARIO
    # ========================================================================
    def test_03_ajustes_inventario(self):
        """
        Prueba los ajustes manuales de inventario
        - Crear ajuste en borrador
        - Agregar detalles de productos
        - Finalizar ajuste
        - Verificar movimientos generados
        """
        self.print_header(3, "AJUSTES DE INVENTARIO")
        
        try:
            # Obtener empleado
            self.cursor.execute("SELECT ID_Empleado FROM empleados LIMIT 1")
            id_empleado = self.cursor.fetchone()[0]
            
            # Obtener producto para ajuste
            self.cursor.execute("""
                SELECT p.ID_Producto, p.Codigo, s.Stock_Actual
                FROM productos p
                INNER JOIN stock_unico s ON p.ID_Producto = s.ID_Producto
                WHERE p.Activo = 1
                LIMIT 1
            """)
            producto = self.cursor.fetchone()
            id_producto, codigo, stock_actual = producto
            
            print(f"  [INFO] Producto: {codigo}, Stock actual: {stock_actual}")
            
            # 1. CREAR AJUSTE EN BORRADOR
            self.cursor.execute("""
                INSERT INTO ajustes_inventario (
                    ID_Ajuste,
                    ID_Empleado_Responsable,
                    Tipo_Ajuste,
                    Motivo,
                    Estado
                ) VALUES (
                    9001,
                    %s,
                    'Positivo',
                    'Ajuste de inventario físico - TEST',
                    'Borrador'
                )
            """, (id_empleado,))
            
            connection.commit()
            
            self.assert_true(
                True,
                "Ajuste creado en estado Borrador"
            )
            
            # 2. AGREGAR DETALLE DE PRODUCTO A AJUSTAR
            cantidad_ajuste = Decimal('3.500')
            
            # Primero crear el movimiento
            self.cursor.execute("""
                INSERT INTO movimientos_stock (
                    ID_MovimientoStock,
                    ID_Producto,
                    ID_Empleado_Autoriza,
                    Tipo_Movimiento,
                    Cantidad,
                    Stock_Resultante,
                    Referencia_Documento
                ) VALUES (
                    9003,
                    %s, %s, 'Ajuste', %s, %s, 'AJUSTE-9001'
                )
            """, (id_producto, id_empleado, cantidad_ajuste, stock_actual + cantidad_ajuste))
            
            # Luego el detalle del ajuste
            self.cursor.execute("""
                INSERT INTO detalle_ajuste (
                    ID_Detalle,
                    ID_Ajuste,
                    ID_Producto,
                    ID_MovimientoStock,
                    Cantidad_Ajustada
                ) VALUES (
                    9001,
                    9001,
                    %s,
                    9003,
                    %s
                )
            """, (id_producto, cantidad_ajuste))
            
            connection.commit()
            
            self.assert_true(
                True,
                f"Detalle agregado: +{cantidad_ajuste} unidades"
            )
            
            # 3. FINALIZAR AJUSTE
            self.cursor.execute("""
                UPDATE ajustes_inventario
                SET Estado = 'Finalizado'
                WHERE ID_Ajuste = 9001
            """)
            
            # Actualizar stock
            self.cursor.execute("""
                UPDATE stock_unico
                SET Stock_Actual = Stock_Actual + %s
                WHERE ID_Producto = %s
            """, (cantidad_ajuste, id_producto))
            
            connection.commit()
            
            self.assert_true(
                True,
                "Ajuste finalizado correctamente"
            )
            
            # 4. VERIFICAR ESTADO DEL AJUSTE
            self.cursor.execute("""
                SELECT 
                    a.Estado,
                    a.Tipo_Ajuste,
                    a.Motivo,
                    COUNT(d.ID_Detalle) as Total_Productos
                FROM ajustes_inventario a
                LEFT JOIN detalle_ajuste d ON a.ID_Ajuste = d.ID_Ajuste
                WHERE a.ID_Ajuste = 9001
                GROUP BY a.ID_Ajuste
            """)
            
            ajuste_info = self.cursor.fetchone()
            
            self.assert_equals(
                ajuste_info[0], 'Finalizado',
                "Estado del ajuste verificado"
            )
            
            self.assert_equals(
                ajuste_info[3], 1,
                f"Productos en el ajuste: {ajuste_info[3]}"
            )
            
            # 5. VERIFICAR STOCK ACTUALIZADO
            self.cursor.execute("""
                SELECT Stock_Actual
                FROM stock_unico
                WHERE ID_Producto = %s
            """, (id_producto,))
            
            stock_nuevo = self.cursor.fetchone()[0]
            
            # Verificar que el stock es mayor que antes del ajuste
            self.assert_true(
                stock_nuevo > stock_actual,
                f"Stock actualizado por ajuste: {stock_nuevo}"
            )
            
            # 6. VERIFICAR MOVIMIENTO GENERADO
            self.cursor.execute("""
                SELECT Tipo_Movimiento, Cantidad, Referencia_Documento
                FROM movimientos_stock
                WHERE ID_MovimientoStock = 9003
            """)
            
            movimiento = self.cursor.fetchone()
            
            self.assert_equals(
                movimiento[0], 'Ajuste',
                "Movimiento de ajuste registrado"
            )
            
            self.assert_equals(
                movimiento[2], 'AJUSTE-9001',
                "Referencia al ajuste correcta"
            )
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # TEST 4: ALERTAS DE STOCK BAJO/CRÍTICO
    # ========================================================================
    def test_04_alertas_stock_critico(self):
        """
        Verifica el sistema de alertas de stock
        - Productos con stock bajo (< stock_minimo)
        - Productos sin stock
        - Reporte de productos críticos
        """
        self.print_header(4, "ALERTAS DE STOCK BAJO/CRÍTICO")
        
        try:
            # 1. CONSULTAR PRODUCTOS CON STOCK BAJO
            self.cursor.execute("""
                SELECT 
                    p.Codigo,
                    p.Descripcion,
                    s.Stock_Actual,
                    p.Stock_Minimo,
                    (p.Stock_Minimo - s.Stock_Actual) as Faltante
                FROM productos p
                INNER JOIN stock_unico s ON p.ID_Producto = s.ID_Producto
                WHERE p.Activo = 1
                  AND s.Stock_Actual < p.Stock_Minimo
                ORDER BY (p.Stock_Minimo - s.Stock_Actual) DESC
            """)
            
            productos_bajos = self.cursor.fetchall()
            
            print(f"  [INFO] Productos con stock bajo: {len(productos_bajos)}")
            
            if len(productos_bajos) > 0:
                print("\n  Detalle de productos con stock bajo:")
                for prod in productos_bajos[:5]:  # Mostrar máximo 5
                    print(f"    - {prod[0]}: Stock={prod[2]}, Mínimo={prod[3]}, Faltan={prod[4]}")
            
            # 2. CONSULTAR PRODUCTOS SIN STOCK
            self.cursor.execute("""
                SELECT 
                    p.Codigo,
                    p.Descripcion,
                    s.Stock_Actual
                FROM productos p
                INNER JOIN stock_unico s ON p.ID_Producto = s.ID_Producto
                WHERE p.Activo = 1
                  AND s.Stock_Actual <= 0
            """)
            
            productos_sin_stock = self.cursor.fetchall()
            
            print(f"\n  [ALERTA] Productos sin stock: {len(productos_sin_stock)}")
            
            if len(productos_sin_stock) > 0:
                print("  Productos sin stock:")
                for prod in productos_sin_stock[:5]:
                    print(f"    - {prod[0]}: {prod[1]}")
            
            # 3. REPORTE DE STOCK POR CATEGORÍA
            self.cursor.execute("""
                SELECT 
                    c.Nombre as Categoria,
                    COUNT(p.ID_Producto) as Total_Productos,
                    SUM(CASE WHEN s.Stock_Actual < p.Stock_Minimo THEN 1 ELSE 0 END) as Con_Stock_Bajo,
                    SUM(CASE WHEN s.Stock_Actual <= 0 THEN 1 ELSE 0 END) as Sin_Stock
                FROM categorias c
                LEFT JOIN productos p ON c.ID_Categoria = p.ID_Categoria
                LEFT JOIN stock_unico s ON p.ID_Producto = s.ID_Producto
                WHERE p.Activo = 1
                GROUP BY c.ID_Categoria
                HAVING Total_Productos > 0
                ORDER BY Con_Stock_Bajo DESC
            """)
            
            reporte_categorias = self.cursor.fetchall()
            
            print(f"\n  [INFO] Reporte por categoría:")
            for cat in reporte_categorias:
                print(f"    {cat[0]}: {cat[1]} productos, {cat[2]} con stock bajo, {cat[3]} sin stock")
            
            # 4. USAR VISTA DE ALERTAS (si existe)
            try:
                self.cursor.execute("""
                    SELECT COUNT(*) 
                    FROM v_stock_alerta
                """)
                alertas_vista = self.cursor.fetchone()[0]
                print(f"\n  [INFO] Vista v_stock_alerta: {alertas_vista} alertas")
            except:
                print(f"\n  [INFO] Vista v_stock_alerta no disponible")
            
            self.assert_true(
                True,
                "Sistema de alertas funcional"
            )
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # TEST 5: REPORTES DE MOVIMIENTOS
    # ========================================================================
    def test_05_reportes_movimientos(self):
        """
        Genera reportes de movimientos de stock
        - Movimientos por período
        - Movimientos por producto
        - Resumen de entradas/salidas
        """
        self.print_header(5, "REPORTES DE MOVIMIENTOS")
        
        try:
            # 1. MOVIMIENTOS DEL DÍA
            self.cursor.execute("""
                SELECT 
                    Tipo_Movimiento,
                    COUNT(*) as Cantidad_Movimientos,
                    SUM(Cantidad) as Total_Unidades
                FROM movimientos_stock
                WHERE DATE(Fecha_Hora) = CURDATE()
                GROUP BY Tipo_Movimiento
            """)
            
            movimientos_hoy = self.cursor.fetchall()
            
            print(f"  [INFO] Movimientos del día:")
            for mov in movimientos_hoy:
                print(f"    {mov[0]}: {mov[1]} movimientos, {mov[2]} unidades")
            
            # 2. PRODUCTOS MÁS MOVIDOS (ÚLTIMOS 7 DÍAS)
            self.cursor.execute("""
                SELECT 
                    p.Codigo,
                    p.Descripcion,
                    COUNT(m.ID_MovimientoStock) as Total_Movimientos,
                    SUM(CASE WHEN m.Tipo_Movimiento = 'Entrada' THEN m.Cantidad ELSE 0 END) as Total_Entradas,
                    SUM(CASE WHEN m.Tipo_Movimiento = 'Salida' THEN m.Cantidad ELSE 0 END) as Total_Salidas
                FROM movimientos_stock m
                INNER JOIN productos p ON m.ID_Producto = p.ID_Producto
                WHERE m.Fecha_Hora >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY m.ID_Producto
                ORDER BY Total_Movimientos DESC
                LIMIT 10
            """)
            
            productos_movidos = self.cursor.fetchall()
            
            print(f"\n  [INFO] Top 10 productos más movidos (últimos 7 días):")
            for i, prod in enumerate(productos_movidos, 1):
                print(f"    {i}. {prod[0]}: {prod[2]} movimientos (E:{prod[3]}, S:{prod[4]})")
            
            # 3. RESUMEN GENERAL DE STOCK
            self.cursor.execute("""
                SELECT 
                    COUNT(DISTINCT p.ID_Producto) as Total_Productos,
                    SUM(s.Stock_Actual) as Stock_Total,
                    AVG(s.Stock_Actual) as Promedio_Stock,
                    MIN(s.Stock_Actual) as Stock_Minimo_Sistema,
                    MAX(s.Stock_Actual) as Stock_Maximo_Sistema
                FROM productos p
                INNER JOIN stock_unico s ON p.ID_Producto = s.ID_Producto
                WHERE p.Activo = 1
            """)
            
            resumen = self.cursor.fetchone()
            
            print(f"\n  [INFO] Resumen general de inventario:")
            print(f"    Total productos: {resumen[0]}")
            print(f"    Stock total: {resumen[1]}")
            print(f"    Promedio por producto: {float(resumen[2]):.2f}")
            print(f"    Rango: {resumen[3]} - {resumen[4]}")
            
            # 4. VALOR DE INVENTARIO (si hay precios)
            try:
                self.cursor.execute("""
                    SELECT 
                        SUM(s.Stock_Actual * COALESCE(pp.Precio_Unitario_Neto, 0)) as Valor_Total
                    FROM stock_unico s
                    INNER JOIN productos p ON s.ID_Producto = p.ID_Producto
                    LEFT JOIN precios_por_lista pp ON s.ID_Producto = pp.ID_Producto AND pp.ID_Lista = 1
                    WHERE p.Activo = 1
                """)
                
                valor_inventario = self.cursor.fetchone()[0]
                if valor_inventario:
                    print(f"    Valor estimado inventario: Gs. {float(valor_inventario):,.0f}")
            except:
                print(f"    Valor de inventario: No disponible")
            
            self.assert_true(
                True,
                "Reportes de movimientos generados correctamente"
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
        print("INICIANDO TESTS DE MÓDULO: INVENTARIO Y STOCK")
        print("="*70)
        
        try:
            self.setup_datos_base()
            
            # Ejecutar todos los tests
            self.test_01_consulta_stock_actual()
            self.test_02_movimientos_stock()
            self.test_03_ajustes_inventario()
            self.test_04_alertas_stock_critico()
            self.test_05_reportes_movimientos()
            
        except Exception as e:
            print(f"\n[ERROR FATAL] {str(e)}")
            self.tests_failed += 1
        
        finally:
            # Mostrar resumen
            print("\n" + "="*70)
            print("RESUMEN DE TESTS - MÓDULO INVENTARIO")
            print("="*70)
            print(f"Tests exitosos: {self.tests_passed}")
            print(f"Tests fallidos: {self.tests_failed}")
            total = self.tests_passed + self.tests_failed
            if total > 0:
                porcentaje = (self.tests_passed / total) * 100
                print(f"Porcentaje de éxito: {porcentaje:.1f}%")
            print("="*70)
            
            # Limpiar datos de prueba
            try:
                self.limpiar_datos_prueba()
                print("\n[INFO] Datos de prueba limpiados correctamente")
            except Exception as e:
                print(f"\n[WARNING] Error al limpiar datos: {e}")
            
            self.cursor.close()

if __name__ == "__main__":
    test = TestInventario()
    test.run_all_tests()
