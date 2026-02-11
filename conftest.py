"""
Fixtures globales para pytest - Sistema de Gestión de Cantina

Este archivo contiene fixtures compartidos entre todos los tests.
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APIClient
from decimal import Decimal
from datetime import datetime, timedelta

User = get_user_model()


# ============================================================================
# FIXTURES DE AUTENTICACIÓN
# ============================================================================

@pytest.fixture
def user_data():
    """Datos básicos para crear usuarios."""
    return {
        'username': 'testuser',
        'email': 'test@cantina.com',
        'password': 'TestPassword123!',
        'first_name': 'Test',
        'last_name': 'User'
    }


@pytest.fixture
def user(db, user_data):
    """Usuario normal de prueba."""
    return User.objects.create_user(**user_data)


@pytest.fixture
def superuser(db):
    """Superusuario para pruebas admin."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@cantina.com',
        password='AdminPassword123!'
    )


@pytest.fixture
def staff_user(db):
    """Usuario staff para pruebas de permisos."""
    user = User.objects.create_user(
        username='staff',
        email='staff@cantina.com',
        password='StaffPassword123!',
        is_staff=True
    )
    return user


# ============================================================================
# FIXTURES DE CLIENTES
# ============================================================================

@pytest.fixture
def client():
    """Cliente Django para tests de vistas."""
    return Client()


@pytest.fixture
def authenticated_client(client, user):
    """Cliente autenticado con usuario normal."""
    client.force_login(user)
    return client


@pytest.fixture
def admin_client(client, superuser):
    """Cliente autenticado con superusuario."""
    client.force_login(superuser)
    return client


@pytest.fixture
def api_client():
    """Cliente DRF para tests de API."""
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, user):
    """Cliente API autenticado."""
    api_client.force_authenticate(user=user)
    return api_client


# ============================================================================
# FIXTURES DE MODELOS COMUNES
# ============================================================================

@pytest.fixture
def categoria_producto(db):
    """Categoría de producto de prueba."""
    from gestion.models import CategoriaProducto
    return CategoriaProducto.objects.create(
        nombre='Test Categoría',
        descripcion='Categoría de prueba',
        activo=True
    )


@pytest.fixture
def producto(db, categoria_producto):
    """Producto de prueba."""
    from gestion.models import Producto
    return Producto.objects.create(
        nombre='Test Producto',
        descripcion='Producto de prueba',
        categoria=categoria_producto,
        precio_venta=Decimal('5000.00'),
        precio_costo=Decimal('3000.00'),
        stock_actual=100,
        stock_minimo=10,
        activo=True
    )


@pytest.fixture
def cliente(db):
    """Cliente de prueba."""
    from gestion.models import Cliente
    return Cliente.objects.create(
        nombre='Juan',
        apellido='Pérez',
        documento='12345678',
        telefono='0981234567',
        email='juan.perez@example.com',
        activo=True
    )


@pytest.fixture
def tarjeta(db, cliente):
    """Tarjeta de prueba."""
    from gestion.models import Tarjeta
    return Tarjeta.objects.create(
        numero_tarjeta='1234567890',
        titular=cliente,
        saldo_actual=Decimal('10000.00'),
        activo=True
    )


@pytest.fixture
def caja(db, user):
    """Caja de prueba."""
    from gestion.models import Caja
    return Caja.objects.create(
        nombre='Caja Test',
        responsable=user,
        saldo_inicial=Decimal('50000.00'),
        saldo_actual=Decimal('50000.00'),
        estado='abierta'
    )


# ============================================================================
# FIXTURES DE VENTAS
# ============================================================================

@pytest.fixture
def venta_data(cliente, caja):
    """Datos para crear una venta."""
    return {
        'cliente': cliente,
        'caja': caja,
        'total': Decimal('15000.00'),
        'metodo_pago': 'efectivo',
        'estado': 'completada'
    }


@pytest.fixture
def venta(db, venta_data):
    """Venta de prueba."""
    from gestion.models import Venta
    return Venta.objects.create(**venta_data)


@pytest.fixture
def detalle_venta(db, venta, producto):
    """Detalle de venta de prueba."""
    from gestion.models import DetalleVenta
    return DetalleVenta.objects.create(
        venta=venta,
        producto=producto,
        cantidad=3,
        precio_unitario=producto.precio_venta,
        subtotal=producto.precio_venta * 3
    )


# ============================================================================
# FIXTURES DE PORTAL PADRES
# ============================================================================

@pytest.fixture
def padre(db, user):
    """Padre/tutor de prueba."""
    from gestion.models import Padre
    return Padre.objects.create(
        user=user,
        documento='87654321',
        telefono='0987654321',
        activo=True
    )


@pytest.fixture
def hijo(db, padre):
    """Hijo/estudiante de prueba."""
    from gestion.models import Hijo
    return Hijo.objects.create(
        padre=padre,
        nombre='María',
        apellido='Pérez',
        grado='5to',
        seccion='A',
        activo=True
    )


@pytest.fixture
def recarga_data(hijo, tarjeta):
    """Datos para crear una recarga."""
    return {
        'hijo': hijo,
        'tarjeta': tarjeta,
        'monto': Decimal('20000.00'),
        'metodo_pago': 'transferencia',
        'estado': 'pendiente'
    }


# ============================================================================
# FIXTURES DE TIEMPO
# ============================================================================

@pytest.fixture
def hoy():
    """Fecha de hoy."""
    return datetime.now().date()


@pytest.fixture
def ayer():
    """Fecha de ayer."""
    return (datetime.now() - timedelta(days=1)).date()


@pytest.fixture
def manana():
    """Fecha de mañana."""
    return (datetime.now() + timedelta(days=1)).date()


# ============================================================================
# FIXTURES DE UTILIDADES
# ============================================================================

@pytest.fixture
def mock_response():
    """Mock de response HTTP."""
    class MockResponse:
        def __init__(self, json_data=None, status_code=200):
            self.json_data = json_data or {}
            self.status_code = status_code
            
        def json(self):
            return self.json_data
    
    return MockResponse


@pytest.fixture
def freeze_time():
    """Helper para congelar tiempo en tests."""
    from unittest.mock import patch
    
    def _freeze(dt):
        return patch('django.utils.timezone.now', return_value=dt)
    
    return _freeze


# ============================================================================
# FIXTURES DE DATABASE
# ============================================================================

@pytest.fixture(scope='session')
def django_db_setup():
    """Setup de base de datos para tests."""
    from django.conf import settings
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'test_cantina_db',
        'USER': 'root',
        'PASSWORD': 'L01G05S33Vice.42',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }


@pytest.fixture
def transactional_db(request, django_db_setup, django_db_blocker):
    """
    Fixture que garantiza transacciones reales en tests.
    Útil para tests que necesitan rollback explícito.
    """
    django_db_blocker.unblock()
    request.addfinalizer(django_db_blocker.restore)


# ============================================================================
# FIXTURES DE PERFORMANCE
# ============================================================================

@pytest.fixture
def assert_num_queries():
    """Helper para verificar número de queries SQL."""
    from django.test.utils import CaptureQueriesContext
    from django.db import connection
    
    def _assert_num_queries(num):
        return CaptureQueriesContext(connection)
    
    return _assert_num_queries


# ============================================================================
# FIXTURES DE CACHE
# ============================================================================

@pytest.fixture
def clear_cache():
    """Limpiar cache entre tests."""
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


# ============================================================================
# HOOKS DE PYTEST
# ============================================================================

def pytest_configure(config):
    """Configuración global de pytest."""
    import django
    from django.conf import settings
    
    if not settings.configured:
        settings.configure(
            DEBUG_PROPAGATE_EXCEPTIONS=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.mysql',
                    'NAME': 'test_cantina_db',
                }
            },
            SECRET_KEY='test-secret-key',
            USE_TZ=True,
            TIME_ZONE='America/Asuncion',
        )
        django.setup()


def pytest_collection_modifyitems(config, items):
    """Modificar items de tests antes de ejecución."""
    for item in items:
        # Agregar marker de slow a tests que toman >5 segundos
        if 'slow' not in item.keywords:
            if hasattr(item, 'callspec'):
                if any('integration' in str(v) for v in item.callspec.params.values()):
                    item.add_marker(pytest.mark.slow)
