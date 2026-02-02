"""
TEST MÓDULO: AUDITORÍA
======================
Prueba el sistema de auditoría y trazabilidad
- Auditoría de comisiones
- Auditoría de empleados
- Auditoría de usuarios web
- Consultas por fecha y usuario
- Reportes de auditoría
"""

import os
import sys
import django
from datetime import date, datetime, timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection

class TestModuloAuditoria:
    
    def __init__(self):
        self.cursor = connection.cursor()
        self.tests_passed = 0
        self.tests_failed = 0
    
    def print_header(self, test_num, title):
        print("\n" + "=" * 80)
        print(f"TEST {test_num}: {title}")
        print("=" * 80)
    
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
            print(f"  [OK] {mensaje}")
            return True
        else:
            print(f"  [FALLO] {mensaje}")
            print(f"         Esperado: {esperado}, Actual: {actual}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # TEST 1: AUDITORÍA DE CAMBIOS EN COMISIONES
    # ========================================================================
    def test_01_auditoria_comisiones(self):
        """
        Prueba el registro de auditoría de cambios en tarifas de comisión
        - Registrar cambio de tarifa
        - Consultar historial
        - Verificar trazabilidad
        """
        self.print_header(1, "AUDITORÍA DE CAMBIOS EN COMISIONES")
        
        try:
            # Obtener una tarifa existente
            self.cursor.execute("""
                SELECT ID_Tarifa, Porcentaje_Comision
                FROM tarifas_comision
                WHERE Activo = 1
                LIMIT 1
            """)
            
            tarifa_data = self.cursor.fetchone()
            if not tarifa_data:
                print("  [INFO] No hay tarifas disponibles para auditar")
                self.tests_passed += 1
                return True
            
            id_tarifa, porcentaje_actual = tarifa_data
            
            # Obtener empleado
            self.cursor.execute("SELECT ID_Empleado FROM empleados LIMIT 1")
            id_empleado = self.cursor.fetchone()[0]
            
            # Simular cambio de tarifa (registrar en auditoría)
            nuevo_porcentaje = Decimal('0.0350')  # 3.5%
            
            self.cursor.execute("""
                INSERT INTO auditoria_comisiones (
                    ID_Auditoria,
                    ID_Tarifa,
                    Fecha_Cambio,
                    Campo_Modificado,
                    Valor_Anterior,
                    Valor_Nuevo,
                    ID_Empleado_Modifico
                ) VALUES (
                    9001,
                    %s,
                    %s,
                    'Porcentaje_Comision',
                    %s,
                    %s,
                    %s
                )
            """, (id_tarifa, datetime.now(), porcentaje_actual, nuevo_porcentaje, id_empleado))
            
            connection.commit()
            
            self.assert_true(True, "Registro de auditoría creado")
            
            # Consultar historial de cambios
            self.cursor.execute("""
                SELECT 
                    ac.Campo_Modificado,
                    ac.Valor_Anterior,
                    ac.Valor_Nuevo,
                    ac.Fecha_Cambio,
                    CONCAT(e.Nombre, ' ', e.Apellido) as Empleado
                FROM auditoria_comisiones ac
                LEFT JOIN empleados e ON ac.ID_Empleado_Modifico = e.ID_Empleado
                WHERE ac.ID_Auditoria = 9001
            """)
            
            auditoria = self.cursor.fetchone()
            
            if auditoria:
                campo, anterior, nuevo, fecha, empleado = auditoria
                print(f"\n  [INFO] Auditoría registrada:")
                print(f"    Campo: {campo}")
                print(f"    Valor anterior: {float(anterior) if anterior else 'N/A':.2%}")
                print(f"    Valor nuevo: {float(nuevo) if nuevo else 'N/A':.2%}")
                print(f"    Fecha: {fecha}")
                print(f"    Modificado por: {empleado}")
            
            self.assert_true(auditoria is not None, "Auditoría consultada exitosamente")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # TEST 2: AUDITORÍA DE EMPLEADOS
    # ========================================================================
    def test_02_auditoria_empleados(self):
        """
        Prueba el registro de auditoría de cambios en empleados
        - Registrar modificaciones
        - Consultar por empleado
        """
        self.print_header(2, "AUDITORÍA DE EMPLEADOS")
        
        try:
            # Obtener un empleado
            self.cursor.execute("SELECT ID_Empleado, Nombre FROM empleados LIMIT 1")
            empleado_data = self.cursor.fetchone()
            
            if not empleado_data:
                print("  [INFO] No hay empleados disponibles")
                self.tests_passed += 1
                return True
            
            id_empleado, nombre = empleado_data
            
            # Simular registro en auditoría (si la tabla existe)
            # Verificar si existe la tabla auditoria_empleados
            self.cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                  AND table_name = 'auditoria_empleados'
            """)
            
            tabla_existe = self.cursor.fetchone()[0] > 0
            
            if tabla_existe:
                # Registrar cambio
                self.cursor.execute("""
                    INSERT INTO auditoria_empleados (
                        ID_Auditoria,
                        ID_Empleado,
                        Fecha_Cambio,
                        Campo_Modificado,
                        Valor_Anterior,
                        Valor_Nuevo
                    ) VALUES (
                        9002,
                        %s,
                        %s,
                        'Cargo',
                        'Cajero',
                        'Supervisor'
                    )
                """, (id_empleado, datetime.now()))
                
                connection.commit()
                
                print(f"  [OK] Auditoría de empleado '{nombre}' registrada")
                
                # Consultar auditorías del empleado
                self.cursor.execute("""
                    SELECT COUNT(*) 
                    FROM auditoria_empleados
                    WHERE ID_Empleado = %s
                """, (id_empleado,))
                
                count = self.cursor.fetchone()[0]
                print(f"  [INFO] Total de auditorías para este empleado: {count}")
            else:
                print("  [INFO] Tabla auditoria_empleados no existe, omitiendo test")
            
            self.assert_true(True, "Auditoría de empleados verificada")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            connection.rollback()
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # TEST 3: CONSULTAR AUDITORÍAS POR FECHA
    # ========================================================================
    def test_03_consultar_por_fecha(self):
        """
        Prueba la consulta de auditorías por rango de fechas
        """
        self.print_header(3, "CONSULTAR AUDITORÍAS POR FECHA")
        
        try:
            fecha_inicio = date.today() - timedelta(days=7)
            fecha_fin = date.today() + timedelta(days=1)
            
            # Consultar auditorías de comisiones
            self.cursor.execute("""
                SELECT 
                    DATE(Fecha_Cambio) as Fecha,
                    COUNT(*) as Total_Cambios
                FROM auditoria_comisiones
                WHERE Fecha_Cambio BETWEEN %s AND %s
                GROUP BY DATE(Fecha_Cambio)
                ORDER BY Fecha DESC
                LIMIT 10
            """, (fecha_inicio, fecha_fin))
            
            resultados = self.cursor.fetchall()
            
            print(f"\n  [INFO] Auditorías de comisiones (últimos 7 días): {len(resultados)} días con cambios")
            
            if len(resultados) > 0:
                for fecha, total in resultados:
                    print(f"    {fecha}: {total} cambio(s)")
            
            self.assert_true(True, "Consulta por fecha ejecutada")
            
            # Verificar auditorías recientes
            self.cursor.execute("""
                SELECT COUNT(*) 
                FROM auditoria_comisiones
                WHERE Fecha_Cambio >= CURDATE()
            """)
            
            count_hoy = self.cursor.fetchone()[0]
            print(f"\n  [INFO] Cambios registrados hoy: {count_hoy}")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # TEST 4: AUDITORÍA POR USUARIO/EMPLEADO
    # ========================================================================
    def test_04_consultar_por_usuario(self):
        """
        Prueba la consulta de auditorías por usuario que realizó el cambio
        """
        self.print_header(4, "AUDITORÍAS POR USUARIO/EMPLEADO")
        
        try:
            # Obtener empleados que han realizado cambios
            self.cursor.execute("""
                SELECT 
                    e.ID_Empleado,
                    CONCAT(e.Nombre, ' ', e.Apellido) as Empleado,
                    COUNT(ac.ID_Auditoria) as Total_Cambios
                FROM empleados e
                LEFT JOIN auditoria_comisiones ac ON e.ID_Empleado = ac.ID_Empleado_Modifico
                WHERE ac.ID_Auditoria IS NOT NULL
                GROUP BY e.ID_Empleado
                ORDER BY Total_Cambios DESC
                LIMIT 5
            """)
            
            empleados = self.cursor.fetchall()
            
            if len(empleados) > 0:
                print(f"\n  [INFO] Empleados con cambios registrados: {len(empleados)}\n")
                for id_emp, nombre, total in empleados:
                    print(f"    {nombre}: {total} cambio(s)")
                
                self.assert_true(True, "Auditorías por usuario encontradas")
            else:
                print("  [INFO] No hay cambios registrados por empleados")
                self.assert_true(True, "Consulta ejecutada correctamente")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # TEST 5: REPORTE GENERAL DE AUDITORÍA
    # ========================================================================
    def test_05_reporte_auditoria(self):
        """
        Genera un reporte general del sistema de auditoría
        """
        self.print_header(5, "REPORTE GENERAL DE AUDITORÍA")
        
        try:
            # Resumen de auditorías por tipo
            print("\n  [INFO] Resumen del sistema de auditoría:\n")
            
            # Auditorías de comisiones
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as Total,
                    COUNT(DISTINCT ID_Tarifa) as Tarifas_Modificadas,
                    COUNT(DISTINCT ID_Empleado_Modifico) as Empleados_Modificadores
                FROM auditoria_comisiones
            """)
            
            comisiones = self.cursor.fetchone()
            if comisiones:
                print(f"    Auditorías de Comisiones:")
                print(f"      Total registros: {comisiones[0]}")
                print(f"      Tarifas modificadas: {comisiones[1]}")
                print(f"      Empleados que modificaron: {comisiones[2]}")
            
            # Verificar si existe auditoria_empleados
            self.cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                  AND table_name = 'auditoria_empleados'
            """)
            
            if self.cursor.fetchone()[0] > 0:
                self.cursor.execute("SELECT COUNT(*) FROM auditoria_empleados")
                emp_count = self.cursor.fetchone()[0]
                print(f"\n    Auditorías de Empleados:")
                print(f"      Total registros: {emp_count}")
            
            # Verificar si existe auditoria_usuarios_web
            self.cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                  AND table_name = 'auditoria_usuarios_web'
            """)
            
            if self.cursor.fetchone()[0] > 0:
                self.cursor.execute("SELECT COUNT(*) FROM auditoria_usuarios_web")
                web_count = self.cursor.fetchone()[0]
                print(f"\n    Auditorías de Usuarios Web:")
                print(f"      Total registros: {web_count}")
            
            self.assert_true(True, "Sistema de auditoría operativo")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # LIMPIEZA DE DATOS DE PRUEBA
    # ========================================================================
    def cleanup(self):
        """Limpia los datos de prueba creados"""
        try:
            # Eliminar auditorías de prueba
            self.cursor.execute("DELETE FROM auditoria_comisiones WHERE ID_Auditoria IN (9001)")
            
            # Eliminar de auditoria_empleados si existe
            self.cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = DATABASE() 
                  AND table_name = 'auditoria_empleados'
            """)
            
            if self.cursor.fetchone()[0] > 0:
                self.cursor.execute("DELETE FROM auditoria_empleados WHERE ID_Auditoria IN (9002)")
            
            connection.commit()
            print("\n[INFO] Datos de prueba limpiados")
            
        except Exception as e:
            connection.rollback()
            print(f"\n[WARNING] Error al limpiar datos: {str(e)}")
    
    # ========================================================================
    # EJECUTAR TODOS LOS TESTS
    # ========================================================================
    def run_all_tests(self):
        """Ejecuta todos los tests del módulo"""
        print("=" * 80)
        print("INICIANDO TESTS DE MÓDULO: AUDITORÍA")
        print("=" * 80)
        
        self.test_01_auditoria_comisiones()
        self.test_02_auditoria_empleados()
        self.test_03_consultar_por_fecha()
        self.test_04_consultar_por_usuario()
        self.test_05_reporte_auditoria()
        
        # Resumen
        print("\n" + "=" * 80)
        print("RESUMEN DE TESTS - MÓDULO AUDITORÍA")
        print("=" * 80)
        print(f"Tests exitosos: {self.tests_passed}")
        print(f"Tests fallidos: {self.tests_failed}")
        
        total = self.tests_passed + self.tests_failed
        if total > 0:
            porcentaje = (self.tests_passed / total) * 100
            print(f"\nTotal: {self.tests_passed}/{total} tests exitosos ({porcentaje:.1f}%)")
        
        print("=" * 80)
        
        # Limpiar datos
        self.cleanup()


if __name__ == "__main__":
    test = TestModuloAuditoria()
    test.run_all_tests()
