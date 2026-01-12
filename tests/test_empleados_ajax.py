"""
Tests para endpoints AJAX de gestión de empleados
"""
import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from gestion.models import Empleado, TipoRolGeneral, Cajas
import bcrypt


class TestEmpleadoAjaxEndpoints(TestCase):
    """Tests para endpoints AJAX de empleados"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear roles
        self.rol_admin = TipoRolGeneral.objects.create(
            nombre='Administrador'
        )
        
        self.rol_cajero = TipoRolGeneral.objects.create(
            nombre='Cajero'
        )
        
        # Crear empleado admin
        password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.admin = Empleado.objects.create(
            nombre_usuario='admin_test',
            contrasena_hash=password_hash,
            id_rol=self.rol_admin,
            activo=True
        )
        
        # Crear empleado para editar
        self.empleado_test = Empleado.objects.create(
            nombre_usuario='empleado_editar',
            contrasena_hash=password_hash,
            id_rol=self.rol_cajero,
            activo=True
        )
        
        # Crear caja
        self.caja = Cajas.objects.create(
            nombre_caja='Caja 1',
            activo=True
        )
        
        # Usuario Django para autenticación
        self.user = User.objects.create_user(
            username='admin_test',
            password='admin123'
        )
        
        # Cliente de testing
        self.client = Client()
        self.client.login(username='admin_test', password='admin123')
    
    def test_obtener_empleado_ajax_success(self):
        """Test: Obtener datos de empleado vía AJAX (GET)"""
        response = self.client.get(
            f'/empleados/{self.empleado_test.id_empleado}/ajax/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['empleado']['nombre_usuario'], 'empleado_editar')
        self.assertEqual(data['empleado']['id_rol'], 1)
        self.assertEqual(data['empleado']['rol_descripcion'], 'Cajero')
    
    def test_obtener_empleado_ajax_not_found(self):
        """Test: Obtener empleado inexistente vía AJAX"""
        response = self.client.get(
            '/empleados/99999/ajax/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('no encontrado', data['message'].lower())
    
    def test_editar_empleado_ajax_success(self):
        """Test: Editar empleado vía AJAX (POST)"""
        response = self.client.post(
            f'/empleados/{self.empleado_test.id_empleado}/editar/',
            {
                'nombre_usuario': 'empleado_modificado',
                'id_rol': 2,  # Cambiar a Gerente
                'id_caja': self.caja.id_caja
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['empleado']['nombre_usuario'], 'empleado_modificado')
        
        # Verificar en base de datos
        self.empleado_test.refresh_from_db()
        self.assertEqual(self.empleado_test.nombre_usuario, 'empleado_modificado')
        self.assertEqual(self.empleado_test.id_rol.id_rol, 2)
        self.assertEqual(self.empleado_test.id_caja, self.caja)
    
    def test_editar_empleado_ajax_nombre_duplicado(self):
        """Test: Editar empleado con nombre de usuario ya existente"""
        # Crear otro empleado
        password_hash = bcrypt.hashpw('test123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        otro_empleado = Empleado.objects.create(
            nombre_usuario='otro_empleado',
            contrasena_hash=password_hash,
            id_rol=self.rol_cajero,
            activo=True
        )
        
        # Intentar cambiar nombre a uno que ya existe
        response = self.client.post(
            f'/empleados/{self.empleado_test.id_empleado}/editar/',
            {
                'nombre_usuario': 'otro_empleado',
                'id_rol': 1
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('ya existe', data['message'].lower())
    
    def test_editar_empleado_ajax_campos_vacios(self):
        """Test: Editar empleado con campos obligatorios vacíos"""
        response = self.client.post(
            f'/empleados/{self.empleado_test.id_empleado}/editar/',
            {
                'nombre_usuario': '',
                'id_rol': ''
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('obligatorios', data['message'].lower())
    
    def test_resetear_password_ajax_success(self):
        """Test: Resetear contraseña vía AJAX"""
        response = self.client.post(
            f'/empleados/{self.empleado_test.id_empleado}/resetear-password/',
            {
                'nueva_password': 'nuevapass123',
                'confirmar_password': 'nuevapass123'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Verificar que la contraseña cambió
        self.empleado_test.refresh_from_db()
        self.assertTrue(
            bcrypt.checkpw(
                'nuevapass123'.encode('utf-8'),
                self.empleado_test.contrasena_hash.encode('utf-8')
            )
        )
    
    def test_resetear_password_ajax_no_coinciden(self):
        """Test: Resetear contraseña con passwords que no coinciden"""
        response = self.client.post(
            f'/empleados/{self.empleado_test.id_empleado}/resetear-password/',
            {
                'nueva_password': 'password1',
                'confirmar_password': 'password2'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('no coinciden', data['message'].lower())
    
    def test_resetear_password_ajax_muy_corta(self):
        """Test: Resetear contraseña muy corta"""
        response = self.client.post(
            f'/empleados/{self.empleado_test.id_empleado}/resetear-password/',
            {
                'nueva_password': '123',
                'confirmar_password': '123'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('al menos 4 caracteres', data['message'].lower())
    
    def test_toggle_estado_empleado_ajax_activar(self):
        """Test: Activar/desactivar empleado vía AJAX"""
        # Primero desactivar
        self.empleado_test.activo = False
        self.empleado_test.save()
        
        # Activar vía AJAX
        response = self.client.post(
            f'/empleados/{self.empleado_test.id_empleado}/toggle-estado/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertTrue(data['nuevo_estado'])
        
        # Verificar en base de datos
        self.empleado_test.refresh_from_db()
        self.assertTrue(self.empleado_test.activo)
    
    def test_toggle_estado_empleado_ajax_desactivar(self):
        """Test: Desactivar empleado activo"""
        # Asegurar que está activo
        self.empleado_test.activo = True
        self.empleado_test.save()
        
        # Desactivar vía AJAX
        response = self.client.post(
            f'/empleados/{self.empleado_test.id_empleado}/toggle-estado/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertFalse(data['nuevo_estado'])
        
        # Verificar en base de datos
        self.empleado_test.refresh_from_db()
        self.assertFalse(self.empleado_test.activo)


class TestPermisosAjax(TestCase):
    """Tests de permisos para endpoints AJAX"""
    
    def setUp(self):
        """Configuración inicial"""
        # Crear rol cajero (sin permisos de admin)
        self.rol_cajero = TipoRolGeneral.objects.create(
            nombre='Cajero'
        )
        
        # Crear empleado cajero
        password_hash = bcrypt.hashpw('cajero123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.cajero = Empleado.objects.create(
            nombre_usuario='cajero_sin_permisos',
            contrasena_hash=password_hash,
            id_rol=self.rol_cajero,
            activo=True
        )
        
        # Usuario Django
        self.user = User.objects.create_user(
            username='cajero_sin_permisos',
            password='cajero123'
        )
        
        self.client = Client()
        self.client.login(username='cajero_sin_permisos', password='cajero123')
    
    def test_acceso_denegado_editar_empleado(self):
        """Test: Cajero sin permisos no puede editar empleados"""
        response = self.client.post(
            f'/empleados/{self.cajero.id_empleado}/editar/',
            {
                'nombre_usuario': 'nuevo_nombre',
                'id_rol': 1
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Debe redirigir o retornar 403
        self.assertIn(response.status_code, [302, 403])
    
    def test_acceso_denegado_resetear_password(self):
        """Test: Cajero sin permisos no puede resetear passwords"""
        response = self.client.post(
            f'/empleados/{self.cajero.id_empleado}/resetear-password/',
            {
                'nueva_password': 'newpass123',
                'confirmar_password': 'newpass123'
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertIn(response.status_code, [302, 403])


# ==================== EJECUTAR TESTS ====================
# pytest test_empleados_ajax.py -v
# python manage.py test gestion.tests.test_empleados_ajax
# coverage run --source='.' manage.py test gestion.tests.test_empleados_ajax
# coverage report
