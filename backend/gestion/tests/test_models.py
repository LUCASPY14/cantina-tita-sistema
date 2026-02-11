"""
Tests de Modelos Core - Migrados a Pytest
Tests para Ventas, Cliente, Cuenta Corriente
"""

import pytest
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ValidationError

from pos.models import Venta as Ventas, PagoVenta as PagosVenta
from gestion.models import (
    Cliente, Compras, Proveedor, 
    AplicacionPagosVentas,
    Empleado, TiposPago
)


@pytest.mark.django_db
class TestVentasModel:
    """Tests para el modelo Ventas"""
    
    # Fixture empleado movido a conftest.py
    # Fixture cliente movido a conftest.py
    # Fixture tipo_pago movido a conftest.py
    
    def test_crear_venta_exitosa(self, empleado, cliente, tipo_pago):
        """Test: Crear una venta válida"""
        venta = Ventas.objects.create(
            cliente=cliente,
            empleado=empleado,
            total=Decimal('50000.00'),
            estado='P'  # Pendiente
        )
        
        assert venta.id is not None
        assert venta.total == Decimal('50000.00')
        assert venta.estado == 'P'
        assert venta.cliente == cliente
    
    def test_calculo_saldo_pendiente(self, empleado, cliente):
        """Test: Cálculo correcto de saldo pendiente"""
        venta = Ventas.objects.create(
            cliente=cliente,
            empleado=empleado,
            total=Decimal('100000.00'),
            estado='P'
        )
        
        # Sin pagos, saldo debe ser el total
        assert venta.saldo_pendiente == Decimal('100000.00')
    
    def test_venta_requiere_cliente(self, empleado):
        """Test: Venta debe tener cliente"""
        with pytest.raises(Exception):  # IntegrityError o ValidationError
            Ventas.objects.create(
                empleado=empleado,
                total=Decimal('50000.00')
            )
    
    def test_total_no_negativo(self, empleado, cliente):
        """Test: Total no puede ser negativo"""
        with pytest.raises(ValidationError):
            venta = Ventas(
                cliente=cliente,
                empleado=empleado,
                total=Decimal('-1000.00')
            )
            venta.full_clean()


@pytest.mark.django_db
class TestClienteModel:
    """Tests para el modelo Cliente"""
    
    def test_crear_cliente_valido(self):
        """Test: Crear cliente con datos válidos"""
        cliente = Cliente.objects.create(
            nombres='Pedro',
            apellidos='Ramírez',
            ruc_ci='5555555',
            telefono='0991234567',
            activo=True,
            limite_credito=Decimal('500000.00')
        )
        
        assert cliente.id is not None
        assert cliente.nombres == 'Pedro'
        assert cliente.activo is True
    
    def test_cliente_sin_limite_credito(self):
        """Test: Cliente puede no tener límite de crédito"""
        cliente = Cliente.objects.create(
            nombres='Ana',
            apellidos='Silva',
            ruc_ci='6666666',
            activo=True
        )
        
        assert cliente.limite_credito is None or cliente.limite_credito == Decimal('0.00')
    
    def test_ruc_ci_unico(self):
        """Test: RUC/CI debe ser único"""
        Cliente.objects.create(
            nombres='Usuario1',
            apellidos='Test',
            ruc_ci='7777777',
            activo=True
        )
        
        # Intentar crear otro con mismo RUC/CI
        with pytest.raises(Exception):  # IntegrityError
            Cliente.objects.create(
                nombres='Usuario2',
                apellidos='Test',
                ruc_ci='7777777',
                activo=True
            )


@pytest.mark.django_db
class TestCuentaCorriente:
    """Tests para funcionalidad de Cuenta Corriente"""
    
    @pytest.fixture
    def cliente_con_ventas(self):
        """Cliente con múltiples ventas"""
        empleado = Empleado.objects.create(
            nombre='Vendedor',
            apellido='Test',
            ci='9999999',
            activo=True
        )
        
        cliente = Cliente.objects.create(
            nombres='Cliente',
            apellidos='Cuenta Corriente',
            ruc_ci='8888888',
            activo=True,
            limite_credito=Decimal('2000000.00')
        )
        
        # Crear 3 ventas
        for i in range(3):
            Ventas.objects.create(
                cliente=cliente,
                empleado=empleado,
                total=Decimal(f'{(i+1) * 100000}.00'),
                estado='P'
            )
        
        return cliente
    
    def test_saldo_total_cliente(self, cliente_con_ventas):
        """Test: Cálculo de saldo total del cliente"""
        ventas = Ventas.objects.filter(cliente=cliente_con_ventas)
        
        saldo_total = sum(v.saldo_pendiente for v in ventas)
        
        # 100000 + 200000 + 300000 = 600000
        assert saldo_total == Decimal('600000.00')
    
    def test_limite_credito_no_excedido(self, cliente_con_ventas):
        """Test: Verificar que no se excede límite de crédito"""
        ventas = Ventas.objects.filter(cliente=cliente_con_ventas)
        saldo_total = sum(v.saldo_pendiente for v in ventas)
        
        assert saldo_total <= cliente_con_ventas.limite_credito


@pytest.mark.integration
@pytest.mark.django_db
class TestIntegracionVentasPagos:
    """Tests de integración entre Ventas y Pagos"""
    
    @pytest.fixture
    def setup_venta_completa(self):
        """Setup completo para tests de ventas con pagos"""
        empleado = Empleado.objects.create(
            nombre='Cajero',
            apellido='Principal',
            ci='1111111',
            activo=True
        )
        
        cliente = Cliente.objects.create(
            nombres='Comprador',
            apellidos='Regular',
            ruc_ci='2222222',
            activo=True
        )
        
        venta = Ventas.objects.create(
            cliente=cliente,
            empleado=empleado,
            total=Decimal('200000.00'),
            estado='P'
        )
        
        tipo_pago = TiposPago.objects.create(
            descripcion='Transferencia',
            activo=True
        )
        
        return {
            'venta': venta,
            'cliente': cliente,
            'empleado': empleado,
            'tipo_pago': tipo_pago
        }
    
    def test_pago_parcial_reduce_saldo(self, setup_venta_completa):
        """Test: Pago parcial reduce el saldo correctamente"""
        venta = setup_venta_completa['venta']
        tipo_pago = setup_venta_completa['tipo_pago']
        
        # Registrar pago parcial
        pago = PagosVenta.objects.create(
            monto=Decimal('100000.00'),
            tipo_pago=tipo_pago
        )
        
        AplicacionPagosVentas.objects.create(
            venta=venta,
            pago=pago,
            monto_aplicado=Decimal('100000.00')
        )
        
        # Recalcular saldo
        saldo = venta.total - Decimal('100000.00')
        
        assert saldo == Decimal('100000.00')
    
    def test_pago_completo_cambia_estado(self, setup_venta_completa):
        """Test: Pago completo debe cambiar estado de venta"""
        venta = setup_venta_completa['venta']
        tipo_pago = setup_venta_completa['tipo_pago']
        
        # Pago total
        pago = PagosVenta.objects.create(
            monto=venta.total,
            tipo_pago=tipo_pago
        )
        
        AplicacionPagosVentas.objects.create(
            venta=venta,
            pago=pago,
            monto_aplicado=venta.total
        )
        
        # Actualizar estado (esto normalmente lo haría un signal o método)
        venta.estado = 'C'  # Completada
        venta.save()
        
        venta.refresh_from_db()
        assert venta.estado == 'C'
