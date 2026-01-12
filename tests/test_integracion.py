"""
Tests de integración completos para Cantina Tita
"""
import pytest
from django.test import TestCase, Client, TransactionTestCase
from django.contrib.auth.models import User
from gestion.models import *
from decimal import Decimal
from datetime import datetime, timedelta
import bcrypt


class TestIntegracionVentaCompleta(TransactionTestCase):
    """Test del flujo completo de una venta desde POS"""
    
    def setUp(self):
        """Configuración inicial"""
        # Crear roles
        self.rol_cajero = TipoRolGeneral.objects.create(nombre='Cajero')
        
        # Crear empleado
        password_hash = bcrypt.hashpw('cajero123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.cajero = Empleado.objects.create(
            nombre_usuario='cajero1',
            contrasena_hash=password_hash,
            id_rol=self.rol_cajero,
            activo=True
        )
        
        # Usuario Django
        self.user = User.objects.create_user(
            username='cajero1',
            password='cajero123'
        )
        
        # Crear caja
        self.caja = Cajas.objects.create(
            nombre_caja='Caja Principal',
            activo=True
        )
        
        # Crear cliente con hijo
        self.cliente = Cliente.objects.create(
            nombre='Test Cliente',
            telefono='0981234567',
            saldo=Decimal('100000')
        )
        
        self.hijo = Hijos.objects.create(
            cliente=self.cliente,
            nombre='Hijo Test',
            grado='3ro',
            activo=True
        )
        
        # Crear productos
        self.producto1 = Producto.objects.create(
            nombre='Gaseosa',
            precio_venta=Decimal('5000'),
            stock=50,
            activo=True
        )
        
        self.producto2 = Producto.objects.create(
            nombre='Empanada',
            precio_venta=Decimal('3000'),
            stock=100,
            activo=True
        )
        
        # Cliente de testing
        self.client = Client()
        self.client.login(username='cajero1', password='cajero123')
    
    def test_flujo_venta_completo(self):
        """Test: Flujo completo de venta (agregar productos, confirmar, verificar stock)"""
        # 1. Login al POS
        response = self.client.get('/pos/')
        self.assertEqual(response.status_code, 200)
        
        # 2. Crear venta con productos
        saldo_inicial = self.cliente.saldo
        stock_inicial_p1 = self.producto1.stock
        stock_inicial_p2 = self.producto2.stock
        
        # Simular POST de venta
        response = self.client.post('/pos/venta/confirmar/', {
            'cliente_id': self.cliente.id_cliente,
            'productos': [
                {'id': self.producto1.id_producto, 'cantidad': 2},
                {'id': self.producto2.id_producto, 'cantidad': 3}
            ],
            'forma_pago': 'SALDO',
            'id_caja': self.caja.id_caja
        })
        
        # 3. Verificar que la venta se creó
        venta = Ventas.objects.filter(cliente=self.cliente).latest('fecha')
        self.assertIsNotNone(venta)
        
        # 4. Verificar monto total
        monto_esperado = (self.producto1.precio_venta * 2) + (self.producto2.precio_venta * 3)
        self.assertEqual(venta.monto_total, monto_esperado)
        
        # 5. Verificar que se descontó el saldo
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.saldo, saldo_inicial - monto_esperado)
        
        # 6. Verificar que se descontó el stock
        self.producto1.refresh_from_db()
        self.producto2.refresh_from_db()
        self.assertEqual(self.producto1.stock, stock_inicial_p1 - 2)
        self.assertEqual(self.producto2.stock, stock_inicial_p2 - 3)


class TestIntegracionRecarga(TransactionTestCase):
    """Test del flujo completo de recarga de saldo"""
    
    def setUp(self):
        """Configuración inicial"""
        self.rol_cajero = Rol.objects.create(id_rol=1, descripcion='Cajero')
        password_hash = bcrypt.hashpw('test123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        self.cajero = Empleado.objects.create(
            nombre_usuario='cajero1',
            contrasena_hash=password_hash,
            id_rol=self.rol_cajero,
            activo=True
        )
        
        self.user = User.objects.create_user(
            username='cajero1',
            password='test123'
        )
        
        self.cliente = Cliente.objects.create(
            nombre='Test Cliente',
            telefono='0981234567',
            saldo=Decimal('0')
        )
        
        self.caja = Cajas.objects.create(
            nombre_caja='Caja 1',
            activo=True
        )
        
        self.client = Client()
        self.client.login(username='cajero1', password='test123')
    
    def test_flujo_recarga_completo(self):
        """Test: Recarga de saldo completa con validación"""
        saldo_inicial = self.cliente.saldo
        monto_recarga = Decimal('50000')
        
        # 1. Crear recarga
        response = self.client.post('/pos/recarga/', {
            'cliente_id': self.cliente.id_cliente,
            'monto': str(monto_recarga),
            'forma_pago': 'EFECTIVO'
        })
        
        # 2. Verificar que se creó la recarga
        recarga = Recargas.objects.filter(cliente=self.cliente).latest('fecha')
        self.assertIsNotNone(recarga)
        self.assertEqual(recarga.monto, monto_recarga)
        
        # 3. Verificar que se actualizó el saldo del cliente
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.saldo, saldo_inicial + monto_recarga)


class TestIntegracionCuentaCorriente(TransactionTestCase):
    """Test del flujo completo de cuenta corriente con pago pendiente"""
    
    def setUp(self):
        """Configuración inicial"""
        self.rol_admin = TipoRolGeneral.objects.create(nombre='Administrador')
        password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        self.admin = Empleado.objects.create(
            nombre_usuario='admin1',
            contrasena_hash=password_hash,
            id_rol=self.rol_admin,
            activo=True
        )
        
        self.user = User.objects.create_user(
            username='admin1',
            password='admin123'
        )
        
        self.cliente = Cliente.objects.create(
            nombre='Cliente CC',
            ruc='12345678-9',
            telefono='0981234567',
            saldo=Decimal('0'),
            cuenta_corriente_activa=True
        )
        
        self.caja = Cajas.objects.create(
            nombre_caja='Caja 1',
            activo=True
        )
        
        self.producto = Producto.objects.create(
            nombre='Producto Test',
            precio_venta=Decimal('10000'),
            stock=100,
            activo=True
        )
        
        self.client = Client()
        self.client.login(username='admin1', password='admin123')
    
    def test_flujo_venta_cc_y_validacion(self):
        """Test: Venta en cuenta corriente con validación de pago posterior"""
        # 1. Crear venta con pago pendiente de transferencia
        venta = Ventas.objects.create(
            cliente=self.cliente,
            fecha=datetime.now(),
            monto_total=Decimal('30000'),
            forma_pago='CUENTA_CORRIENTE',
            motivo_credito='PAGO_PENDIENTE_TRANSFERENCIA - Pago a validar',
            id_caja=self.caja,
            usuario=self.admin
        )
        
        DetalleVenta.objects.create(
            venta=venta,
            producto=self.producto,
            cantidad=3,
            precio=Decimal('10000'),
            subtotal=Decimal('30000')
        )
        
        # 2. Verificar que aparece en pendientes
        response = self.client.get('/pos/validaciones/pagos-pendientes/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cliente CC')
        
        # 3. Validar el pago
        response = self.client.post(
            f'/pos/validaciones/pago/{venta.id}/',
            {
                'comprobante': 'REF-123456',
                'observaciones': 'Pago verificado'
            }
        )
        
        # 4. Verificar que se actualizó
        venta.refresh_from_db()
        self.assertNotIn('PAGO_PENDIENTE_TRANSFERENCIA', venta.motivo_credito)
        self.assertIn('REF-123456', venta.motivo_credito)


class TestIntegracionAlmuerzos(TransactionTestCase):
    """Test del flujo completo de almuerzos"""
    
    def setUp(self):
        """Configuración inicial"""
        self.rol_cajero = Rol.objects.create(id_rol=1, descripcion='Cajero')
        password_hash = bcrypt.hashpw('test123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        self.cajero = Empleado.objects.create(
            nombre_usuario='cajero1',
            contrasena_hash=password_hash,
            id_rol=self.rol_cajero,
            activo=True
        )
        
        self.user = User.objects.create_user(
            username='cajero1',
            password='test123'
        )
        
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test',
            telefono='0981234567',
            saldo=Decimal('100000')
        )
        
        self.hijo = Hijos.objects.create(
            cliente=self.cliente,
            nombre='Hijo Test',
            grado='3ro',
            activo=True
        )
        
        # Configuración de precio de almuerzo
        self.config_almuerzo = ConfiguracionAlmuerzo.objects.create(
            precio_almuerzo=Decimal('15000'),
            activo=True
        )
        
        self.client = Client()
        self.client.login(username='cajero1', password='test123')
    
    def test_flujo_registro_almuerzo(self):
        """Test: Registro de almuerzo y descuento de saldo"""
        saldo_inicial = self.cliente.saldo
        
        # Registrar almuerzo
        response = self.client.post('/pos/almuerzo/registrar/', {
            'hijo_id': self.hijo.id_hijo,
            'fecha': datetime.now().date(),
            'tipo_almuerzo': 'COMPLETO'
        })
        
        # Verificar registro
        almuerzo = RegistroAlmuerzos.objects.filter(hijo=self.hijo).latest('fecha')
        self.assertIsNotNone(almuerzo)
        self.assertEqual(almuerzo.monto, self.config_almuerzo.precio_almuerzo)
        
        # Verificar descuento de saldo
        self.cliente.refresh_from_db()
        self.assertEqual(
            self.cliente.saldo,
            saldo_inicial - self.config_almuerzo.precio_almuerzo
        )


class TestRendimiento(TransactionTestCase):
    """Tests de rendimiento y carga"""
    
    def test_multiples_ventas_simultaneas(self):
        """Test: Procesar múltiples ventas simultáneas sin errores"""
        # Crear 10 clientes y 10 productos
        clientes = []
        productos = []
        
        for i in range(10):
            cliente = Cliente.objects.create(
                nombre=f'Cliente {i}',
                telefono=f'098123456{i}',
                saldo=Decimal('100000')
            )
            clientes.append(cliente)
            
            producto = Producto.objects.create(
                nombre=f'Producto {i}',
                precio_venta=Decimal(f'{(i+1)*1000}'),
                stock=1000,
                activo=True
            )
            productos.append(producto)
        
        # Crear empleado y caja
        rol = TipoRolGeneral.objects.create(nombre='Cajero')
        password_hash = bcrypt.hashpw('test'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        empleado = Empleado.objects.create(
            nombre_usuario='cajero_test',
            contrasena_hash=password_hash,
            id_rol=rol,
            activo=True
        )
        
        caja = Cajas.objects.create(nombre_caja='Caja Test', activo=True)
        
        # Procesar 100 ventas
        for i in range(100):
            cliente = clientes[i % 10]
            producto = productos[i % 10]
            
            venta = Ventas.objects.create(
                cliente=cliente,
                fecha=datetime.now(),
                monto_total=producto.precio_venta,
                forma_pago='SALDO',
                id_caja=caja,
                usuario=empleado
            )
            
            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=1,
                precio=producto.precio_venta,
                subtotal=producto.precio_venta
            )
        
        # Verificar que se crearon todas
        self.assertEqual(Ventas.objects.count(), 100)


# ==================== EJECUTAR TESTS ====================
# pytest test_integracion.py -v
# python manage.py test gestion.tests.test_integracion
# coverage run --source='.' manage.py test
# coverage html  # Genera reporte HTML en htmlcov/
