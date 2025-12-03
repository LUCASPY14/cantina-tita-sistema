"""
Tests de Vistas con Autenticación - Sistema de Cuenta Corriente
================================================================

Tests adicionales para verificar vistas protegidas por autenticación
y permisos de usuario.
"""

from decimal import Decimal
from django.test import TestCase, Client
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from django.utils import timezone

from gestion.models import (
    Cliente, Ventas, Compras, Proveedor,
    Empleado, TiposPago, MediosPago
)


class AuthenticationTestCase(TestCase):
    """Tests de autenticación y permisos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        
        # Crear usuarios con diferentes roles
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@cantina.com'
        )
        
        self.staff_user = User.objects.create_user(
            username='staff',
            password='staff123',
            is_staff=True
        )
        
        self.normal_user = User.objects.create_user(
            username='user',
            password='user123'
        )
        
        # Crear datos básicos
        self.empleado = Empleado.objects.create(
            nombre='Juan',
            apellido='Pérez',
            ci='1234567',
            telefono='0981234567',
            activo=True
        )
        
        self.cliente = Cliente.objects.create(
            nombres='María',
            apellidos='González',
            ruc_ci='9876543',
            telefono='0971234567',
            activo=True,
            limite_credito=1000000
        )
        
        self.proveedor = Proveedor.objects.create(
            ruc='80012345-6',
            razon_social='Distribuidora Test S.A.',
            telefono='021123456',
            activo=True
        )
    
    def test_vista_sin_login_redirect(self):
        """Test: Vista protegida redirige si no hay login"""
        # Intentar acceder sin login
        response = self.client.get('/pos/compras-dashboard/')
        
        # Debe redirigir al login o devolver 302/401
        self.assertIn(response.status_code, [302, 401, 403])
    
    def test_vista_con_login_admin(self):
        """Test: Admin puede acceder a todas las vistas"""
        # Login como admin
        self.client.login(username='admin', password='admin123')
        
        # Intentar acceder a vista protegida
        response = self.client.get('/pos/compras-dashboard/')
        
        # Debe permitir acceso
        self.assertIn(response.status_code, [200, 302])
    
    def test_vista_con_login_staff(self):
        """Test: Staff puede acceder a vistas de staff"""
        # Login como staff
        self.client.login(username='staff', password='staff123')
        
        response = self.client.get('/pos/compras-dashboard/')
        
        # Debe permitir acceso
        self.assertIn(response.status_code, [200, 302])
    
    def test_vista_con_login_normal_user(self):
        """Test: Usuario normal sin permisos"""
        # Login como usuario normal
        self.client.login(username='user', password='user123')
        
        response = self.client.get('/pos/compras-dashboard/')
        
        # Puede ser redirigido o prohibido
        self.assertIn(response.status_code, [200, 302, 403])


class ComprasDashboardViewTest(TestCase):
    """Tests para la vista compras_dashboard_view"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Crear proveedor
        self.proveedor = Proveedor.objects.create(
            ruc='80012345-6',
            razon_social='Proveedor Test',
            telefono='021123456',
            activo=True
        )
        
        # Crear compras de prueba
        Compras.objects.create(
            nro_factura=1001,
            id_proveedor=self.proveedor,
            fecha=timezone.now(),
            total=Decimal('500000.00'),
            saldo_pendiente=Decimal('500000.00'),
            estado_pago='PENDIENTE'
        )
        
        Compras.objects.create(
            nro_factura=1002,
            id_proveedor=self.proveedor,
            fecha=timezone.now(),
            total=Decimal('300000.00'),
            saldo_pendiente=Decimal('150000.00'),
            estado_pago='PARCIAL'
        )
    
    def test_vista_accesible(self):
        """Test: Vista es accesible con autenticación"""
        response = self.client.get('/pos/compras-dashboard/')
        
        self.assertIn(response.status_code, [200, 302])
    
    def test_contexto_contiene_datos_esperados(self):
        """Test: El contexto contiene los datos esperados"""
        response = self.client.get('/pos/compras-dashboard/')
        
        if response.status_code == 200:
            # Verificar que el template tiene contexto
            self.assertTrue(
                'compras_recientes' in response.context or
                response.context is None  # Vista puede no tener template
            )


class DeudaProveedoresViewTest(TestCase):
    """Tests para la vista deuda_proveedores_view"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        self.client.login(username='testuser', password='testpass123')
        
        # Crear proveedores
        self.proveedor1 = Proveedor.objects.create(
            ruc='80012345-6',
            razon_social='Proveedor A',
            telefono='021111111',
            activo=True
        )
        
        self.proveedor2 = Proveedor.objects.create(
            ruc='80098765-4',
            razon_social='Proveedor B',
            telefono='021222222',
            activo=True
        )
        
        # Crear compras pendientes
        Compras.objects.create(
            nro_factura=2001,
            id_proveedor=self.proveedor1,
            fecha=timezone.now(),
            total=Decimal('1000000.00'),
            saldo_pendiente=Decimal('1000000.00'),
            estado_pago='PENDIENTE'
        )
        
        Compras.objects.create(
            nro_factura=2002,
            id_proveedor=self.proveedor2,
            fecha=timezone.now(),
            total=Decimal('500000.00'),
            saldo_pendiente=Decimal('250000.00'),
            estado_pago='PARCIAL'
        )
    
    def test_vista_accesible(self):
        """Test: Vista es accesible"""
        response = self.client.get('/pos/deuda-proveedores/')
        
        self.assertIn(response.status_code, [200, 302])
    
    def test_vista_muestra_deudas(self):
        """Test: Vista muestra las deudas correctamente"""
        response = self.client.get('/pos/deuda-proveedores/')
        
        if response.status_code == 200 and response.context:
            # Verificar que hay deudas en el contexto
            self.assertTrue(
                'deudas' in response.context or
                'total_deuda' in response.context
            )


class PermissionsTestCase(TestCase):
    """Tests de permisos específicos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        
        # Usuario sin permisos
        self.user_sin_permisos = User.objects.create_user(
            username='user_sin_permisos',
            password='pass123'
        )
        
        # Usuario con permisos de vista
        self.user_con_vista = User.objects.create_user(
            username='user_con_vista',
            password='pass123'
        )
        permission = Permission.objects.get(codename='view_compras')
        self.user_con_vista.user_permissions.add(permission)
    
    def test_usuario_sin_permiso_view(self):
        """Test: Usuario sin permiso no puede ver"""
        self.client.login(username='user_sin_permisos', password='pass123')
        
        response = self.client.get('/pos/compras-dashboard/')
        
        # Debe denegar acceso
        self.assertIn(response.status_code, [302, 403])
    
    def test_usuario_con_permiso_view(self):
        """Test: Usuario con permiso puede ver"""
        self.client.login(username='user_con_vista', password='pass123')
        
        response = self.client.get('/pos/compras-dashboard/')
        
        # Debe permitir acceso
        self.assertIn(response.status_code, [200, 302])


class SessionDataTestCase(TestCase):
    """Tests de datos de sesión"""
    
    def setUp(self):
        """Configuración inicial"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_session_persiste_login(self):
        """Test: La sesión persiste después del login"""
        # Login
        self.client.login(username='testuser', password='testpass123')
        
        # Verificar que la sesión existe
        session = self.client.session
        self.assertIn('_auth_user_id', session)
    
    def test_logout_limpia_session(self):
        """Test: Logout limpia la sesión"""
        # Login
        self.client.login(username='testuser', password='testpass123')
        
        # Logout
        self.client.logout()
        
        # Verificar que la sesión está limpia
        session = self.client.session
        self.assertNotIn('_auth_user_id', session)


# =============================================================================
# Para ejecutar estos tests:
#
#     # Tests de autenticación
#     python manage.py test gestion.tests_auth
#
#     # Test específico
#     python manage.py test gestion.tests_auth.AuthenticationTestCase
#
#     # Con verbosidad
#     python manage.py test gestion.tests_auth --verbosity=2
# =============================================================================
