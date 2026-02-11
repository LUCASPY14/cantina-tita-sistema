"""
Tests de Performance - Sistema de Cuenta Corriente
==================================================

Tests para medir y optimizar el rendimiento de queries.
"""

import time
from decimal import Decimal
from django.test import TestCase
from django.db import connection
from django.db.models import Sum, Count, Q
from django.test.utils import override_settings
from django.utils import timezone

from gestion.models import (
    Cliente, Ventas, Compras, Proveedor,
    Empleado, TiposPago
)


class QueryPerformanceTestCase(TestCase):
    """Tests de performance de queries"""
    
    @classmethod
    def setUpTestData(cls):
        """
        Crear datos de prueba una sola vez
        (más eficiente que setUp que se ejecuta en cada test)
        """
        # Crear datos básicos
        cls.empleado = Empleado.objects.create(
            nombre='Juan',
            apellido='Pérez',
            ci='1234567',
            telefono='0981234567',
            activo=True
        )
        
        cls.tipo_pago = TiposPago.objects.create(
            descripcion='Efectivo',
            activo=True
        )
        
        # Crear 100 clientes
        cls.clientes = []
        for i in range(100):
            cliente = Cliente.objects.create(
                nombres=f'Cliente{i}',
                apellidos=f'Apellido{i}',
                ruc_ci=f'1234567{i:03d}',
                telefono=f'09812345{i:02d}',
                activo=True,
                limite_credito=1000000
            )
            cls.clientes.append(cliente)
        
        # Crear 50 proveedores
        cls.proveedores = []
        for i in range(50):
            proveedor = Proveedor.objects.create(
                ruc=f'8001234{i:02d}-{i % 10}',
                razon_social=f'Proveedor {i}',
                telefono=f'02112345{i:02d}',
                activo=True
            )
            cls.proveedores.append(proveedor)
        
        # Crear 1000 ventas
        for i in range(1000):
            cliente = cls.clientes[i % len(cls.clientes)]
            Ventas.objects.create(
                nro_factura_venta=10000 + i,
                id_cliente=cliente,
                id_tipo_pago=cls.tipo_pago,
                id_empleado_cajero=cls.empleado,
                fecha=timezone.now(),
                monto_total=50000 + (i * 1000),
                saldo_pendiente=(50000 + (i * 1000)) * (i % 3) / 3,  # Algunos pagados, otros pendientes
                estado_pago=['PAGADA', 'PENDIENTE', 'PARCIAL'][i % 3],
                estado='PROCESADO',
                tipo_venta='Venta Directa'
            )
        
        # Crear 500 compras
        for i in range(500):
            proveedor = cls.proveedores[i % len(cls.proveedores)]
            Compras.objects.create(
                nro_factura=20000 + i,
                id_proveedor=proveedor,
                fecha=timezone.now(),
                total=Decimal(100000 + (i * 1000)),
                saldo_pendiente=Decimal((100000 + (i * 1000)) * (i % 3) / 3),
                estado_pago=['PAGADA', 'PENDIENTE', 'PARCIAL'][i % 3]
            )
    
    def count_queries(self, func):
        """Contador de queries ejecutadas"""
        queries_before = len(connection.queries)
        start_time = time.time()
        
        result = func()
        
        end_time = time.time()
        queries_after = len(connection.queries)
        
        return {
            'result': result,
            'queries_count': queries_after - queries_before,
            'execution_time': end_time - start_time
        }
    
    def test_query_ventas_pendientes_sin_optimizar(self):
        """Test: Query sin optimizar (N+1 problem)"""
        print("\n📊 TEST: Query SIN optimizar")
        
        def query_sin_optimizar():
            ventas = Ventas.objects.filter(estado_pago__in=['PENDIENTE', 'PARCIAL'])
            # Acceder a relaciones (causa N+1)
            for venta in ventas[:10]:
                _ = venta.id_cliente.nombres
                _ = venta.id_empleado_cajero.nombre
            return ventas.count()
        
        stats = self.count_queries(query_sin_optimizar)
        
        print(f"   Queries ejecutadas: {stats['queries_count']}")
        print(f"   Tiempo: {stats['execution_time']:.4f}s")
        
        # Debe ejecutar múltiples queries (N+1)
        self.assertGreater(stats['queries_count'], 10)
    
    def test_query_ventas_pendientes_optimizado(self):
        """Test: Query optimizado con select_related"""
        print("\n📊 TEST: Query OPTIMIZADO con select_related")
        
        def query_optimizado():
            ventas = Ventas.objects.filter(
                estado_pago__in=['PENDIENTE', 'PARCIAL']
            ).select_related('id_cliente', 'id_empleado_cajero')
            
            # Acceder a relaciones (NO causa N+1)
            for venta in ventas[:10]:
                _ = venta.id_cliente.nombres
                _ = venta.id_empleado_cajero.nombre
            return ventas.count()
        
        stats = self.count_queries(query_optimizado)
        
        print(f"   Queries ejecutadas: {stats['queries_count']}")
        print(f"   Tiempo: {stats['execution_time']:.4f}s")
        
        # Debe ejecutar pocas queries (1-3)
        self.assertLessEqual(stats['queries_count'], 5)
    
    def test_agregacion_deuda_clientes(self):
        """Test: Agregación de deuda por cliente"""
        print("\n📊 TEST: Agregación de deuda por cliente")
        
        def query_agregacion():
            return Ventas.objects.filter(
                estado_pago__in=['PENDIENTE', 'PARCIAL']
            ).values(
                'id_cliente__nombres',
                'id_cliente__apellidos'
            ).annotate(
                saldo_total=Sum('saldo_pendiente'),
                cantidad=Count('id_venta')
            ).order_by('-saldo_total')
        
        stats = self.count_queries(query_agregacion)
        
        print(f"   Queries ejecutadas: {stats['queries_count']}")
        print(f"   Tiempo: {stats['execution_time']:.4f}s")
        print(f"   Resultados: {len(stats['result'])}")
        
        # Debe ser eficiente (1-2 queries)
        self.assertLessEqual(stats['queries_count'], 3)
    
    def test_agregacion_deuda_proveedores(self):
        """Test: Agregación de deuda con proveedores"""
        print("\n📊 TEST: Agregación de deuda con proveedores")
        
        def query_agregacion():
            return Compras.objects.filter(
                Q(estado_pago='PENDIENTE') | Q(estado_pago='PARCIAL'),
                saldo_pendiente__gt=0
            ).values(
                'id_proveedor__razon_social'
            ).annotate(
                saldo=Sum('saldo_pendiente'),
                cantidad=Count('id_compra')
            ).order_by('-saldo')
        
        stats = self.count_queries(query_agregacion)
        
        print(f"   Queries ejecutadas: {stats['queries_count']}")
        print(f"   Tiempo: {stats['execution_time']:.4f}s")
        print(f"   Resultados: {len(stats['result'])}")
        
        # Debe ser eficiente
        self.assertLessEqual(stats['queries_count'], 3)
    
    def test_query_con_filtros_multiples(self):
        """Test: Query con múltiples filtros"""
        print("\n📊 TEST: Query con múltiples filtros")
        
        def query_filtros():
            return Ventas.objects.filter(
                estado_pago='PENDIENTE',
                monto_total__gte=100000,
                fecha__year=2025
            ).select_related('id_cliente').count()
        
        stats = self.count_queries(query_filtros)
        
        print(f"   Queries ejecutadas: {stats['queries_count']}")
        print(f"   Tiempo: {stats['execution_time']:.4f}s")
        
        # Debe ser 1 query
        self.assertEqual(stats['queries_count'], 1)
    
    def test_comparacion_exists_vs_count(self):
        """Test: Comparar exists() vs count()"""
        print("\n📊 TEST: exists() vs count()")
        
        def query_con_count():
            return Ventas.objects.filter(estado_pago='PENDIENTE').count() > 0
        
        def query_con_exists():
            return Ventas.objects.filter(estado_pago='PENDIENTE').exists()
        
        stats_count = self.count_queries(query_con_count)
        stats_exists = self.count_queries(query_con_exists)
        
        print(f"   count() - Queries: {stats_count['queries_count']}, Tiempo: {stats_count['execution_time']:.4f}s")
        print(f"   exists() - Queries: {stats_exists['queries_count']}, Tiempo: {stats_exists['execution_time']:.4f}s")
        
        # exists() debe ser igual o más rápido
        self.assertLessEqual(stats_exists['execution_time'], stats_count['execution_time'] * 1.5)


class BulkOperationsTestCase(TestCase):
    """Tests de operaciones bulk"""
    
    def test_bulk_create_vs_individual_saves(self):
        """Test: bulk_create vs saves individuales"""
        print("\n📊 TEST: bulk_create vs saves individuales")
        
        # Crear empleado y tipo de pago
        empleado = Empleado.objects.create(
            nombre='Test',
            apellido='User',
            ci='1111111',
            telefono='0991234567',
            activo=True
        )
        
        tipo_pago = TiposPago.objects.create(
            descripcion='Test',
            activo=True
        )
        
        # Crear clientes para test
        clientes = []
        for i in range(100):
            cliente = Cliente.objects.create(
                nombres=f'Cliente{i}',
                apellidos=f'Test{i}',
                ruc_ci=f'999{i:04d}',
                telefono='0991234567',
                activo=True,
                limite_credito=1000000
            )
            clientes.append(cliente)
        
        # Test 1: Saves individuales
        start_time = time.time()
        for i in range(100):
            Ventas.objects.create(
                nro_factura_venta=30000 + i,
                id_cliente=clientes[i],
                id_tipo_pago=tipo_pago,
                id_empleado_cajero=empleado,
                fecha=timezone.now(),
                monto_total=50000,
                saldo_pendiente=50000,
                estado_pago='PENDIENTE',
                estado='PROCESADO',
                tipo_venta='Venta Directa'
            )
        time_individual = time.time() - start_time
        
        # Limpiar
        Ventas.objects.filter(nro_factura_venta__gte=30000).delete()
        
        # Test 2: Bulk create
        ventas_bulk = []
        for i in range(100):
            ventas_bulk.append(
                Ventas(
                    nro_factura_venta=30000 + i,
                    id_cliente=clientes[i],
                    id_tipo_pago=tipo_pago,
                    id_empleado_cajero=empleado,
                    fecha=timezone.now(),
                    monto_total=50000,
                    saldo_pendiente=50000,
                    estado_pago='PENDIENTE',
                    estado='PROCESADO',
                    tipo_venta='Venta Directa'
                )
            )
        
        start_time = time.time()
        Ventas.objects.bulk_create(ventas_bulk)
        time_bulk = time.time() - start_time
        
        print(f"   Saves individuales: {time_individual:.4f}s")
        print(f"   Bulk create: {time_bulk:.4f}s")
        print(f"   Mejora: {(time_individual / time_bulk):.2f}x más rápido")
        
        # bulk_create debe ser significativamente más rápido
        self.assertLess(time_bulk, time_individual * 0.5)


# =============================================================================
# Para ejecutar estos tests:
#
#     # Tests de performance
#     python manage.py test gestion.tests_performance --verbosity=2
#
#     # Ver queries ejecutadas
#     python manage.py test gestion.tests_performance --verbosity=2 --debug-mode
# =============================================================================
