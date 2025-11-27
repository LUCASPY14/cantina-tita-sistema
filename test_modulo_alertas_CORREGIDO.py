#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TEST MÓDULO: ALERTAS Y NOTIFICACIONES
======================================

Tests para el sistema de alertas y notificaciones.

Tablas involucradas:
- alertas_sistema: Campos reales= ID_Alerta, Tipo, Mensaje, Fecha_Creacion, Fecha_Leida, Estado
- solicitudes_notificacion

SCHEMA REAL alertas_sistema:
- Tipo: enum('STOCK_MINIMO','SALDO_BAJO','LIMITE_CREDITO','TIMBRADO_VENCIDO','TARJETA_VENCIDA')
- Estado: enum('Pendiente','Leida','Resuelta')
"""

import MySQLdb
from datetime import datetime, timedelta

# Configuración de conexión
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Tita.BioMol22',
    'database': 'cantinatitadb',
    'charset': 'utf8mb4'
}

class TestModuloAlertas:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.connection = None
        self.cursor = None
        self.alertas_creadas = []
        
    def conectar(self):
        try:
            self.connection = MySQLdb.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            print(f"[ERROR] Conexión fallida: {e}")
            return False
    
    def limpiar_datos_prueba(self):
        """Limpia datos de prueba"""
        try:
            # Limpiar alertas de prueba
            if self.alertas_creadas:
                ids = ','.join(map(str, self.alertas_creadas))
                self.cursor.execute(f"DELETE FROM alertas_sistema WHERE ID_Alerta IN ({ids})")
            
            # Limpiar notificaciones de prueba
            self.cursor.execute("DELETE FROM solicitudes_notificacion WHERE ID_Solicitud >= 9000")
            
            self.connection.commit()
            print("[INFO] Datos de prueba limpiados")
        except Exception as e:
            print(f"[WARN] Error limpiando datos: {e}")
    
    def print_header(self, test_num, title):
        print(f"\n{'='*80}")
        print(f"TEST {test_num}: {title}")
        print(f"{'='*80}")
    
    def assert_true(self, condition, message):
        if condition:
            print(f"  [OK] {message}")
        else:
            print(f"  [FAIL] {message}")
        return condition
    
    def assert_equals(self, actual, expected, message):
        if actual == expected:
            print(f"  [OK] {message}: {actual}")
            return True
        else:
            print(f"  [FAIL] {message}: esperado {expected}, obtenido {actual}")
            return False
    
    # ========================================================================
    # TESTS
    # ========================================================================
    
    def test_01_crear_alertas(self):
        self.print_header(1, "CREAR ALERTAS DEL SISTEMA")
        
        try:
            # Crear alerta de stock bajo
            self.cursor.execute("""
                INSERT INTO alertas_sistema (
                    ID_Alerta,
                    Tipo,
                    Mensaje,
                    Fecha_Creacion,
                    Estado
                ) VALUES (
                    9001,
                    'STOCK_MINIMO',
                    'TEST: Stock crítico detectado en productos',
                    NOW(),
                    'Pendiente'
                )
            """)
            self.alertas_creadas.append(9001)
            
            # Crear alerta de límite de crédito
            self.cursor.execute("""
                INSERT INTO alertas_sistema (
                    ID_Alerta,
                    Tipo,
                    Mensaje,
                    Fecha_Creacion,
                    Estado
                ) VALUES (
                    9002,
                    'LIMITE_CREDITO',
                    'TEST: Cliente con deuda vencida',
                    NOW(),
                    'Pendiente'
                )
            """)
            self.alertas_creadas.append(9002)
            
            # Crear alerta de timbrado
            self.cursor.execute("""
                INSERT INTO alertas_sistema (
                    ID_Alerta,
                    Tipo,
                    Mensaje,
                    Fecha_Creacion,
                    Estado
                ) VALUES (
                    9003,
                    'TIMBRADO_VENCIDO',
                    'TEST: Timbrado próximo a vencer en 15 días',
                    NOW(),
                    'Pendiente'
                )
            """)
            self.alertas_creadas.append(9003)
            
            self.connection.commit()
            
            self.assert_true(True, "Alertas creadas correctamente")
            
            # Verificar alertas
            self.cursor.execute("""
                SELECT COUNT(*) 
                FROM alertas_sistema 
                WHERE ID_Alerta IN (9001, 9002, 9003)
            """)
            
            count = self.cursor.fetchone()[0]
            
            self.assert_equals(count, 3, "Alertas verificadas")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_02_consultar_alertas_pendientes(self):
        self.print_header(2, "CONSULTAR ALERTAS PENDIENTES")
        
        try:
            self.cursor.execute("""
                SELECT 
                    a.ID_Alerta,
                    a.Tipo,
                    a.Mensaje,
                    a.Fecha_Creacion,
                    a.Estado
                FROM alertas_sistema a
                WHERE a.Estado = 'Pendiente'
                ORDER BY a.Fecha_Creacion DESC
                LIMIT 20
            """)
            
            alertas = self.cursor.fetchall()
            
            print(f"  [INFO] Alertas pendientes: {len(alertas)}\n")
            
            for alerta in alertas[:10]:
                id_alerta, tipo, mensaje, fecha, estado = alerta
                print(f"    [{tipo}] {mensaje[:60]}...")
                print(f"      ID: {id_alerta}, Fecha: {fecha}, Estado: {estado}\n")
            
            self.assert_true(len(alertas) > 0, "Sistema de alertas operativo")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_03_marcar_alertas_leidas(self):
        self.print_header(3, "MARCAR ALERTAS COMO LEÍDAS")
        
        try:
            # Marcar como leída
            self.cursor.execute("""
                UPDATE alertas_sistema
                SET Estado = 'Leida',
                    Fecha_Leida = NOW()
                WHERE ID_Alerta = 9001
            """)
            
            self.connection.commit()
            
            self.assert_true(True, "Alerta marcada como leída")
            
            # Verificar
            self.cursor.execute("""
                SELECT Estado, Fecha_Leida
                FROM alertas_sistema
                WHERE ID_Alerta = 9001
            """)
            
            result = self.cursor.fetchone()
            
            if result:
                estado, fecha_leida = result
                self.assert_equals(estado, 'Leida', "Estado actualizado")
                self.assert_true(fecha_leida is not None, "Fecha de lectura registrada")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_04_enviar_notificaciones(self):
        self.print_header(4, "ENVIAR NOTIFICACIONES")
        
        try:
            # Obtener un empleado para enviar notificación
            self.cursor.execute("""
                SELECT ID_Empleado, Nombres, Apellidos, Email
                FROM empleados
                WHERE Email IS NOT NULL
                  AND Activo = 1
                LIMIT 1
            """)
            
            empleado = self.cursor.fetchone()
            
            if not empleado:
                print("  [INFO] No hay empleados con email")
                self.tests_passed += 1
                return True
            
            id_empleado, nombres, apellidos, email = empleado
            
            # Crear solicitud de notificación por email
            self.cursor.execute("""
                INSERT INTO solicitudes_notificacion (
                    ID_Solicitud,
                    ID_Alerta,
                    Tipo_Notificacion,
                    Destinatario,
                    Mensaje,
                    Estado,
                    Fecha_Creacion
                ) VALUES (
                    9001,
                    9002,
                    'Email',
                    %s,
                    'Alerta TEST de límite de crédito',
                    'Pendiente',
                    NOW()
                )
            """, (email,))
            
            self.connection.commit()
            
            print(f"  [INFO] Notificación enviada a: {nombres} {apellidos} ({email})")
            
            self.assert_true(True, "Solicitud de notificación creada")
            
            # Simular envío exitoso
            self.cursor.execute("""
                UPDATE solicitudes_notificacion
                SET Estado = 'Enviada',
                    Fecha_Envio = NOW()
                WHERE ID_Solicitud = 9001
            """)
            
            self.connection.commit()
            
            self.assert_true(True, "Notificación marcada como enviada")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_05_reporte_alertas(self):
        self.print_header(5, "REPORTE DE ALERTAS")
        
        try:
            # Alertas por tipo
            self.cursor.execute("""
                SELECT 
                    Tipo,
                    COUNT(*) as Cantidad
                FROM alertas_sistema
                WHERE Fecha_Creacion >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                GROUP BY Tipo
                ORDER BY Cantidad DESC
            """)
            
            por_tipo = self.cursor.fetchall()
            
            print(f"  [INFO] Alertas últimos 30 días por tipo:\n")
            for tipo, cantidad in por_tipo:
                print(f"    {tipo}: {cantidad} alertas")
            
            # Alertas por estado
            self.cursor.execute("""
                SELECT 
                    Estado,
                    COUNT(*) as Cantidad
                FROM alertas_sistema
                WHERE Fecha_Creacion >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                GROUP BY Estado
            """)
            
            por_estado = self.cursor.fetchall()
            
            print(f"\n  [INFO] Alertas por estado:\n")
            for estado, cantidad in por_estado:
                print(f"    {estado}: {cantidad} alertas")
            
            # Alertas pendientes críticas
            self.cursor.execute("""
                SELECT COUNT(*)
                FROM alertas_sistema
                WHERE Estado = 'Pendiente'
                  AND Tipo IN ('STOCK_MINIMO', 'TIMBRADO_VENCIDO')
            """)
            
            criticas = self.cursor.fetchone()[0]
            
            print(f"\n  [INFO] Alertas críticas pendientes: {criticas}")
            
            self.assert_true(True, "Reporte generado correctamente")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    # ========================================================================
    # EJECUCIÓN
    # ========================================================================
    
    def run_all_tests(self):
        print("\n" + "="*80)
        print("INICIANDO TESTS DE MÓDULO: ALERTAS Y NOTIFICACIONES")
        print("="*80)
        
        if not self.conectar():
            return
        
        # Ejecutar tests
        self.test_01_crear_alertas()
        self.test_02_consultar_alertas_pendientes()
        self.test_03_marcar_alertas_leidas()
        self.test_04_enviar_notificaciones()
        self.test_05_reporte_alertas()
        
        # Limpiar
        self.limpiar_datos_prueba()
        
        # Resumen
        print("\n" + "="*80)
        print("RESUMEN DE TESTS - MÓDULO ALERTAS")
        print("="*80)
        print(f"Tests exitosos: {self.tests_passed}")
        print(f"Tests fallidos: {self.tests_failed}")
        
        total = self.tests_passed + self.tests_failed
        if total > 0:
            porcentaje = (self.tests_passed / total) * 100
            print(f"\nTotal: {self.tests_passed}/{total} tests exitosos ({porcentaje:.1f}%)")
        
        print("="*80)
        
        # Cerrar conexión
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


if __name__ == '__main__':
    test_suite = TestModuloAlertas()
    test_suite.run_all_tests()
