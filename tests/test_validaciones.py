"""
Tests para endpoints de validación (cargas y pagos pendientes)
"""
import pytest
from django.test import TestCase, Client
from django.contrib.auth.models import User
from gestion.models import (
    Empleado, TipoRolGeneral, Cliente, CargasSaldo, Ventas,
    DetalleVenta, Producto, Cajas
)
from decimal import Decimal
from datetime import datetime


class TestValidacionCargasSaldo(TestCase):
    """Tests para validación de cargas de saldo"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear roles
        self.rol_admin = Rol.objects.create(
            id_rol=3,
            descripcion='Administrador'
        )
        
        # Crear empleado admin
        self.admin = Empleado.objects.create(
            nombre_usuario='admin_test',
            contrasena_hash='$2b$12$dummy_hash',
            id_rol=self.rol_admin,
            activo=True
        )
        
        # Crear usuario Django para autenticación
        self.user = User.objects.create_user(
            username='admin_test',
            password='testpass123'
        )
        
        # Crear cliente
        self.cliente = Cliente.objects.create(
            nombre='Juan Pérez',
            ruc='12345678-9',
            telefono='0981234567'
        )
        
        # Crear carga pendiente
        self.carga_pendiente = CargasSaldo.objects.create(
            cliente=self.cliente,
            monto=Decimal('50000'),
            fecha=datetime.now(),
            estado='PENDIENTE',
            usuario_carga=self.admin,
            observaciones='Carga de prueba'
        )
        
        # Cliente de testing
        self.client = Client()
        self.client.login(username='admin_test', password='testpass123')
    
    def test_lista_cargas_pendientes_get(self):
        """Test: Listar cargas pendientes (GET)"""
        response = self.client.get('/pos/validaciones/cargas-pendientes/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cargas de Saldo Pendientes')
        self.assertContains(response, '₲ 50,000')
        self.assertContains(response, 'Juan Pérez')
    
    def test_lista_cargas_pendientes_filtro_busqueda(self):
        """Test: Filtrar cargas pendientes por búsqueda"""
        response = self.client.get(
            '/pos/validaciones/cargas-pendientes/',
            {'buscar': 'Juan'}
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Juan Pérez')
    
    def test_validar_carga_get(self):
        """Test: Mostrar formulario de validación (GET)"""
        response = self.client.get(
            f'/pos/validaciones/carga-saldo/{self.carga_pendiente.id}/'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Validar Carga de Saldo')
        self.assertContains(response, 'Juan Pérez')
        self.assertContains(response, '₲ 50,000')
    
    def test_validar_carga_post_success(self):
        """Test: Validar carga exitosamente (POST)"""
        response = self.client.post(
            f'/pos/validaciones/carga-saldo/{self.carga_pendiente.id}/',
            {
                'observaciones': 'Validado correctamente'
            }
        )
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que la carga fue actualizada
        self.carga_pendiente.refresh_from_db()
        self.assertEqual(self.carga_pendiente.estado, 'CONFIRMADO')
        self.assertIsNotNone(self.carga_pendiente.fecha_validacion)
        self.assertEqual(self.carga_pendiente.validado_por, self.admin)
    
    def test_validar_carga_inexistente(self):
        """Test: Intentar validar carga que no existe"""
        response = self.client.get('/pos/validaciones/carga-saldo/99999/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No se encontró la carga')
    
    def test_validar_carga_ya_confirmada(self):
        """Test: Intentar validar carga ya confirmada"""
        # Marcar como confirmada
        self.carga_pendiente.estado = 'CONFIRMADO'
        self.carga_pendiente.save()
        
        response = self.client.get(
            f'/pos/validaciones/carga-saldo/{self.carga_pendiente.id}/'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ya fue validada')


class TestValidacionPagos(TestCase):
    """Tests para validación de pagos por transferencia"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear roles
        self.rol_admin = Rol.objects.create(
            id_rol=3,
            descripcion='Administrador'
        )
        
        # Crear empleado
        self.empleado = Empleado.objects.create(
            nombre_usuario='cajero_test',
            contrasena_hash='$2b$12$dummy_hash',
            id_rol=self.rol_admin,
            activo=True
        )
        
        # Usuario Django
        self.user = User.objects.create_user(
            username='cajero_test',
            password='testpass123'
        )
        
        # Crear cliente
        self.cliente = Cliente.objects.create(
            nombre='María González',
            ruc='98765432-1',
            telefono='0991234567'
        )
        
        # Crear caja
        self.caja = Cajas.objects.create(
            nombre_caja='Caja 1',
            activo=True
        )
        
        # Crear producto
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            precio_venta=Decimal('10000'),
            stock=100,
            activo=True
        )
        
        # Crear venta pendiente de validación
        self.venta_pendiente = Ventas.objects.create(
            cliente=self.cliente,
            fecha=datetime.now(),
            monto_total=Decimal('30000'),
            forma_pago='CUENTA_CORRIENTE',
            motivo_credito='PAGO_PENDIENTE_TRANSFERENCIA - Pago por transferencia',
            id_caja=self.caja,
            usuario=self.empleado
        )
        
        # Crear detalle de venta
        DetalleVenta.objects.create(
            venta=self.venta_pendiente,
            producto=self.producto,
            cantidad=3,
            precio=Decimal('10000'),
            subtotal=Decimal('30000')
        )
        
        # Cliente de testing
        self.client = Client()
        self.client.login(username='cajero_test', password='testpass123')
    
    def test_lista_pagos_pendientes_get(self):
        """Test: Listar pagos pendientes (GET)"""
        response = self.client.get('/pos/validaciones/pagos-pendientes/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pagos por Transferencia Pendientes')
        self.assertContains(response, '₲ 30,000')
        self.assertContains(response, 'María González')
    
    def test_validar_pago_get(self):
        """Test: Mostrar formulario de validación de pago (GET)"""
        response = self.client.get(
            f'/pos/validaciones/pago/{self.venta_pendiente.id}/'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Validar Pago por Transferencia')
        self.assertContains(response, 'María González')
        self.assertContains(response, '₲ 30,000')
    
    def test_validar_pago_post_success(self):
        """Test: Validar pago exitosamente (POST)"""
        response = self.client.post(
            f'/pos/validaciones/pago/{self.venta_pendiente.id}/',
            {
                'comprobante': 'REF-123456',
                'observaciones': 'Transferencia verificada'
            }
        )
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que el motivo_credito fue actualizado
        self.venta_pendiente.refresh_from_db()
        self.assertNotIn('PAGO_PENDIENTE_TRANSFERENCIA', self.venta_pendiente.motivo_credito)
        self.assertIn('REF-123456', self.venta_pendiente.motivo_credito)
    
    def test_validar_pago_sin_comprobante(self):
        """Test: Intentar validar sin número de comprobante"""
        response = self.client.post(
            f'/pos/validaciones/pago/{self.venta_pendiente.id}/',
            {
                'comprobante': '',
                'observaciones': 'Test'
            }
        )
        
        # Debe redirigir con error
        self.assertEqual(response.status_code, 302)
    
    def test_lista_pagos_filtro_fecha(self):
        """Test: Filtrar pagos por rango de fechas"""
        response = self.client.get(
            '/pos/validaciones/pagos-pendientes/',
            {
                'fecha_desde': '2026-01-01',
                'fecha_hasta': '2026-12-31'
            }
        )
        
        self.assertEqual(response.status_code, 200)


class TestPermisos(TestCase):
    """Tests de permisos y seguridad"""
    
    def setUp(self):
        """Configuración inicial"""
        # Crear rol cajero (sin permisos de admin)
        self.rol_cajero = TipoRolGeneral.objects.create(
            nombre='Cajero'
        )
        
        # Crear empleado cajero
        self.cajero = Empleado.objects.create(
            nombre_usuario='cajero_sin_permisos',
            contrasena_hash='$2b$12$dummy_hash',
            id_rol=self.rol_cajero,
            activo=True
        )
        
        # Usuario Django
        self.user = User.objects.create_user(
            username='cajero_sin_permisos',
            password='testpass123'
        )
        
        self.client = Client()
        self.client.login(username='cajero_sin_permisos', password='testpass123')
    
    def test_acceso_sin_permisos_lista_cargas(self):
        """Test: Acceso denegado a lista de cargas sin permisos de admin"""
        response = self.client.get('/pos/validaciones/cargas-pendientes/')
        
        # Debe redirigir o retornar 403
        self.assertIn(response.status_code, [302, 403])
    
    def test_acceso_sin_permisos_validar_carga(self):
        """Test: Acceso denegado a validación sin permisos"""
        response = self.client.get('/pos/validaciones/carga-saldo/1/')
        
        self.assertIn(response.status_code, [302, 403])


@pytest.mark.django_db
class TestIntegracionValidaciones:
    """Tests de integración completos"""
    
    def test_flujo_completo_carga_saldo(self, client, django_user_model):
        """Test: Flujo completo de carga de saldo"""
        # 1. Crear datos necesarios
        # 2. Listar cargas pendientes
        # 3. Validar una carga
        # 4. Verificar que ya no aparece en pendientes
        pass
    
    def test_flujo_completo_pago_transferencia(self, client, django_user_model):
        """Test: Flujo completo de validación de pago"""
        pass


# ==================== EJECUTAR TESTS ====================
# pytest test_validaciones.py -v
# python manage.py test gestion.tests.test_validaciones
# coverage run --source='.' manage.py test gestion.tests.test_validaciones
# coverage report
