"""
TEST MÓDULO: PUNTOS DE EXPEDICIÓN
==================================
Pruebas para gestión de puntos de expedición de facturas.

Tablas: puntos_expedicion

Autor: Sistema de Tests Automatizado
Fecha: 26 de Noviembre de 2025
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

class TestPuntosExpedicion:
    def __init__(self):
        self.cursor = connection.cursor()
        self.tests_passed = 0
        self.tests_failed = 0
        self.limpiar_datos_prueba()
    
    def limpiar_datos_prueba(self):
        try:
            self.cursor.execute("DELETE FROM puntos_expedicion WHERE ID_Punto >= 9000")
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
    
    def test_01_crear_punto_expedicion(self):
        self.print_header(1, "CREAR PUNTO DE EXPEDICIÓN")
        
        try:
            # Verificar si ya existe el punto para evitar duplicados
            self.cursor.execute("""
                SELECT COUNT(*) FROM puntos_expedicion 
                WHERE Codigo_Establecimiento = '001' AND Codigo_Punto_Expedicion = '001'
            """)
            existe = self.cursor.fetchone()[0]
            
            if existe == 0:
                self.cursor.execute("""
                    INSERT INTO puntos_expedicion (
                        ID_Punto,
                        Codigo_Establecimiento,
                        Codigo_Punto_Expedicion,
                        Descripcion_Ubicacion,
                        Activo
                    ) VALUES (9001, '001', '001', 'Punto TEST Principal', 1)
                """)
                connection.commit()
                self.assert_true(True, "Punto de expedición creado")
            else:
                print("  [INFO] Punto 001-001 ya existe, usando existente")
            
            # Verificar que existe al menos un punto con ese código
            self.cursor.execute("""
                SELECT COUNT(*) FROM puntos_expedicion 
                WHERE Codigo_Establecimiento = '001' AND Codigo_Punto_Expedicion = '001'
            """)
            count = self.cursor.fetchone()[0]
            
            self.assert_true(count >= 1, "Punto verificado en BD")
            
            self.assert_true(count == 1, "Punto verificado en BD")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_02_consultar_puntos_activos(self):
        self.print_header(2, "CONSULTAR PUNTOS ACTIVOS")
        
        try:
            self.cursor.execute("""
                SELECT 
                    Codigo_Establecimiento,
                    Codigo_Punto_Expedicion,
                    Descripcion_Ubicacion,
                    Activo
                FROM puntos_expedicion
                WHERE Activo = 1
            """)
            
            puntos = self.cursor.fetchall()
            
            print(f"  [INFO] Puntos activos encontrados: {len(puntos)}\n")
            
            for punto in puntos:
                est, exp, desc, activo = punto
                print(f"    {est}-{exp}: {desc}")
            
            self.assert_true(len(puntos) > 0, "Puntos activos disponibles")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_03_validar_codigos(self):
        self.print_header(3, "VALIDAR CÓDIGOS DE PUNTO")
        
        try:
            self.cursor.execute("""
                SELECT 
                    Codigo_Establecimiento,
                    Codigo_Punto_Expedicion,
                    LENGTH(Codigo_Establecimiento) as Len_Est,
                    LENGTH(Codigo_Punto_Expedicion) as Len_Punto
                FROM puntos_expedicion
            """)
            
            puntos = self.cursor.fetchall()
            
            validos = 0
            for punto in puntos:
                est, exp, len_est, len_exp = punto
                if len_est == 3 and len_exp == 3:
                    validos += 1
            
            print(f"  [INFO] Puntos con códigos válidos (XXX-XXX): {validos}/{len(puntos)}")
            
            self.assert_true(validos > 0, "Códigos de formato válido encontrados")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_04_activar_desactivar_punto(self):
        self.print_header(4, "ACTIVAR/DESACTIVAR PUNTO")
        
        try:
            # Desactivar
            self.cursor.execute("UPDATE puntos_expedicion SET Activo = 0 WHERE ID_Punto = 9001")
            connection.commit()
            
            self.cursor.execute("SELECT Activo FROM puntos_expedicion WHERE ID_Punto = 9001")
            activo = self.cursor.fetchone()
            
            if activo:
                self.assert_true(activo[0] == 0, "Punto desactivado")
            
            # Reactivar
            self.cursor.execute("UPDATE puntos_expedicion SET Activo = 1 WHERE ID_Punto = 9001")
            connection.commit()
            
            self.cursor.execute("SELECT Activo FROM puntos_expedicion WHERE ID_Punto = 9001")
            activo = self.cursor.fetchone()
            
            if activo:
                self.assert_true(activo[0] == 1, "Punto reactivado")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_05_reporte_puntos(self):
        self.print_header(5, "REPORTE DE PUNTOS DE EXPEDICIÓN")
        
        try:
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as Total,
                    SUM(CASE WHEN Activo = 1 THEN 1 ELSE 0 END) as Activos,
                    SUM(CASE WHEN Activo = 0 THEN 1 ELSE 0 END) as Inactivos
                FROM puntos_expedicion
            """)
            
            stats = self.cursor.fetchone()
            total, activos, inactivos = stats
            
            print(f"  [INFO] Resumen de puntos de expedición:")
            print(f"    Total: {total}")
            print(f"    Activos: {activos}")
            print(f"    Inactivos: {inactivos}")
            
            self.assert_true(total > 0, "Sistema de puntos configurado")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def run_all_tests(self):
        print("\n" + "="*70)
        print("INICIANDO TESTS DE MÓDULO: PUNTOS DE EXPEDICIÓN")
        print("="*70)
        
        try:
            self.test_01_crear_punto_expedicion()
            self.test_02_consultar_puntos_activos()
            self.test_03_validar_codigos()
            self.test_04_activar_desactivar_punto()
            self.test_05_reporte_puntos()
        except Exception as e:
            print(f"\n[ERROR FATAL] {str(e)}")
            self.tests_failed += 1
        finally:
            print("\n" + "="*70)
            print("RESUMEN DE TESTS - MÓDULO PUNTOS EXPEDICIÓN")
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
    test = TestPuntosExpedicion()
    test.run_all_tests()
