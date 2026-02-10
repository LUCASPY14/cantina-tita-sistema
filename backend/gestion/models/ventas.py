from django.db import models
from .base import ManagedModel


class AplicacionPagosVentas(ManagedModel):
    id_aplicacion = models.BigAutoField(db_column='id_aplicacion', primary_key=True)
    id_pago_venta = models.ForeignKey('pos.PagoVenta', on_delete=models.CASCADE, db_column='id_pago_venta')
    id_venta = models.ForeignKey('pos.Venta', on_delete=models.CASCADE, db_column='id_venta')
    monto_aplicado = models.BigIntegerField(db_column='monto_aplicado')
    
    class Meta(ManagedModel.Meta):
        db_table = 'aplicacion_pagos_ventas'


class DetalleComisionVenta(ManagedModel):
    id_detalle_comision = models.BigAutoField(db_column='id_detalle_comision', primary_key=True)
    id_pago_venta = models.ForeignKey('pos.PagoVenta', on_delete=models.CASCADE, db_column='id_pago_venta')
    id_tarifa = models.ForeignKey('TarifasComision', on_delete=models.PROTECT, db_column='id_tarifa')
    monto_base = models.BigIntegerField(db_column='monto_base')
    porcentaje_aplicado = models.DecimalField(db_column='porcentaje_aplicado', max_digits=5, decimal_places=2)
    comision_calculada = models.BigIntegerField(db_column='comision_calculada')
    
    class Meta(ManagedModel.Meta):
        db_table = 'detalle_comision_venta'


class NotasCreditoCliente(ManagedModel):
    id_nota = models.BigAutoField(db_column='id_nota', primary_key=True)
    nro_nota_credito = models.BigIntegerField(db_column='nro_nota_credito')
    id_cliente = models.ForeignKey('Cliente', on_delete=models.PROTECT, db_column='id_cliente')
    id_venta_origen = models.ForeignKey('pos.Venta', on_delete=models.PROTECT, db_column='id_venta_origen', blank=True, null=True)
    id_empleado_autoriza = models.ForeignKey('Empleado', on_delete=models.PROTECT, db_column='id_empleado_autoriza')
    fecha_emision = models.DateTimeField(db_column='fecha_emision')
    motivo = models.TextField(db_column='motivo')
    monto_total = models.BigIntegerField(db_column='monto_total')
    estado = models.CharField(db_column='estado', max_length=10, choices=[('EMITIDA', 'Emitida'), ('APLICADA', 'Aplicada'), ('ANULADA', 'Anulada')], default='EMITIDA')
    
    class Meta(ManagedModel.Meta):
        db_table = 'notas_credito_cliente'


class DetalleNota(ManagedModel):
    id_detalle_nota = models.BigAutoField(db_column='id_detalle_nota', primary_key=True)
    id_nota = models.ForeignKey(NotasCreditoCliente, on_delete=models.CASCADE, db_column='id_nota', related_name='detalles')
    id_producto = models.ForeignKey('Producto', on_delete=models.PROTECT, db_column='id_producto')
    cantidad = models.DecimalField(db_column='cantidad', max_digits=10, decimal_places=3)
    precio_unitario = models.BigIntegerField(db_column='precio_unitario')
    subtotal = models.BigIntegerField(db_column='subtotal')
    
    class Meta(ManagedModel.Meta):
        db_table = 'detalle_nota'


class AutorizacionSaldoNegativo(ManagedModel):
    id_autorizacion = models.BigAutoField(db_column='id_autorizacion', primary_key=True)
    id_cliente = models.ForeignKey('Cliente', on_delete=models.PROTECT, db_column='id_cliente')
    id_venta = models.ForeignKey('pos.Venta', on_delete=models.PROTECT, db_column='id_venta')
    id_empleado_autoriza = models.ForeignKey('Empleado', on_delete=models.PROTECT, db_column='id_empleado_autoriza')
    monto_autorizado = models.BigIntegerField(db_column='monto_autorizado')
    saldo_anterior = models.BigIntegerField(db_column='saldo_anterior')
    saldo_resultante = models.BigIntegerField(db_column='saldo_resultante')
    motivo = models.TextField(db_column='motivo')
    fecha_autorizacion = models.DateTimeField(db_column='fecha_autorizacion')
    estado = models.CharField(db_column='estado', max_length=10, choices=[('VIGENTE', 'Vigente'), ('UTILIZADA', 'Utilizada'), ('VENCIDA', 'Vencida')], default='VIGENTE')
    
    class Meta(ManagedModel.Meta):
        db_table = 'autorizacion_saldo_negativo'
