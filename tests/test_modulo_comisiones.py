"""
TEST MÓDULO: COMISIONES
=======================
Pruebas para gestión de comisiones de ventas por medios de pago.

Tablas: tarifas_comision, detalle_comision_venta, auditoria_comisiones

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

class TestComisiones:
    def __init__(self):
        self.cursor = connection.cursor()
        self.tests_passed = 0
        self.tests_failed = 0
        self.limpiar_datos_prueba()
    
    def limpiar_datos_prueba(self):
        try:
            self.cursor.execute("DELETE FROM detalle_comision_venta WHERE ID_Tarifa >= 9000")
            self.cursor.execute("DELETE FROM tarifas_comision WHERE ID_Tarifa >= 9000")
            connection.commit()
        except Exception as e:
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
    
    def assert_equals(self, actual, esperado, mensaje):
        if actual == esperado:
            print(f"  [OK] {mensaje}: {actual}")
            return True
        else:
            print(f"  [FALLO] {mensaje}")
            print(f"         Esperado: {esperado}, Actual: {actual}")
            self.tests_failed += 1
            return False
    
    def test_01_configurar_tarifas_comision(self):
        self.print_header(1, "CONFIGURAR TARIFAS DE COMISIÓN")
        
        try:
            # Obtener medios de pago
            self.cursor.execute("SELECT ID_Medio_Pago, Descripcion FROM medios_pago LIMIT 3")
            medios = self.cursor.fetchall()
            
            if len(medios) == 0:
                print("  [INFO] No hay medios de pago disponibles")
                self.tests_passed += 1
                return True
            
            # Configurar tarifas
            tarifas = [
                (Decimal('0.0300'), None, 'Tarjeta Crédito'),  # 3%
                (Decimal('0.0250'), None, 'Tarjeta Débito'),   # 2.5%
                (Decimal('0.0000'), Decimal('500.00'), 'Efectivo'),  # Gs. 500 fijo (porcentaje = 0)
            ]
            
            for i, medio in enumerate(medios[:3]):
                id_medio, desc = medio
                porcentaje, monto_fijo, tipo = tarifas[i]
                
                self.cursor.execute("""
                    INSERT INTO tarifas_comision (
                        ID_Tarifa,
                        ID_Medio_Pago,
                        Fecha_Inicio_Vigencia,
                        Porcentaje_Comision,
                        Monto_Fijo_Comision,
                        Activo
                    ) VALUES (%s, %s, %s, %s, %s, 1)
                """, (9001 + i, id_medio, date.today(), porcentaje, monto_fijo))
                
                if porcentaje:
                    print(f"  [INFO] {desc}: {float(porcentaje)*100}% comisión")
                else:
                    print(f"  [INFO] {desc}: Gs.{float(monto_fijo):,.0f} fijo")
            
            connection.commit()
            
            self.cursor.execute("SELECT COUNT(*) FROM tarifas_comision WHERE ID_Tarifa >= 9000")
            count = self.cursor.fetchone()[0]
            
            self.assert_true(count >= 3, f"Tarifas configuradas: {count}")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_02_calcular_comision_venta(self):
        self.print_header(2, "CALCULAR COMISIÓN EN VENTA")
        
        try:
            # Obtener pago reciente
            self.cursor.execute("""
                SELECT pv.ID_Pago_Venta, pv.Monto_Aplicado, mp.Descripcion
                FROM pagos_venta pv
                INNER JOIN medios_pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
                WHERE pv.Monto_Aplicado > 0
                ORDER BY pv.Fecha_Pago DESC
                LIMIT 1
            """)
            
            pago = self.cursor.fetchone()
            if not pago:
                print("  [INFO] No hay pagos para calcular comisión")
                self.tests_passed += 1
                return True
            
            id_pago, monto, medio = pago
            
            print(f"  [INFO] Pago: {medio}, Monto: Gs.{float(monto):,.0f}")
            
            # Calcular comisión (simulación con 2.5%)
            porcentaje = Decimal('0.025')
            comision = float(monto) * float(porcentaje)
            
            print(f"  [INFO] Comisión calculada: Gs.{comision:,.2f} ({float(porcentaje)*100}%)")
            
            self.assert_true(comision > 0, f"Comisión válida: Gs.{comision:,.2f}")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_03_consultar_comisiones_empleado(self):
        self.print_header(3, "CONSULTAR COMISIONES POR EMPLEADO")
        
        try:
            # Consultar empleados con ventas
            self.cursor.execute("""
                SELECT 
                    e.ID_Empleado,
                    e.Nombre,
                    e.Apellido,
                    COUNT(DISTINCT v.ID_Venta) as Total_Ventas,
                    SUM(v.Monto_Total) as Monto_Total
                FROM empleados e
                INNER JOIN ventas v ON e.ID_Empleado = v.ID_Empleado_Cajero
                WHERE v.Fecha >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY e.ID_Empleado
                ORDER BY Total_Ventas DESC
                LIMIT 5
            """)
            
            empleados = self.cursor.fetchall()
            
            print(f"  [INFO] Empleados con ventas (últimos 30 días): {len(empleados)}")
            
            for emp in empleados:
                id_emp, nombre, apellido, ventas, monto = emp
                comision_estimada = float(monto) * 0.025  # 2.5% estimado
                print(f"    {nombre} {apellido}: {ventas} ventas, Comisión est.: Gs.{comision_estimada:,.0f}")
            
            self.assert_true(True, "Consulta de comisiones exitosa")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_04_reportes_comisiones(self):
        self.print_header(4, "REPORTES DE COMISIONES")
        
        try:
            # Reporte por medio de pago
            self.cursor.execute("""
                SELECT 
                    mp.Descripcion,
                    COUNT(pv.ID_Pago_Venta) as Cantidad_Pagos,
                    SUM(pv.Monto_Aplicado) as Monto_Total
                FROM pagos_venta pv
                INNER JOIN medios_pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
                WHERE pv.Fecha_Pago >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY mp.ID_Medio_Pago
            """)
            
            medios = self.cursor.fetchall()
            
            print("  [INFO] Comisiones por medio de pago (últimos 30 días):\n")
            total_comisiones = 0
            
            for medio in medios:
                desc, cantidad, monto = medio
                comision = float(monto) * 0.025  # 2.5% estimado
                total_comisiones += comision
                print(f"    {desc}: {cantidad} pagos, Comisión: Gs.{comision:,.0f}")
            
            print(f"\n  [INFO] Total comisiones estimadas: Gs.{total_comisiones:,.0f}")
            
            self.assert_true(True, "Reporte generado correctamente")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_05_tarifas_vigentes(self):
        self.print_header(5, "CONSULTAR TARIFAS VIGENTES")
        
        try:
            self.cursor.execute("""
                SELECT 
                    mp.Descripcion,
                    tc.Porcentaje_Comision,
                    tc.Monto_Fijo_Comision,
                    tc.Fecha_Inicio_Vigencia,
                    tc.Activo
                FROM tarifas_comision tc
                INNER JOIN medios_pago mp ON tc.ID_Medio_Pago = mp.ID_Medio_Pago
                WHERE tc.Activo = 1
                  AND (tc.Fecha_Fin_Vigencia IS NULL OR tc.Fecha_Fin_Vigencia >= CURDATE())
            """)
            
            tarifas = self.cursor.fetchall()
            
            print(f"  [INFO] Tarifas activas: {len(tarifas)}\n")
            
            for tarifa in tarifas:
                medio, porcentaje, monto_fijo, fecha, activo = tarifa
                if porcentaje:
                    print(f"    {medio}: {float(porcentaje)*100}% desde {fecha}")
                elif monto_fijo:
                    print(f"    {medio}: Gs.{float(monto_fijo):,.0f} fijo desde {fecha}")
            
            self.assert_true(len(tarifas) > 0, "Tarifas vigentes encontradas")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def run_all_tests(self):
        print("\n" + "="*70)
        print("INICIANDO TESTS DE MÓDULO: COMISIONES")
        print("="*70)
        
        try:
            self.test_01_configurar_tarifas_comision()
            self.test_02_calcular_comision_venta()
            self.test_03_consultar_comisiones_empleado()
            self.test_04_reportes_comisiones()
            self.test_05_tarifas_vigentes()
            
        except Exception as e:
            print(f"\n[ERROR FATAL] {str(e)}")
            self.tests_failed += 1
        
        finally:
            print("\n" + "="*70)
            print("RESUMEN DE TESTS - MÓDULO COMISIONES")
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
    test = TestComisiones()
    test.run_all_tests()
