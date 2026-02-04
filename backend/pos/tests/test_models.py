"""
Tests para modelos POS
"""
import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from pos.models import Venta, DetalleVenta, PagoVenta
from gestion.models import (
    Cliente, Producto, TiposPago, Empleado, MediosPago,
    CierresCaja, Tarjeta
)


@pytest.mark.django_db
class TestVentaModel:
    """Tests para el modelo Venta"""
    
    def test_crear_venta_contado(self, venta_contado):
        """Test crear venta al contado"""
        assert venta_contado.id_venta is not None
        assert venta_contado.tipo_venta == 'CONTADO'
        assert venta_contado.estado == 'PROCESADO'
        assert venta_contado.estado_pago == 'PENDIENTE'
        assert venta_contado.monto_total == 50000
        # El __str__ formatea con comas, buscar '50,000' o simplemente verificar que tiene contenido
        assert 'Juan' in str(venta_contado)
        assert 'Venta' in str(venta_contado)
    
    def test_crear_venta_credito_sin_autorizacion(self, cliente, cajero, tipo_pago):
        """Test crear venta a crédito sin autorización debe fallar"""
        venta = Venta(
            id_cliente=cliente,
            id_tipo_pago=tipo_pago,
            id_empleado_cajero=cajero,
            tipo_venta='CREDITO',
            monto_total=100000,
            saldo_pendiente=100000,
        )
        
        with pytest.raises(ValidationError) as exc_info:
            venta.save()
        
        assert 'autorizado_por' in str(exc_info.value)
    
    def test_crear_venta_credito_con_autorizacion(self, venta_credito, supervisor):
        """Test crear venta a crédito con autorización"""
        assert venta_credito.id_venta is not None
        assert venta_credito.tipo_venta == 'CREDITO'
        assert venta_credito.autorizado_por == supervisor
        assert venta_credito.motivo_credito is not None
    
    def test_validacion_saldo_mayor_total(self, cliente, cajero, tipo_pago):
        """Test validar que saldo no sea mayor al total"""
        venta = Venta(
            id_cliente=cliente,
            id_tipo_pago=tipo_pago,
            id_empleado_cajero=cajero,
            tipo_venta='CONTADO',
            monto_total=50000,
            saldo_pendiente=100000,  # Saldo mayor al total
        )
        
        with pytest.raises(ValidationError) as exc_info:
            venta.save()
        
        assert 'saldo_pendiente' in str(exc_info.value)
    
    def test_propiedades_calculadas(self, venta_contado):
        """Test propiedades calculadas total_pagado y porcentaje_pagado"""
        venta_contado.estado_pago = 'PARCIAL'  # Cambiar antes de modificar saldo
        venta_contado.saldo_pendiente = 30000
        venta_contado.save()
        
        assert venta_contado.total_pagado == 20000  # 50000 - 30000
        assert venta_contado.porcentaje_pagado == 40.0  # 20000/50000 * 100
    
    def test_str_representation(self, venta_contado):
        """Test representación en string"""
        str_repr = str(venta_contado)
        assert f'Venta #{venta_contado.id_venta}' in str_repr
        assert venta_contado.id_cliente.nombre_completo in str_repr


@pytest.mark.django_db
class TestDetalleVentaModel:
    """Tests para el modelo DetalleVenta"""
    
    def test_crear_detalle_venta(self, venta_contado, producto):
        """Test crear detalle de venta"""
        detalle = DetalleVenta.objects.create(
            id_venta=venta_contado,
            id_producto=producto,
            cantidad=Decimal('2.000'),
            precio_unitario=10000,
            subtotal_total=20000,
        )
        
        assert detalle.id_detalle is not None
        assert detalle.cantidad == Decimal('2.000')
        assert detalle.subtotal_total == 20000
    
    def test_calculo_automatico_subtotal(self, venta_contado, producto):
        """Test que el subtotal se calcula automáticamente"""
        detalle = DetalleVenta(
            id_venta=venta_contado,
            id_producto=producto,
            cantidad=Decimal('3.000'),
            precio_unitario=15000,
        )
        detalle.save()
        
        assert detalle.subtotal_total == 45000  # 3 * 15000
    
    def test_validacion_cantidad_negativa(self, venta_contado, producto):
        """Test validar cantidad positiva"""
        detalle = DetalleVenta(
            id_venta=venta_contado,
            id_producto=producto,
            cantidad=Decimal('-1.000'),
            precio_unitario=10000,
        )
        
        with pytest.raises(ValidationError) as exc_info:
            detalle.save()
        
        assert 'cantidad' in str(exc_info.value)
    
    def test_validacion_precio_negativo(self, venta_contado, producto):
        """Test validar precio positivo"""
        detalle = DetalleVenta(
            id_venta=venta_contado,
            id_producto=producto,
            cantidad=Decimal('1.000'),
            precio_unitario=-5000,
        )
        
        with pytest.raises(ValidationError) as exc_info:
            detalle.save()
        
        assert 'precio_unitario' in str(exc_info.value)
    
    def test_unique_together_venta_producto(self, venta_contado, producto):
        """Test que no se puedan duplicar productos en una venta"""
        DetalleVenta.objects.create(
            id_venta=venta_contado,
            id_producto=producto,
            cantidad=Decimal('1.000'),
            precio_unitario=10000,
            subtotal_total=10000,
        )
        
        # Intentar crear otro detalle con el mismo producto
        with pytest.raises(Exception):  # IntegrityError
            DetalleVenta.objects.create(
                id_venta=venta_contado,
                id_producto=producto,
                cantidad=Decimal('2.000'),
                precio_unitario=10000,
                subtotal_total=20000,
            )


@pytest.mark.django_db
class TestPagoVentaModel:
    """Tests para el modelo PagoVenta"""
    
    def test_crear_pago_venta(self, venta_contado, medio_pago):
        """Test crear pago de venta"""
        pago = PagoVenta.objects.create(
            id_venta=venta_contado,
            id_medio_pago=medio_pago,
            monto_aplicado=50000,
        )
        
        assert pago.id_pago_venta is not None
        assert pago.monto_aplicado == 50000
        assert pago.estado == 'PROCESADO'
    
    def test_validacion_monto_mayor_saldo(self, venta_contado, medio_pago):
        """Test validar que pago no exceda saldo pendiente"""
        venta_contado.estado_pago = 'PARCIAL'  # Cambiar antes de modificar saldo
        venta_contado.saldo_pendiente = 30000
        venta_contado.save()
        
        pago = PagoVenta(
            id_venta=venta_contado,
            id_medio_pago=medio_pago,
            monto_aplicado=40000,  # Mayor al saldo
        )
        
        with pytest.raises(ValidationError) as exc_info:
            pago.save()
        
        assert 'monto_aplicado' in str(exc_info.value)
    
    def test_validacion_monto_negativo(self, venta_contado, medio_pago):
        """Test validar monto positivo"""
        pago = PagoVenta(
            id_venta=venta_contado,
            id_medio_pago=medio_pago,
            monto_aplicado=-10000,
        )
        
        with pytest.raises(ValidationError) as exc_info:
            pago.save()
        
        assert 'monto_aplicado' in str(exc_info.value)
    
    def test_str_representation(self, venta_contado, medio_pago):
        """Test representación en string"""
        pago = PagoVenta.objects.create(
            id_venta=venta_contado,
            id_medio_pago=medio_pago,
            monto_aplicado=25000,
        )
        
        str_repr = str(pago)
        assert f'Pago {pago.id_pago_venta}' in str_repr
        assert f'Venta #{venta_contado.id_venta}' in str_repr
