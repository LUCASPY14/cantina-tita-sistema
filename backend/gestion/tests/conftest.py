"""
Fixtures para tests de gestion
"""
import pytest
from decimal import Decimal
from django.utils import timezone

from gestion.models import (
    Cliente, TipoCliente, ListaPrecios, TipoRolGeneral, Empleado,
    TiposPago, MediosPago
)


@pytest.fixture
def tipo_cliente():
    """Tipo de cliente"""
    tipo, created = TipoCliente.objects.get_or_create(
        nombre_tipo='Regular',
        defaults={'activo': True}
    )
    return tipo


@pytest.fixture
def lista_precios():
    """Lista de precios de prueba"""
    from django.utils import timezone
    lista, created = ListaPrecios.objects.get_or_create(
        nombre_lista='Lista Test',
        defaults={
            'moneda': 'PYG',
            'activo': True
        }
    )
    return lista


@pytest.fixture
def cliente(tipo_cliente, lista_precios):
    """Cliente de prueba"""
    cliente, created = Cliente.objects.get_or_create(
        ruc_ci='1234567',
        defaults={
            'id_tipo_cliente': tipo_cliente,
            'id_lista': lista_precios,
            'nombres': 'Juan',
            'apellidos': 'Pérez',
            'ciudad': 'Asunción',
            'telefono': '0981234567',
            'limite_credito': Decimal('1000000.00'),
            'activo': True
        }
    )
    return cliente


@pytest.fixture
def tipo_rol():
    """Tipo de rol general"""
    rol, created = TipoRolGeneral.objects.get_or_create(
        nombre_rol='Empleado',
        defaults={'activo': True}
    )
    return rol


@pytest.fixture
def empleado(tipo_rol):
    """Empleado de prueba"""
    emp, created = Empleado.objects.get_or_create(
        usuario='jperez',
        defaults={
            'id_rol': tipo_rol,
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'contrasena_hash': 'pbkdf2_sha256$',
            'telefono': '0981234567',
            'email': 'juan@cantina.com',
            'activo': True
        }
    )
    return emp


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
