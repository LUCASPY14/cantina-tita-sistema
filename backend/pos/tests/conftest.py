"""
Fixtures para tests de POS
"""
import pytest
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model

from pos.models import Venta, DetalleVenta, PagoVenta
from gestion.models import (
    Cliente, TipoCliente, Producto, Categoria, UnidadMedida,
    TiposPago, Empleado, MediosPago, CierresCaja, Tarjeta, TipoRolGeneral,
    Impuesto, PreciosPorLista, ListaPrecios
)

User = get_user_model()


# ==================== FIXTURES BÁSICAS ====================

@pytest.fixture
def user():
    """Usuario de prueba"""
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )


@pytest.fixture
def tipo_cliente():
    """Tipo de cliente"""
    return TipoCliente.objects.create(
        nombre_tipo='Alumno',
        activo=True
    )


@pytest.fixture
def lista_precios():
    """Lista de precios de prueba"""
    from gestion.models import ListaPrecios
    return ListaPrecios.objects.create(
        nombre_lista='Lista Test',
        moneda='PYG',
        activo=True
    )


@pytest.fixture
def cliente(tipo_cliente, lista_precios):
    """Cliente de prueba"""
    return Cliente.objects.create(
        nombres='Juan',
        apellidos='Pérez',
        ruc_ci='1234567',
        id_tipo_cliente=tipo_cliente,
        id_lista=lista_precios,
        telefono='0981123456',
        email='juan@example.com',
        direccion='Asunción',
        ciudad='Asunción',
        activo=True
    )


@pytest.fixture
def categoria():
    """Categoría de producto"""
    cat, created = Categoria.objects.get_or_create(
        nombre='Bebidas',
        defaults={'activo': True}
    )
    return cat

@pytest.fixture
def unidad_medida():
    """Unidad de medida"""
    unidad, created = UnidadMedida.objects.get_or_create(
        nombre='Unidad',
        defaults={'abreviatura': 'u', 'activo': True}
    )
    return unidad


@pytest.fixture
def impuesto():
    """Impuesto (IVA 10%)"""
    from django.utils import timezone
    imp, created = Impuesto.objects.get_or_create(
        nombre_impuesto='IVA 10%',
        defaults={
            'porcentaje': 10.0,
            'vigente_desde': timezone.now().date(),
            'activo': True
        }
    )
    return imp


@pytest.fixture
def producto(categoria, unidad_medida, impuesto, lista_precios):
    """Producto de prueba"""
    from django.utils import timezone
    
    prod, created = Producto.objects.get_or_create(
        codigo_barra='PROD001',
        defaults={
            'descripcion': 'Coca Cola 500ml',
            'id_categoria': categoria,
            'id_unidad_medida': unidad_medida,
            'id_impuesto': impuesto,
            'stock_minimo': 10,
            'activo': True
        }
    )
    
    # Crear precio si no existe
    if created:
        PreciosPorLista.objects.create(
            id_producto=prod,
            id_lista_precios=lista_precios,
            precio_venta=5000,
            fecha_vigencia=timezone.now()
        )
    
    return prod


@pytest.fixture
def tipo_pago():
    """Tipo de pago"""
    tipo, created = TiposPago.objects.get_or_create(
        descripcion='Efectivo',
        defaults={'activo': True}
    )
    return tipo


@pytest.fixture
def medio_pago():
    """Medio de pago"""
    medio, created = MediosPago.objects.get_or_create(
        descripcion='Efectivo',
        defaults={
            'genera_comision': False,
            'requiere_validacion': False,
            'activo': True
        }
    )
    return medio


@pytest.fixture
def tipo_rol_cajero():
    """Tipo de rol para cajero"""
    rol, created = TipoRolGeneral.objects.get_or_create(
        nombre_rol='Cajero',
        defaults={'activo': True}
    )
    return rol


@pytest.fixture
def tipo_rol_supervisor():
    """Tipo de rol para supervisor"""
    rol, created = TipoRolGeneral.objects.get_or_create(
        nombre_rol='Supervisor',
        defaults={'activo': True}
    )
    return rol


@pytest.fixture
def cajero(tipo_rol_cajero):
    """Empleado cajero"""
    return Empleado.objects.create(
        id_rol=tipo_rol_cajero,
        nombre='María',
        apellido='González',
        usuario='mgonzalez',
        contrasena_hash='pbkdf2_sha256$',  # Hash dummy para tests
        telefono='0981654321',
        email='maria@cantina.com',
        activo=True
    )


@pytest.fixture
def supervisor(tipo_rol_supervisor):
    """Empleado supervisor"""
    return Empleado.objects.create(
        id_rol=tipo_rol_supervisor,
        nombre='Carlos',
        apellido='Ramírez',
        usuario='cramirez',
        contrasena_hash='pbkdf2_sha256$',
        telefono='0981987654',
        email='carlos@cantina.com',
        activo=True
    )


# ==================== FIXTURES DE VENTAS ====================

@pytest.fixture
def venta_contado(cliente, cajero, tipo_pago):
    """Venta al contado de prueba"""
    return Venta.objects.create(
        id_cliente=cliente,
        id_tipo_pago=tipo_pago,
        id_empleado_cajero=cajero,
        fecha=timezone.now(),
        monto_total=50000,
        saldo_pendiente=50000,
        estado_pago='PENDIENTE',
        estado='PROCESADO',
        tipo_venta='CONTADO',
        genera_factura_legal=False
    )


@pytest.fixture
def venta_credito(cliente, cajero, supervisor, tipo_pago):
    """Venta a crédito de prueba"""
    return Venta.objects.create(
        id_cliente=cliente,
        id_tipo_pago=tipo_pago,
        id_empleado_cajero=cajero,
        fecha=timezone.now(),
        monto_total=100000,
        saldo_pendiente=100000,
        estado_pago='PENDIENTE',
        estado='PROCESADO',
        tipo_venta='CREDITO',
        autorizado_por=supervisor,
        motivo_credito='Cliente frecuente con buen historial',
        genera_factura_legal=False
    )


@pytest.fixture
def venta_con_detalles(venta_contado, producto):
    """Venta con detalles"""
    DetalleVenta.objects.create(
        id_venta=venta_contado,
        id_producto=producto,
        cantidad=Decimal('5.000'),
        precio_unitario=10000,
        subtotal_total=50000,
    )
    return venta_contado


@pytest.fixture
def venta_con_pago(venta_contado, medio_pago):
    """Venta con un pago aplicado"""
    PagoVenta.objects.create(
        id_venta=venta_contado,
        id_medio_pago=medio_pago,
        monto_aplicado=50000,
        fecha_pago=timezone.now(),
        estado='PROCESADO'
    )
    
    # Actualizar estado de la venta
    venta_contado.saldo_pendiente = 0
    venta_contado.estado_pago = 'PAGADA'
    venta_contado.save()
    
    return venta_contado


# ==================== FIXTURES DE API ====================

@pytest.fixture
def api_client():
    """Cliente de API REST"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, user):
    """Cliente de API autenticado"""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def venta_data(cliente, cajero, tipo_pago, producto):
    """Datos para crear venta via API"""
    return {
        'id_cliente': cliente.id_cliente,
        'id_tipo_pago': tipo_pago.id_tipo_pago,
        'id_empleado_cajero': cajero.id_empleado,
        'tipo_venta': 'CONTADO',
        'detalles': [
            {
                'id_producto': producto.id_producto,
                'cantidad': '2.000',
                'precio_unitario': 5000,
            }
        ]
    }
