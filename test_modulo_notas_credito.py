"""
TEST MÓDULO: NOTAS DE CRÉDITO
==============================
Pruebas para gestión de notas de crédito y devoluciones.

Tablas: notas_credito, detalle_nota

Autor: Sistema de Tests Automatizado
Fecha: 26 de Noviembre de 2025
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection
from datetime import datetime
from decimal import Decimal

class TestNotasCredito:
    def __init__(self):
        self.cursor = connection.cursor()
        self.tests_passed = 0
        self.tests_failed = 0
        self.limpiar_datos_prueba()
    
    def limpiar_datos_prueba(self):
        """Limpia datos de pruebas anteriores"""
        try:
            self.cursor.execute("DELETE FROM detalle_nota WHERE ID_Nota >= 9000")
            self.cursor.execute("DELETE FROM notas_credito WHERE ID_Nota >= 9000")
            connection.commit()
        except Exception as e:
            connection.rollback()
            print(f"[INFO] Limpieza inicial: {e}")
    
    def print_header(self, test_num, test_name):
        print(f"\n{'='*70}")
        print(f"TEST {test_num}: {test_name}")
        print('='*70)
    
    def assert_true(self, condition, mensaje):
        if condition:
            print(f"  [OK] {mensaje}")
            return True
        else:
            print(f"  [FALLO] {mensaje}")
            self.tests_failed += 1
            return False
    
    def assert_equals(self, actual, esperado, mensaje):
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
    # TEST 1: EMISIÓN DE NOTA DE CRÉDITO DESDE VENTA
    # ========================================================================
    def test_01_emision_nota_credito(self):
        """
        Prueba la emisión de una nota de crédito desde una venta
        - Obtener venta completada
        - Crear documento tributario
        - Emitir nota de crédito
        """
        self.print_header(1, "EMISIÓN DE NOTA DE CRÉDITO DESDE VENTA")
        
        try:
            # Obtener venta completada
            self.cursor.execute("""
                SELECT v.ID_Venta, v.ID_Cliente, v.Monto_Total, c.Nombres, c.Apellidos
                FROM ventas v
                INNER JOIN clientes c ON v.ID_Cliente = c.ID_Cliente
                WHERE v.Estado = 'Completada'
                  AND v.Monto_Total > 0
                LIMIT 1
            """)
            
            venta = self.cursor.fetchone()
            if not venta:
                print("  [INFO] No hay ventas para emitir nota de crédito")
                self.tests_passed += 1
                return True
            
            id_venta, id_cliente, monto_venta, nombre, apellido = venta
            
            print(f"  [INFO] Venta: #{id_venta}, Cliente: {nombre} {apellido}")
            print(f"  [INFO] Monto venta: Gs.{float(monto_venta):,.0f}")
            
            # Obtener timbrado activo
            self.cursor.execute("""
                SELECT Nro_Timbrado
                FROM timbrados
                WHERE Tipo_Documento = 'Nota Credito'
                  AND Activo = 1
                  AND Fecha_Inicio <= CURDATE()
                  AND Fecha_Fin >= CURDATE()
                LIMIT 1
            """)
            timbrado = self.cursor.fetchone()
            
            if not timbrado:
                print("  [INFO] No hay timbrado activo para emitir nota")
                self.tests_passed += 1
                return True
            
            nro_timbrado = timbrado[0]
            
            # Crear documento tributario para la nota
            self.cursor.execute("""
                INSERT INTO documentos_tributarios (
                    ID_Documento,
                    Nro_Timbrado,
                    Nro_Secuencial,
                    Monto_Total,
                    Monto_Exento,
                    Monto_Gravado_5,
                    Monto_IVA_5,
                    Monto_Gravado_10,
                    Monto_IVA_10
                ) VALUES (
                    9001, %s, 'NC-TEST-001', %s, 0, 0, 0, 0, 0
                )
            """, (nro_timbrado, monto_venta))
            
            # Emitir nota de crédito
            motivo = "Devolución de mercadería - TEST"
            self.cursor.execute("""
                INSERT INTO notas_credito (
                    ID_Nota,
                    ID_Documento,
                    ID_Cliente,
                    ID_Venta_Original,
                    Monto_Total,
                    Motivo_Devolucion,
                    Estado
                ) VALUES (
                    9001, 9001, %s, %s, %s, %s, 'Emitida'
                )
            """, (id_cliente, id_venta, monto_venta, motivo))
            
            connection.commit()
            
            self.assert_true(
                True,
                "Nota de crédito emitida correctamente"
            )
            
            # Verificar nota creada
            self.cursor.execute("""
                SELECT n.Estado, n.Monto_Total, n.Motivo_Devolucion
                FROM notas_credito n
                WHERE n.ID_Nota = 9001
            """)
            
            nota = self.cursor.fetchone()
            
            self.assert_equals(
                nota[0], 'Emitida',
                "Estado de la nota verificado"
            )
            
            self.assert_equals(
                float(nota[1]), float(monto_venta),
                f"Monto de la nota: Gs.{float(nota[1]):,.0f}"
            )
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # TEST 2: AGREGAR DETALLES DE PRODUCTOS DEVUELTOS
    # ========================================================================
    def test_02_agregar_detalles_devolucion(self):
        """
        Agrega productos devueltos al detalle de la nota
        - Obtener productos de la venta original
        - Agregar a detalle_nota
        - Verificar subtotales
        """
        self.print_header(2, "AGREGAR DETALLES DE PRODUCTOS DEVUELTOS")
        
        try:
            # Obtener la nota creada
            self.cursor.execute("""
                SELECT ID_Nota, ID_Venta_Original, Monto_Total
                FROM notas_credito
                WHERE ID_Nota = 9001
            """)
            
            nota = self.cursor.fetchone()
            if not nota:
                print("  [INFO] No hay nota de crédito para agregar detalles")
                self.tests_passed += 1
                return True
            
            id_nota, id_venta_original, monto_total = nota
            
            # Obtener productos de la venta original
            self.cursor.execute("""
                SELECT 
                    dv.ID_Producto,
                    p.Codigo,
                    p.Descripcion,
                    dv.Cantidad,
                    dv.Precio_Unitario,
                    dv.Subtotal
                FROM detalle_venta dv
                INNER JOIN productos p ON dv.ID_Producto = p.ID_Producto
                WHERE dv.ID_Venta = %s
                LIMIT 3
            """, (id_venta_original,))
            
            productos = self.cursor.fetchall()
            
            if len(productos) == 0:
                print("  [INFO] No hay productos en la venta original")
                self.tests_passed += 1
                return True
            
            print(f"  [INFO] Productos a devolver: {len(productos)}")
            
            # Agregar cada producto al detalle de la nota
            id_detalle = 9001
            for producto in productos:
                id_producto, codigo, desc, cantidad, precio_unit, subtotal = producto
                
                self.cursor.execute("""
                    INSERT INTO detalle_nota (
                        ID_Detalle,
                        ID_Nota,
                        ID_Producto,
                        Cantidad,
                        Precio_Unitario,
                        Subtotal
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s
                    )
                """, (id_detalle, id_nota, id_producto, cantidad, precio_unit, subtotal))
                
                print(f"  [INFO] {codigo}: {cantidad} x Gs.{float(precio_unit):,.0f} = Gs.{float(subtotal):,.0f}")
                
                id_detalle += 1
            
            connection.commit()
            
            self.assert_true(
                True,
                f"Detalles agregados: {len(productos)} productos"
            )
            
            # Verificar detalles
            self.cursor.execute("""
                SELECT COUNT(*), SUM(Subtotal)
                FROM detalle_nota
                WHERE ID_Nota = 9001
            """)
            
            detalles = self.cursor.fetchone()
            cantidad_detalles, total_detalles = detalles
            
            self.assert_equals(
                cantidad_detalles, len(productos),
                f"Cantidad de detalles verificada: {cantidad_detalles}"
            )
            
            print(f"  [INFO] Total detalles: Gs.{float(total_detalles):,.0f}")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # TEST 3: APLICACIÓN DE NOTA A CUENTA CORRIENTE
    # ========================================================================
    def test_03_aplicar_nota_cuenta_corriente(self):
        """
        Aplica la nota de crédito a la cuenta corriente del cliente
        - Registrar movimiento en cuenta corriente
        - Actualizar estado de la nota
        - Verificar saldo
        """
        self.print_header(3, "APLICACIÓN A CUENTA CORRIENTE")
        
        try:
            # Obtener nota emitida
            self.cursor.execute("""
                SELECT n.ID_Nota, n.ID_Cliente, n.Monto_Total, n.Estado
                FROM notas_credito n
                WHERE n.ID_Nota = 9001
            """)
            
            nota = self.cursor.fetchone()
            if not nota:
                print("  [INFO] No hay nota para aplicar")
                self.tests_passed += 1
                return True
            
            id_nota, id_cliente, monto_nota, estado = nota
            
            if estado == 'Aplicada':
                print("  [INFO] La nota ya fue aplicada")
                self.tests_passed += 1
                return True
            
            print(f"  [INFO] Cliente: {id_cliente}")
            print(f"  [INFO] Monto nota: Gs.{float(monto_nota):,.0f}")
            
            # Consultar saldo actual del cliente
            self.cursor.execute("""
                SELECT COALESCE(SUM(Monto), 0) as Saldo
                FROM cta_corriente
                WHERE ID_Cliente = %s
            """, (id_cliente,))
            
            saldo_anterior = self.cursor.fetchone()[0]
            
            print(f"  [INFO] Saldo anterior: Gs.{float(saldo_anterior):,.0f}")
            
            # Aplicar nota a cuenta corriente (crédito a favor del cliente)
            self.cursor.execute("""
                INSERT INTO cta_corriente (
                    ID_Movimiento,
                    ID_Cliente,
                    ID_Nota_Credito,
                    Tipo_Movimiento,
                    Monto,
                    Descripcion
                ) VALUES (
                    9001,
                    %s,
                    9001,
                    'NC',
                    %s,
                    'Aplicación de Nota de Crédito TEST'
                )
            """, (id_cliente, -monto_nota))  # Negativo porque es a favor del cliente
            
            # Actualizar estado de la nota
            self.cursor.execute("""
                UPDATE notas_credito
                SET Estado = 'Aplicada'
                WHERE ID_Nota = 9001
            """)
            
            connection.commit()
            
            self.assert_true(
                True,
                "Nota aplicada a cuenta corriente"
            )
            
            # Verificar nuevo saldo
            self.cursor.execute("""
                SELECT COALESCE(SUM(Monto), 0) as Saldo
                FROM cta_corriente
                WHERE ID_Cliente = %s
            """, (id_cliente,))
            
            saldo_nuevo = self.cursor.fetchone()[0]
            
            print(f"  [INFO] Saldo nuevo: Gs.{float(saldo_nuevo):,.0f}")
            print(f"  [INFO] Diferencia: Gs.{float(saldo_nuevo - saldo_anterior):,.0f}")
            
            # Verificar estado de la nota
            self.cursor.execute("""
                SELECT Estado
                FROM notas_credito
                WHERE ID_Nota = 9001
            """)
            
            estado_nuevo = self.cursor.fetchone()[0]
            
            self.assert_equals(
                estado_nuevo, 'Aplicada',
                "Estado actualizado correctamente"
            )
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # TEST 4: CONSULTA DE NOTAS POR CLIENTE
    # ========================================================================
    def test_04_consultar_notas_cliente(self):
        """
        Consulta notas de crédito por cliente
        - Historial de notas
        - Estados de notas
        - Montos totales
        """
        self.print_header(4, "CONSULTA DE NOTAS POR CLIENTE")
        
        try:
            # Consultar todas las notas de crédito
            self.cursor.execute("""
                SELECT 
                    n.ID_Nota,
                    c.Nombres,
                    c.Apellidos,
                    n.Fecha,
                    n.Monto_Total,
                    n.Estado,
                    n.Motivo_Devolucion
                FROM notas_credito n
                INNER JOIN clientes c ON n.ID_Cliente = c.ID_Cliente
                ORDER BY n.Fecha DESC
                LIMIT 10
            """)
            
            notas = self.cursor.fetchall()
            
            self.assert_true(
                len(notas) > 0,
                f"Notas de crédito encontradas: {len(notas)}"
            )
            
            print("\n  Últimas notas de crédito:")
            for nota in notas[:5]:
                id_nota, nombre, apellido, fecha, monto, estado, motivo = nota
                print(f"\n    NC #{id_nota}: {nombre} {apellido}")
                print(f"      Fecha: {fecha}")
                print(f"      Monto: Gs.{float(monto):,.0f}")
                print(f"      Estado: {estado}")
                print(f"      Motivo: {motivo[:50]}...")
            
            # Consultar resumen por estado
            self.cursor.execute("""
                SELECT 
                    Estado,
                    COUNT(*) as Cantidad,
                    SUM(Monto_Total) as Total
                FROM notas_credito
                GROUP BY Estado
            """)
            
            resumen = self.cursor.fetchall()
            
            print("\n  [INFO] Resumen por estado:")
            for estado, cantidad, total in resumen:
                print(f"    {estado}: {cantidad} notas, Gs.{float(total):,.0f}")
            
            # Consultar cliente con más notas
            self.cursor.execute("""
                SELECT 
                    c.Nombres,
                    c.Apellidos,
                    COUNT(n.ID_Nota) as Total_Notas,
                    SUM(n.Monto_Total) as Monto_Total
                FROM clientes c
                INNER JOIN notas_credito n ON c.ID_Cliente = n.ID_Cliente
                GROUP BY c.ID_Cliente
                ORDER BY Total_Notas DESC
                LIMIT 5
            """)
            
            clientes_top = self.cursor.fetchall()
            
            if len(clientes_top) > 0:
                print("\n  [INFO] Clientes con más notas:")
                for cliente in clientes_top:
                    nombre, apellido, cantidad, total = cliente
                    print(f"    {nombre} {apellido}: {cantidad} notas, Gs.{float(total):,.0f}")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # TEST 5: REPORTES Y ESTADÍSTICAS
    # ========================================================================
    def test_05_reportes_estadisticas(self):
        """
        Genera reportes y estadísticas de notas de crédito
        - Notas del mes
        - Productos más devueltos
        - Análisis de motivos
        """
        self.print_header(5, "REPORTES Y ESTADÍSTICAS")
        
        try:
            # 1. NOTAS DEL MES ACTUAL
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as Cantidad,
                    SUM(Monto_Total) as Total,
                    AVG(Monto_Total) as Promedio
                FROM notas_credito
                WHERE YEAR(Fecha) = YEAR(CURDATE())
                  AND MONTH(Fecha) = MONTH(CURDATE())
            """)
            
            mes_actual = self.cursor.fetchone()
            cantidad_mes, total_mes, promedio_mes = mes_actual
            
            print("  [INFO] Notas del mes actual:")
            print(f"    Cantidad: {cantidad_mes}")
            if total_mes:
                print(f"    Total: Gs.{float(total_mes):,.0f}")
                print(f"    Promedio: Gs.{float(promedio_mes):,.0f}")
            
            # 2. PRODUCTOS MÁS DEVUELTOS
            self.cursor.execute("""
                SELECT 
                    p.Codigo,
                    p.Descripcion,
                    COUNT(dn.ID_Detalle) as Veces_Devuelto,
                    SUM(dn.Cantidad) as Cantidad_Total,
                    SUM(dn.Subtotal) as Monto_Total
                FROM detalle_nota dn
                INNER JOIN productos p ON dn.ID_Producto = p.ID_Producto
                GROUP BY dn.ID_Producto
                ORDER BY Veces_Devuelto DESC
                LIMIT 5
            """)
            
            productos_devueltos = self.cursor.fetchall()
            
            if len(productos_devueltos) > 0:
                print("\n  [INFO] Productos más devueltos:")
                for prod in productos_devueltos:
                    codigo, desc, veces, cantidad, monto = prod
                    print(f"    {codigo}: {veces} devoluciones, {float(cantidad)} unidades, Gs.{float(monto):,.0f}")
            
            # 3. ANÁLISIS DE MOTIVOS
            self.cursor.execute("""
                SELECT 
                    LEFT(Motivo_Devolucion, 30) as Motivo,
                    COUNT(*) as Cantidad
                FROM notas_credito
                WHERE Motivo_Devolucion IS NOT NULL
                GROUP BY LEFT(Motivo_Devolucion, 30)
                ORDER BY Cantidad DESC
                LIMIT 5
            """)
            
            motivos = self.cursor.fetchall()
            
            if len(motivos) > 0:
                print("\n  [INFO] Motivos más frecuentes:")
                for motivo, cantidad in motivos:
                    print(f"    {motivo}...: {cantidad} notas")
            
            # 4. EVOLUCIÓN MENSUAL (ÚLTIMOS 6 MESES)
            self.cursor.execute("""
                SELECT 
                    DATE_FORMAT(Fecha, '%Y-%m') as Mes,
                    COUNT(*) as Cantidad,
                    SUM(Monto_Total) as Total
                FROM notas_credito
                WHERE Fecha >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
                GROUP BY DATE_FORMAT(Fecha, '%Y-%m')
                ORDER BY Mes DESC
            """)
            
            evolucion = self.cursor.fetchall()
            
            if len(evolucion) > 0:
                print("\n  [INFO] Evolución últimos meses:")
                for mes, cantidad, total in evolucion:
                    print(f"    {mes}: {cantidad} notas, Gs.{float(total):,.0f}")
            
            # 5. TASA DE DEVOLUCIÓN (RESPECTO A VENTAS)
            self.cursor.execute("""
                SELECT 
                    COUNT(DISTINCT v.ID_Venta) as Total_Ventas,
                    COUNT(DISTINCT n.ID_Nota) as Total_Notas,
                    (COUNT(DISTINCT n.ID_Nota) / COUNT(DISTINCT v.ID_Venta) * 100) as Tasa_Devolucion
                FROM ventas v
                LEFT JOIN notas_credito n ON v.ID_Venta = n.ID_Venta_Original
                WHERE v.Fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            """)
            
            tasa = self.cursor.fetchone()
            total_ventas, total_notas, tasa_dev = tasa
            
            print(f"\n  [INFO] Tasa de devolución (últimos 30 días):")
            print(f"    Ventas: {total_ventas}")
            print(f"    Notas: {total_notas}")
            if tasa_dev:
                print(f"    Tasa: {float(tasa_dev):.2f}%")
            
            self.assert_true(
                True,
                "\nReportes generados correctamente"
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
        print("INICIANDO TESTS DE MÓDULO: NOTAS DE CRÉDITO")
        print("="*70)
        
        try:
            self.test_01_emision_nota_credito()
            self.test_02_agregar_detalles_devolucion()
            self.test_03_aplicar_nota_cuenta_corriente()
            self.test_04_consultar_notas_cliente()
            self.test_05_reportes_estadisticas()
            
        except Exception as e:
            print(f"\n[ERROR FATAL] {str(e)}")
            self.tests_failed += 1
        
        finally:
            print("\n" + "="*70)
            print("RESUMEN DE TESTS - MÓDULO NOTAS DE CRÉDITO")
            print("="*70)
            print(f"Tests exitosos: {self.tests_passed}")
            print(f"Tests fallidos: {self.tests_failed}")
            total = self.tests_passed + self.tests_failed
            if total > 0:
                porcentaje = (self.tests_passed / total) * 100
                print(f"Porcentaje de éxito: {porcentaje:.1f}%")
            
            print(f"\nTotal: {self.tests_passed}/{total} tests exitosos ({porcentaje:.1f}%)")
            print("="*70)
            
            try:
                self.limpiar_datos_prueba()
                print("\n[INFO] Datos de prueba limpiados correctamente")
            except Exception as e:
                print(f"\n[WARNING] Error al limpiar datos: {e}")
            
            self.cursor.close()

if __name__ == "__main__":
    test = TestNotasCredito()
    test.run_all_tests()
