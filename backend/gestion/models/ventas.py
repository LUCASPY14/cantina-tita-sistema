from django.db import models
from .base import ManagedModel


class AplicacionPagosVentas(ManagedModel):
    id_aplicacion = models.BigAutoField(db_column='ID_Aplicacion', primary_key=True)
    id_pago_venta = models.ForeignKey('pos.PagoVenta', on_delete=models.CASCADE, db_column='ID_Pago_Venta')
    id_venta = models.ForeignKey('pos.Venta', on_delete=models.CASCADE, db_column='ID_Venta')
    monto_aplicado = models.BigIntegerField(db_column='Monto_Aplicado')
    
    class Meta(ManagedModel.Meta):
        db_table = 'aplicacion_pagos_ventas'


class DetalleComisionVenta(ManagedModel):
    id_detalle_comision = models.BigAutoField(db_column='ID_Detalle_Comision', primary_key=True)
    id_pago_venta = models.ForeignKey('pos.PagoVenta', on_delete=models.CASCADE, db_column='ID_Pago_Venta')
    id_tarifa = models.ForeignKey('TarifasComision', on_delete=models.PROTECT, db_column='ID_Tarifa')
    monto_base = models.BigIntegerField(db_column='Monto_Base')
    porcentaje_aplicado = models.DecimalField(db_column='Porcentaje_Aplicado', max_digits=5, decimal_places=2)
    comision_calculada = models.BigIntegerField(db_column='Comision_Calculada')
    
    class Meta(ManagedModel.Meta):
        db_table = 'detalle_comision_venta'


class NotasCreditoCliente(ManagedModel):
    id_nota = models.BigAutoField(db_column='ID_Nota', primary_key=True)
    nro_nota_credito = models.BigIntegerField(db_column='Nro_Nota_Credito')
    id_cliente = models.ForeignKey('Cliente', on_delete=models.PROTECT, db_column='ID_Cliente')
    id_venta_origen = models.ForeignKey('pos.Venta', on_delete=models.PROTECT, db_column='ID_Venta_Origen', blank=True, null=True)
    id_empleado_autoriza = models.ForeignKey('Empleado', on_delete=models.PROTECT, db_column='ID_Empleado_Autoriza')
    fecha_emision = models.DateTimeField(db_column='Fecha_Emision')
    motivo = models.TextField(db_column='Motivo')
    monto_total = models.BigIntegerField(db_column='Monto_Total')
    estado = models.CharField(db_column='Estado', max_length=10, choices=[('EMITIDA', 'Emitida'), ('APLICADA', 'Aplicada'), ('ANULADA', 'Anulada')], default='EMITIDA')
    
    class Meta(ManagedModel.Meta):
        db_table = 'notas_credito_cliente'


class DetalleNota(ManagedModel):
    id_detalle_nota = models.BigAutoField(db_column='ID_Detalle_Nota', primary_key=True)
    id_nota = models.ForeignKey(NotasCreditoCliente, on_delete=models.CASCADE, db_column='ID_Nota', related_name='detalles')
    id_producto = models.ForeignKey('Producto', on_delete=models.PROTECT, db_column='ID_Producto')
    cantidad = models.DecimalField(db_column='Cantidad', max_digits=10, decimal_places=3)
    precio_unitario = models.BigIntegerField(db_column='Precio_Unitario')
    subtotal = models.BigIntegerField(db_column='Subtotal')
    
    class Meta(ManagedModel.Meta):
        db_table = 'detalle_nota'


class AutorizacionSaldoNegativo(ManagedModel):
    id_autorizacion = models.BigAutoField(db_column='ID_Autorizacion', primary_key=True)
    id_cliente = models.ForeignKey('Cliente', on_delete=models.PROTECT, db_column='ID_Cliente')
    id_venta = models.ForeignKey('pos.Venta', on_delete=models.PROTECT, db_column='ID_Venta')
    id_empleado_autoriza = models.ForeignKey('Empleado', on_delete=models.PROTECT, db_column='ID_Empleado_Autoriza')
    monto_autorizado = models.BigIntegerField(db_column='Monto_Autorizado')
    saldo_anterior = models.BigIntegerField(db_column='Saldo_Anterior')
    saldo_resultante = models.BigIntegerField(db_column='Saldo_Resultante')
    motivo = models.TextField(db_column='Motivo')
    fecha_autorizacion = models.DateTimeField(db_column='Fecha_Autorizacion')
    estado = models.CharField(db_column='Estado', max_length=10, choices=[('VIGENTE', 'Vigente'), ('UTILIZADA', 'Utilizada'), ('VENCIDA', 'Vencida')], default='VIGENTE')
    
    class Meta(ManagedModel.Meta):
        db_table = 'autorizacion_saldo_negativo'
