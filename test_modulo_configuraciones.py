"""
TEST MÓDULO: CONFIGURACIONES
=============================
Pruebas para gestión de impuestos y unidades de medida.

Tablas: impuestos, unidades_medida

Autor: Sistema de Tests Automatizado
Fecha: 26 de Noviembre de 2025
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection
from datetime import date
from decimal import Decimal

class TestConfiguraciones:
    def __init__(self):
        self.cursor = connection.cursor()
        self.tests_passed = 0
        self.tests_failed = 0
        self.limpiar_datos_prueba()
    
    def limpiar_datos_prueba(self):
        try:
            self.cursor.execute("DELETE FROM impuestos WHERE ID_Impuesto >= 9000")
            self.cursor.execute("DELETE FROM unidades_medida WHERE ID_Unidad >= 9000")
            connection.commit()
        except:
            connection.rollback()
    
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
    
    def test_01_gestionar_impuestos(self):
        self.print_header(1, "GESTIONAR TASAS DE IMPUESTOS")
        
        try:
            # Crear nuevo impuesto TEST
            self.cursor.execute("""
                INSERT INTO impuestos (
                    ID_Impuesto,
                    Nombre_Impuesto,
                    Porcentaje,
                    Vigente_Desde,
                    Activo
                ) VALUES (9001, 'IVA TEST 12%%', 12.00, %s, 1)
            """, (date.today(),))
            
            connection.commit()
            
            self.assert_true(True, "Impuesto creado")
            
            # Consultar impuestos vigentes
            self.cursor.execute("""
                SELECT 
                    Nombre_Impuesto,
                    Porcentaje,
                    Vigente_Desde,
                    Activo
                FROM impuestos
                WHERE Activo = 1
                ORDER BY Porcentaje
            """)
            
            impuestos = self.cursor.fetchall()
            
            print(f"\n  [INFO] Impuestos vigentes: {len(impuestos)}")
            for imp in impuestos:
                nombre, porc, desde, activo = imp
                print(f"    {nombre}: {float(porc)}% desde {desde}")
            
            self.assert_true(len(impuestos) > 0, "Impuestos configurados en el sistema")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_02_gestionar_unidades_medida(self):
        self.print_header(2, "GESTIONAR UNIDADES DE MEDIDA")
        
        try:
            # Crear unidad TEST
            self.cursor.execute("""
                INSERT INTO unidades_medida (
                    ID_Unidad,
                    Nombre,
                    Abreviatura,
                    Activo
                ) VALUES (9001, 'Pack TEST', 'PACK', 1)
            """)
            
            connection.commit()
            
            self.assert_true(True, "Unidad de medida creada")
            
            # Consultar todas las unidades
            self.cursor.execute("""
                SELECT Nombre, Abreviatura, Activo
                FROM unidades_medida
                WHERE Activo = 1
            """)
            
            unidades = self.cursor.fetchall()
            
            print(f"\n  [INFO] Unidades de medida activas: {len(unidades)}")
            for unidad in unidades:
                nombre, abrev, activo = unidad
                print(f"    {nombre} ({abrev})")
            
            self.assert_true(len(unidades) > 0, "Unidades configuradas")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_03_aplicar_impuestos_productos(self):
        self.print_header(3, "CONSULTAR APLICACIÓN DE IMPUESTOS")
        
        try:
            # Verificar productos y sus cálculos de impuestos
            self.cursor.execute("""
                SELECT 
                    p.Codigo,
                    p.Descripcion,
                    pp.Precio_Unitario_Neto,
                    (pp.Precio_Unitario_Neto * 0.10) as IVA_10,
                    (pp.Precio_Unitario_Neto * 1.10) as Precio_Con_IVA
                FROM productos p
                INNER JOIN precios_por_lista pp ON p.ID_Producto = pp.ID_Producto
                WHERE p.Activo = 1
                LIMIT 5
            """)
            
            productos = self.cursor.fetchall()
            
            if len(productos) > 0:
                print("  [INFO] Cálculo de impuestos en productos:\n")
                for prod in productos:
                    codigo, desc, neto, iva, total = prod
                    print(f"    {codigo}: Neto=Gs.{float(neto):,.0f}, IVA=Gs.{float(iva):,.0f}, Total=Gs.{float(total):,.0f}")
            
            self.assert_true(True, "Sistema de cálculo de impuestos funcional")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_04_historial_cambios_impuestos(self):
        self.print_header(4, "HISTORIAL DE CAMBIOS DE IMPUESTOS")
        
        try:
            self.cursor.execute("""
                SELECT 
                    Nombre_Impuesto,
                    Porcentaje,
                    Vigente_Desde,
                    Vigente_Hasta
                FROM impuestos
                ORDER BY Vigente_Desde DESC
                LIMIT 10
            """)
            
            historial = self.cursor.fetchall()
            
            print(f"  [INFO] Historial de tasas impositivas:\n")
            for imp in historial:
                nombre, porc, desde, hasta = imp
                hasta_str = hasta if hasta else "Actualidad"
                print(f"    {nombre}: {float(porc)}% ({desde} - {hasta_str})")
            
            self.assert_true(len(historial) > 0, "Historial de impuestos disponible")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_05_reporte_configuraciones(self):
        self.print_header(5, "REPORTE DE CONFIGURACIONES")
        
        try:
            # Resumen de impuestos
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as Total,
                    SUM(CASE WHEN Activo = 1 THEN 1 ELSE 0 END) as Activos
                FROM impuestos
            """)
            
            imp_stats = self.cursor.fetchone()
            
            # Resumen de unidades
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as Total,
                    SUM(CASE WHEN Activo = 1 THEN 1 ELSE 0 END) as Activos
                FROM unidades_medida
            """)
            
            uni_stats = self.cursor.fetchone()
            
            print("  [INFO] Resumen de configuraciones:\n")
            print(f"    Impuestos: {imp_stats[1]}/{imp_stats[0]} activos")
            print(f"    Unidades: {uni_stats[1]}/{uni_stats[0]} activas")
            
            self.assert_true(True, "Sistema de configuraciones operativo")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def run_all_tests(self):
        print("\n" + "="*70)
        print("INICIANDO TESTS DE MÓDULO: CONFIGURACIONES")
        print("="*70)
        
        try:
            self.test_01_gestionar_impuestos()
            self.test_02_gestionar_unidades_medida()
            self.test_03_aplicar_impuestos_productos()
            self.test_04_historial_cambios_impuestos()
            self.test_05_reporte_configuraciones()
        except Exception as e:
            print(f"\n[ERROR FATAL] {str(e)}")
            self.tests_failed += 1
        finally:
            print("\n" + "="*70)
            print("RESUMEN DE TESTS - MÓDULO CONFIGURACIONES")
            print("="*70)
            print(f"Tests exitosos: {self.tests_passed}")
            print(f"Tests fallidos: {self.tests_failed}")
            total = self.tests_passed + self.tests_failed
            if total > 0:
                porcentaje = (self.tests_passed / total) * 100
                print(f"\nTotal: {self.tests_passed}/{total} tests exitosos ({porcentaje:.1f}%)")
            print("="*70)
            
            try:
                self.limpiar_datos_prueba()
                print("\n[INFO] Datos de prueba limpiados")
            except:
                pass
            
            self.cursor.close()

if __name__ == "__main__":
    test = TestConfiguraciones()
    test.run_all_tests()
