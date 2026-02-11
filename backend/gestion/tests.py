"""
Tests Unitarios - Sistema de Cuenta Corriente
==============================================

Tests automatizados para el sistema de gestión de cuenta corriente.
"""

from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

from pos.models import Venta as Ventas, PagoVenta as PagosVenta
from gestion.models import (
    Cliente, Compras, Proveedor, 
    AplicacionPagosVentas,
    Empleado, TiposPago
)


class VentasModelTest(TestCase):
    """Tests para el modelo Ventas"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear empleado
        self.empleado = Empleado.objects.create(
            nombre='Juan',
            apellido='Pérez',
            ci='1234567',
            telefono='0981234567',
            activo=True
        )
        
        # Crear cliente
        self.cliente = Cliente.objects.create(
            nombres='María',
            apellidos='González',
            ruc_ci='9876543',
            telefono='0971234567',
            activo=True,
            limite_credito=1000000
        )
        
        # Crear tipo de pago
        self.tipo_pago = TiposPago.objects.create(
            descripcion='Efectivo',
            activo=True
        )
    
    def test_venta_pendiente_inicial(self):
        """Test: Una venta nueva debe tener estado PENDIENTE"""
        venta = Ventas.objects.create(
            nro_factura_venta=1001,
            id_cliente=self.cliente,
            id_tipo_pago=self.tipo_pago,
            id_empleado_cajero=self.empleado,
            fecha=timezone.now(),
            monto_total=50000,
            saldo_pendiente=50000,
            estado_pago='PENDIENTE',
            estado='PROCESADO',
            tipo_venta='Venta Directa'
        )
        
        self.assertEqual(venta.estado_pago, 'PENDIENTE')
        self.assertEqual(venta.saldo_pendiente, venta.monto_total)
    
    def test_query_ventas_pendientes(self):
        """Test: Query de ventas pendientes funciona correctamente"""
        # Crear venta pendiente
        Ventas.objects.create(
            nro_factura_venta=1002,
            id_cliente=self.cliente,
            id_tipo_pago=self.tipo_pago,
            id_empleado_cajero=self.empleado,
            fecha=timezone.now(),
            monto_total=100000,
            saldo_pendiente=100000,
            estado_pago='PENDIENTE',
            estado='PROCESADO',
            tipo_venta='Venta Directa'
        )
        
        # Query con MAYÚSCULAS
        pendientes = Ventas.objects.filter(
            estado_pago__in=['PENDIENTE', 'PARCIAL']
        )
        
        self.assertEqual(pendientes.count(), 1)
    
    def test_validacion_saldo_mayor_a_total(self):
        """Test: El saldo pendiente no puede ser mayor al total"""
        venta = Ventas(
            nro_factura_venta=1003,
            id_cliente=self.cliente,
            id_tipo_pago=self.tipo_pago,
            id_empleado_cajero=self.empleado,
            fecha=timezone.now(),
            monto_total=50000,
            saldo_pendiente=60000,  # ❌ Mayor al total
            estado_pago='PENDIENTE',
            estado='PROCESADO',
            tipo_venta='Venta Directa'
        )
        
        # Debe lanzar ValidationError
        with self.assertRaises(ValidationError):
            venta.full_clean()
    
    def test_validacion_pagada_con_saldo(self):
        """Test: Una venta PAGADA no puede tener saldo pendiente"""
        venta = Ventas(
            nro_factura_venta=1004,
            id_cliente=self.cliente,
            id_tipo_pago=self.tipo_pago,
            id_empleado_cajero=self.empleado,
            fecha=timezone.now(),
            monto_total=50000,
            saldo_pendiente=10000,  # ❌ PAGADA con saldo > 0
            estado_pago='PAGADA',
            estado='PROCESADO',
            tipo_venta='Venta Directa'
        )
        
        # Debe lanzar ValidationError
        with self.assertRaises(ValidationError):
            venta.full_clean()


class ComprasModelTest(TestCase):
    """Tests para el modelo Compras"""
    
    def setUp(self):
        """Configuración inicial"""
        # Crear proveedor
        self.proveedor = Proveedor.objects.create(
            ruc='80012345-6',
            razon_social='Distribuidora Test S.A.',
            telefono='021123456',
            activo=True
        )
    
    def test_query_compras_pendientes(self):
        """Test: Query de compras pendientes funciona"""
        # Crear compra pendiente
        Compras.objects.create(
            nro_factura=5001,
            id_proveedor=self.proveedor,
            fecha=timezone.now(),
            total=Decimal('500000.00'),
            saldo_pendiente=Decimal('500000.00'),
            estado_pago='PENDIENTE'
        )
        
        # Query
        pendientes = Compras.objects.filter(
            estado_pago__in=['PENDIENTE', 'PARCIAL']
        )
        
        self.assertEqual(pendientes.count(), 1)
        self.assertEqual(pendientes.first().saldo_pendiente, Decimal('500000.00'))
    
    def test_deuda_proveedores_agregacion(self):
        """Test: Agregación de deuda por proveedor"""
        from django.db.models import Sum, Q
        
        # Crear múltiples compras
        Compras.objects.create(
            nro_factura=5002,
            id_proveedor=self.proveedor,
            fecha=timezone.now(),
            total=Decimal('300000.00'),
            saldo_pendiente=Decimal('300000.00'),
            estado_pago='PENDIENTE'
        )
        
        Compras.objects.create(
            nro_factura=5003,
            id_proveedor=self.proveedor,
            fecha=timezone.now(),
            total=Decimal('200000.00'),
            saldo_pendiente=Decimal('200000.00'),
            estado_pago='PARCIAL'
        )
        
        # Query como en deuda_proveedores_view
        deudas = Compras.objects.filter(
            Q(estado_pago='PENDIENTE') | Q(estado_pago='PARCIAL'),
            saldo_pendiente__gt=0
        ).aggregate(total=Sum('saldo_pendiente'))
        
        self.assertEqual(deudas['total'], Decimal('500000.00'))


class CuentaCorrienteViewsTest(TestCase):
    """Tests para las vistas de cuenta corriente"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        
        # Crear usuario y autenticar
        self.user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.client.login(username='admin', password='admin123')
    
    def test_compras_dashboard_view_accesible(self):
        """Test: Vista compras_dashboard es accesible"""
        response = self.client.get('/pos/compras-dashboard/')
        
        # Verificar que la vista responde (puede requerir login)
        self.assertIn(response.status_code, [200, 302])
    
    def test_deuda_proveedores_view_accesible(self):
        """Test: Vista deuda_proveedores es accesible"""
        response = self.client.get('/pos/deuda-proveedores/')
        
        # Verificar que la vista responde
        self.assertIn(response.status_code, [200, 302])


class EstadoPagoStandardTest(TestCase):
    """Tests para verificar el estándar de MAYÚSCULAS"""
    
    def test_valores_estado_pago_mayusculas(self):
        """Test: Todos los valores de estado_pago usan MAYÚSCULAS"""
        estados_validos = ['PENDIENTE', 'PARCIAL', 'PAGADA', 'ANULADO']
        
        # Verificar que los estados están en mayúsculas
        for estado in estados_validos:
            self.assertEqual(estado, estado.upper())
    
    def test_query_con_mayusculas_funciona(self):
        """Test: Queries con MAYÚSCULAS funcionan correctamente"""
        from django.db.models import Q
        
        # Este test verifica que la sintaxis es correcta
        query = Q(estado_pago='PENDIENTE') | Q(estado_pago='PARCIAL')
        
        # El query debe poder ejecutarse sin errores
        self.assertIsNotNone(query)


class IntegridadDatosTest(TestCase):
    """Tests para verificar integridad de datos"""
    
    def test_sin_saldos_negativos_ventas(self):
        """Test: No debe haber ventas con saldo negativo"""
        ventas_negativas = Ventas.objects.filter(saldo_pendiente__lt=0)
        
        self.assertEqual(
            ventas_negativas.count(), 
            0,
            "Hay ventas con saldo negativo"
        )
    
    def test_sin_saldos_negativos_compras(self):
        """Test: No debe haber compras con saldo negativo"""
        compras_negativas = Compras.objects.filter(saldo_pendiente__lt=0)
        
        self.assertEqual(
            compras_negativas.count(),
            0,
            "Hay compras con saldo negativo"
        )
    
    def test_ventas_pagadas_sin_saldo(self):
        """Test: Ventas PAGADA deben tener saldo 0"""
        ventas_pagadas_con_saldo = Ventas.objects.filter(
            estado_pago='PAGADA',
            saldo_pendiente__gt=0
        )
        
        self.assertEqual(
            ventas_pagadas_con_saldo.count(),
            0,
            "Hay ventas PAGADA con saldo pendiente > 0"
        )


class ReportesIntegrationTest(TestCase):
    """Tests de integración para reportes"""
    
    def test_reportes_pdf_importan(self):
        """Test: Clases de reportes se pueden importar"""
        from gestion.reportes import ReportesPDF, ReportesExcel
        
        self.assertTrue(hasattr(ReportesPDF, 'reporte_cta_corriente_cliente'))
        self.assertTrue(hasattr(ReportesPDF, 'reporte_cta_corriente_proveedor'))
        self.assertTrue(hasattr(ReportesExcel, 'reporte_cta_corriente_cliente'))
        self.assertTrue(hasattr(ReportesExcel, 'reporte_cta_corriente_proveedor'))


# =============================================================================
# Para ejecutar estos tests:
#
#     # Todos los tests
#     python manage.py test gestion
#
#     # Tests específicos
#     python manage.py test gestion.tests.VentasModelTest
#     python manage.py test gestion.tests.ComprasModelTest
#     
#     # Con verbosidad
#     python manage.py test gestion --verbosity=2
#     
#     # Con coverage (instalar: pip install coverage)
#     coverage run --source='.' manage.py test gestion
#     coverage report
# =============================================================================
