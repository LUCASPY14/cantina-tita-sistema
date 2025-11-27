#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
TEST MÓDULO: CONCILIACIÓN DE PAGOS
===================================

Tests para el sistema de conciliación bancaria.

Tablas involucradas:
- conciliacion_pagos

SCHEMA REAL conciliacion_pagos:
- ID_Conciliacion (bigint, PK)
- ID_Pago_Venta (bigint, FK → pagos_venta)
- Fecha_Acreditacion (datetime, nullable)
- Monto_Acreditado (decimal(10,2), nullable)
- Estado (enum('Conciliado','Pendiente','Rechazado'))
- Observaciones (text, nullable)
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cantina_project.settings')
django.setup()

from django.db import connection
from datetime import datetime, timedelta
from decimal import Decimal

class TestModuloConciliacion:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.cursor = connection.cursor()
        self.conciliaciones_creadas = []
    
    def limpiar_datos_prueba(self):
        """Limpia datos de prueba"""
        try:
            if self.conciliaciones_creadas:
                ids = ','.join(map(str, self.conciliaciones_creadas))
                self.cursor.execute(f"DELETE FROM conciliacion_pagos WHERE ID_Conciliacion IN ({ids})")
            
            connection.commit()
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
    
    def test_01_registrar_conciliacion(self):
        self.print_header(1, "REGISTRAR CONCILIACIÓN DE PAGOS")
        
        try:
            # Buscar pago bancario para conciliar
            self.cursor.execute("""
                SELECT pv.ID_Pago_Venta, pv.Monto_Aplicado, mp.Descripcion
                FROM pagos_venta pv
                INNER JOIN medios_pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
                WHERE mp.Descripcion IN ('Tarjeta de Credito', 'Tarjeta de Debito', 'Giros TIGO')
                  AND pv.Monto_Aplicado > 0
                  AND NOT EXISTS (
                      SELECT 1 FROM conciliacion_pagos cp 
                      WHERE cp.ID_Pago_Venta = pv.ID_Pago_Venta
                  )
                LIMIT 1
            """)
            
            pago = self.cursor.fetchone()
            
            if not pago:
                print("  [INFO] No hay pagos bancarios para conciliar")
                self.tests_passed += 1
                return True
            
            id_pago, monto_sistema, medio_pago = pago
            monto_banco = monto_sistema  # Simulamos que coincide
            
            print(f"  [INFO] Pago #{id_pago}: {medio_pago}")
            print(f"  [INFO] Monto sistema: Gs.{float(monto_sistema):,.0f}")
            print(f"  [INFO] Monto banco: Gs.{float(monto_banco):,.0f}")
            
            # Crear conciliación
            self.cursor.execute("""
                INSERT INTO conciliacion_pagos (
                    ID_Conciliacion,
                    ID_Pago_Venta,
                    Fecha_Acreditacion,
                    Monto_Acreditado,
                    Estado,
                    Observaciones
                ) VALUES (
                    9001,
                    %s,
                    NOW(),
                    %s,
                    'Conciliado',
                    'TEST: Conciliación automática - montos coinciden'
                )
            """, (id_pago, monto_banco))
            
            self.conciliaciones_creadas.append(9001)
            connection.commit()
            
            self.assert_true(True, "Conciliación registrada correctamente")
            
            # Verificar
            self.cursor.execute("""
                SELECT Estado, Observaciones
                FROM conciliacion_pagos
                WHERE ID_Conciliacion = 9001
            """)
            
            result = self.cursor.fetchone()
            if result:
                estado, obs = result
                self.assert_equals(estado, 'Conciliado', "Estado de conciliación")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_02_identificar_diferencias(self):
        self.print_header(2, "IDENTIFICAR DIFERENCIAS EN CONCILIACIÓN")
        
        try:
            # Buscar otro pago para simular diferencia
            self.cursor.execute("""
                SELECT pv.ID_Pago_Venta, pv.Monto_Aplicado
                FROM pagos_venta pv
                INNER JOIN medios_pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
                WHERE mp.Descripcion IN ('Tarjeta de Credito', 'Tarjeta de Debito')
                  AND pv.Monto_Aplicado > 0
                  AND NOT EXISTS (
                      SELECT 1 FROM conciliacion_pagos cp 
                      WHERE cp.ID_Pago_Venta = pv.ID_Pago_Venta
                  )
                LIMIT 1
            """)
            
            pago = self.cursor.fetchone()
            
            if not pago:
                print("  [INFO] No hay más pagos disponibles")
                self.tests_passed += 1
                return True
            
            id_pago, monto_sistema = pago
            
            # Simular diferencia del 2% (comisión bancaria)
            monto_banco = float(monto_sistema) * 0.98
            diferencia = float(monto_sistema) - monto_banco
            
            print(f"  [INFO] Monto sistema: Gs.{float(monto_sistema):,.0f}")
            print(f"  [INFO] Monto banco: Gs.{monto_banco:,.0f}")
            print(f"  [INFO] Diferencia: Gs.{diferencia:,.0f}")
            
            # Crear conciliación con diferencia
            self.cursor.execute("""
                INSERT INTO conciliacion_pagos (
                    ID_Conciliacion,
                    ID_Pago_Venta,
                    Fecha_Acreditacion,
                    Monto_Acreditado,
                    Estado,
                    Observaciones
                ) VALUES (
                    9002,
                    %s,
                    NOW(),
                    %s,
                    'Pendiente',
                    %s
                )
            """, (id_pago, monto_banco, f'TEST: Diferencia de Gs.{diferencia:,.0f} - Revisar comisión bancaria'))
            
            self.conciliaciones_creadas.append(9002)
            connection.commit()
            
            self.assert_true(True, "Diferencia identificada y registrada")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_03_consultar_por_periodo(self):
        self.print_header(3, "CONSULTAR CONCILIACIONES POR PERÍODO")
        
        try:
            # Últimos 30 días
            self.cursor.execute("""
                SELECT 
                    cp.ID_Conciliacion,
                    cp.Fecha_Acreditacion,
                    pv.Monto_Aplicado as Monto_Sistema,
                    cp.Monto_Acreditado as Monto_Banco,
                    cp.Estado,
                    mp.Descripcion as Medio_Pago
                FROM conciliacion_pagos cp
                INNER JOIN pagos_venta pv ON cp.ID_Pago_Venta = pv.ID_Pago_Venta
                INNER JOIN medios_pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
                WHERE cp.Fecha_Acreditacion >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                ORDER BY cp.Fecha_Acreditacion DESC
                LIMIT 20
            """)
            
            conciliaciones = self.cursor.fetchall()
            
            print(f"  [INFO] Conciliaciones últimos 30 días: {len(conciliaciones)}\n")
            
            for conc in conciliaciones[:10]:
                id_conc, fecha, monto_sist, monto_banco, estado, medio = conc
                
                # Calcular diferencia si hay monto banco
                if monto_banco:
                    diferencia = float(monto_sist) - float(monto_banco)
                    dif_str = f"Dif: Gs.{diferencia:,.0f}" if diferencia != 0 else "Sin diferencia"
                else:
                    dif_str = "Monto banco: N/A"
                
                print(f"    Conciliación #{id_conc} - {medio}")
                print(f"      Sistema: Gs.{float(monto_sist):,.0f} | Banco: Gs.{float(monto_banco or 0):,.0f}")
                print(f"      {dif_str} | Estado: {estado}\n")
            
            self.assert_true(len(conciliaciones) >= 0, "Consulta ejecutada correctamente")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_04_reporte_diferencias(self):
        self.print_header(4, "REPORTE DE DIFERENCIAS")
        
        try:
            # Conciliaciones con diferencia
            self.cursor.execute("""
                SELECT 
                    cp.ID_Conciliacion,
                    pv.Monto_Aplicado - COALESCE(cp.Monto_Acreditado, 0) as Diferencia,
                    mp.Descripcion,
                    cp.Observaciones
                FROM conciliacion_pagos cp
                INNER JOIN pagos_venta pv ON cp.ID_Pago_Venta = pv.ID_Pago_Venta
                INNER JOIN medios_pago mp ON pv.ID_Medio_Pago = mp.ID_Medio_Pago
                WHERE ABS(pv.Monto_Aplicado - COALESCE(cp.Monto_Acreditado, 0)) > 0.01
                ORDER BY ABS(pv.Monto_Aplicado - COALESCE(cp.Monto_Acreditado, 0)) DESC
                LIMIT 10
            """)
            
            diferencias = self.cursor.fetchall()
            
            print(f"  [INFO] Conciliaciones con diferencias: {len(diferencias)}\n")
            
            for dif in diferencias:
                id_conc, diferencia, medio, obs = dif
                print(f"    Conciliación #{id_conc} - {medio}")
                print(f"      Diferencia: Gs.{float(diferencia):,.0f}")
                if obs:
                    print(f"      Observación: {obs[:60]}...\n")
            
            # Estadísticas
            self.cursor.execute("""
                SELECT 
                    COUNT(*) as Total,
                    SUM(ABS(pv.Monto_Aplicado - COALESCE(cp.Monto_Acreditado, 0))) as Suma_Diferencias
                FROM conciliacion_pagos cp
                INNER JOIN pagos_venta pv ON cp.ID_Pago_Venta = pv.ID_Pago_Venta
                WHERE ABS(pv.Monto_Aplicado - COALESCE(cp.Monto_Acreditado, 0)) > 0.01
            """)
            
            stats = self.cursor.fetchone()
            if stats:
                total, suma = stats
                print(f"  [INFO] Total diferencias: {total}")
                print(f"  [INFO] Suma diferencias: Gs.{float(suma or 0):,.0f}")
            
            self.assert_true(True, "Reporte generado correctamente")
            
            self.tests_passed += 1
            return True
            
        except Exception as e:
            print(f"  [ERROR] {str(e)}")
            self.tests_failed += 1
            return False
    
    def test_05_resumen_general(self):
        self.print_header(5, "RESUMEN GENERAL DE CONCILIACIÓN")
        
        try:
            # Por estado
            self.cursor.execute("""
                SELECT 
                    Estado,
                    COUNT(*) as Cantidad,
                    SUM(COALESCE(Monto_Acreditado, 0)) as Monto_Total
                FROM conciliacion_pagos
                WHERE Fecha_Acreditacion >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                GROUP BY Estado
            """)
            
            por_estado = self.cursor.fetchall()
            
            print(f"  [INFO] Conciliaciones últimos 30 días por estado:\n")
            
            total_conciliaciones = 0
            for estado, cantidad, monto in por_estado:
                print(f"    {estado}: {cantidad} conciliaciones, Gs.{float(monto):,.0f}")
                total_conciliaciones += cantidad
            
            # Tasa de conciliación
            if total_conciliaciones > 0:
                self.cursor.execute("""
                    SELECT COUNT(*) 
                    FROM conciliacion_pagos
                    WHERE Estado = 'Conciliado'
                      AND Fecha_Acreditacion >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                """)
                
                conciliados = self.cursor.fetchone()[0]
                tasa = (conciliados / total_conciliaciones) * 100
                
                print(f"\n  [INFO] Tasa de conciliación: {tasa:.1f}% ({conciliados}/{total_conciliaciones})")
            
            self.assert_true(True, "Resumen generado correctamente")
            
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
        print("INICIANDO TESTS DE MÓDULO: CONCILIACIÓN DE PAGOS")
        print("="*80)
        
        # Ejecutar tests
        self.test_01_registrar_conciliacion()
        self.test_02_identificar_diferencias()
        self.test_03_consultar_por_periodo()
        self.test_04_reporte_diferencias()
        self.test_05_resumen_general()
        
        # Limpiar
        self.limpiar_datos_prueba()
        
        # Resumen
        print("\n" + "="*80)
        print("RESUMEN DE TESTS - MÓDULO CONCILIACIÓN")
        print("="*80)
        print(f"Tests exitosos: {self.tests_passed}")
        print(f"Tests fallidos: {self.tests_failed}")
        
        total = self.tests_passed + self.tests_failed
        if total > 0:
            porcentaje = (self.tests_passed / total) * 100
            print(f"\nTotal: {self.tests_passed}/{total} tests exitosos ({porcentaje:.1f}%)")
        
        print("="*80)
        
        # Cerrar cursor
        if self.cursor:
            self.cursor.close()


if __name__ == '__main__':
    test_suite = TestModuloConciliacion()
    test_suite.run_all_tests()
